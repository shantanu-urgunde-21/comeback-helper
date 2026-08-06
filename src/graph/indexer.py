import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List
import networkx as nx
from google import genai
from google.genai import types

from src.config import get_settings
from src.graph.schema import MathEntityExtraction, GraphNode, GraphEdge
from src.logger import log
from src.vault.state import VaultStateTracker
from src.vault.manager import ObsidianVaultManager


class MathGraphIndexer:
    """
    Indexes mathematical Markdown notes into a NetworkX Property Graph (.storage/graph.json).
    Uses native Google Gemini Pydantic structured output, with automatic fallback
    to local regex + wikilink extraction if Gemini rate limits (HTTP 429) or offline.
    """

    def __init__(self, storage_path: Path | None = None, vault_path: Path | None = None):
        self.settings = get_settings()
        self.storage_path = storage_path or self.settings.storage_path
        self.vault_path = vault_path or self.settings.vault_path

        self.graph_file = self.storage_path / "graph.json"
        self.graph = self._load_graph()
        self.vault_manager = ObsidianVaultManager(self.vault_path)
        self.state_tracker = VaultStateTracker(state_file_path=self.storage_path / "vault_state.json")

        self.client = None
        self._init_genai_client()

    def _init_genai_client(self):
        """Initializes Google GenAI client for Pydantic schema extraction."""
        try:
            if self.settings.gemini_api_key and not self.settings.gemini_api_key.startswith("your_"):
                self.client = genai.Client(api_key=self.settings.gemini_api_key)
                self.has_instructor = True
                log.info("Gemini GenAI client initialized for graph schema extraction.")
            else:
                self.has_instructor = False
                log.info("No Gemini API key provided. Using local regex & wikilink graph extraction.")
        except Exception as e:
            log.warning(f"Failed to initialize GenAI client ({e}). Using local fallback extraction.")
            self.has_instructor = False

    def _load_graph(self) -> nx.DiGraph:
        """Loads NetworkX graph from .storage/graph.json if it exists."""
        G = nx.DiGraph()
        if self.graph_file.exists():
            try:
                data = json.loads(self.graph_file.read_text(encoding="utf-8"))
                for node in data.get("nodes", []):
                    G.add_node(node["id"], **node)
                for edge in data.get("edges", []):
                    G.add_edge(edge["source"], edge["target"], relation=edge.get("relation", "DEPENDS_ON"))
                log.info(f"Loaded existing Math PropertyGraph ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")
            except Exception as e:
                log.warning(f"Failed to load graph.json ({e}), initializing empty graph.")
        return G

    def save_graph(self):
        """Saves NetworkX graph to .storage/graph.json."""
        data = {
            "nodes": [
                {
                    "id": n,
                    "label": n,
                    "type": self.graph.nodes[n].get("entity_type", "Concept"),
                    "description": self.graph.nodes[n].get("description", ""),
                }
                for n in self.graph.nodes
            ],
            "edges": [
                {
                    "from": u,
                    "to": v,
                    "source": u,
                    "target": v,
                    "relation": d.get("relation", "DEPENDS_ON"),
                    "label": d.get("relation", "DEPENDS_ON"),
                }
                for u, v, d in self.graph.edges(data=True)
            ],
        }
        self.graph_file.parent.mkdir(parents=True, exist_ok=True)
        self.graph_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        log.info(f"Persisted PropertyGraph ({len(data['nodes'])} nodes, {len(data['edges'])} edges) to: {self.graph_file}")

    def _fallback_regex_extraction(self, text: str) -> MathEntityExtraction:
        """
        100% Offline, deterministic extraction parsing Markdown headers
        (# Theorem: ..., ## Definition: ...) and Obsidian [[wikilinks]].
        Zero API calls, zero rate limits.
        """
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        node_names: set[str] = set()

        # Find Markdown headings (# Theorem: Spectral Theorem, ## Definition: Symmetric Matrix)
        heading_matches = re.findall(
            r"^(#{1,3})\s+(?:(Theorem|Definition|Concept|Lemma|Proof|Formula|Example):\s*)?(.+)$",
            text,
            re.MULTILINE,
        )

        for _, entity_type, name in heading_matches:
            clean_name = name.strip().rstrip(":")
            # Ignore plain page markers
            if clean_name and not clean_name.startswith("<!--") and clean_name not in node_names:
                node_names.add(clean_name)
                etype = (entity_type or "Concept").title()
                if etype not in ["Theorem", "Definition", "Concept", "Proof", "Formula", "Lemma", "Example", "Course"]:
                    etype = "Concept"
                nodes.append(GraphNode(
                    name=clean_name,
                    entity_type=etype,
                    description=f"Extracted from vault heading: {clean_name}",
                ))

        # Find Obsidian wikilinks [[Target Concept]]
        wikilinks = re.findall(r"\[\[(.*?)\]\]", text)
        for link in wikilinks:
            link_clean = link.split("|")[0].strip()
            if link_clean and not link_clean.endswith(".png") and not link_clean.endswith(".jpg"):
                if link_clean not in node_names:
                    node_names.add(link_clean)
                    nodes.append(GraphNode(
                        name=link_clean,
                        entity_type="Concept",
                        description="Wikilink reference from vault note",
                    ))
                if nodes:
                    src = nodes[0].name
                    if src != link_clean:
                        edges.append(GraphEdge(source=src, target=link_clean, relation="DEPENDS_ON"))

        log.info(f"Local regex & wikilink graph extraction found {len(nodes)} nodes and {len(edges)} edges.")
        return MathEntityExtraction(nodes=nodes, edges=edges)

    def extract_from_text(self, text: str) -> MathEntityExtraction:
        """
        Extracts structured nodes and edges from text chunk using Gemini Pydantic output,
        with automatic fallback to local regex/wikilink extraction on HTTP 429 quota exhaustion.
        """
        if not self.has_instructor or not self.client:
            return self._fallback_regex_extraction(text)

        try:
            model_name = self.settings.gemini_model.replace("models/", "")
            response = self.client.models.generate_content(
                model=model_name,
                contents=f"Extract mathematical entities and prerequisite relationships from this text:\n\n{text}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MathEntityExtraction,
                    temperature=0.1,
                ),
            )
            data = json.loads(response.text)
            return MathEntityExtraction(**data)
        except Exception as e:
            log.warning(f"Gemini Graph Extraction API unavailable/rate-limited ({e}). Switching to local fallback parser...")
            return self._fallback_regex_extraction(text)

    def index_note(self, note_path: Path):
        """Indexes a single Markdown file into the NetworkX graph."""
        content = note_path.read_text(encoding="utf-8")

        # Include note title as primary node
        main_node = note_path.stem
        if main_node not in self.graph:
            course = note_path.parent.name if note_path.parent != self.vault_path else "General"
            self.graph.add_node(main_node, entity_type="Note", description=f"Course Note ({course})")

        extraction = self.extract_from_text(content)

        for node in extraction.nodes:
            self.graph.add_node(
                node.name,
                entity_type=node.entity_type.value if hasattr(node.entity_type, "value") else str(node.entity_type),
                description=node.description,
            )
            # Connect note to its extracted concepts
            if node.name != main_node:
                self.graph.add_edge(main_node, node.name, relation="CONTAINS")

        for edge in extraction.edges:
            self.graph.add_edge(
                edge.source,
                edge.target,
                relation=edge.relation.value if hasattr(edge.relation, "value") else str(edge.relation),
            )

    def build_or_update_index(self) -> nx.DiGraph:
        """Processes new or modified Markdown files in the vault and updates graph."""
        notes = self.vault_manager.get_all_notes()
        modified_notes = [n for n in notes if self.state_tracker.is_file_modified(n)]

        if not modified_notes:
            log.info("Vault graph is up-to-date.")
            return self.graph

        log.info(f"Indexing {len(modified_notes)} new/modified notes into Graph...")
        for note in modified_notes:
            log.info(f"Extracting schema entities from: {note.name}")
            self.index_note(note)
            self.state_tracker.update_file_hash(note)

        self.state_tracker.save_state()
        self.save_graph()
        return self.graph
