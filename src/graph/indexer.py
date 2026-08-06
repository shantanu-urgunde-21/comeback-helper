import json
import os
from pathlib import Path
from typing import Dict, Any, List
import networkx as nx
from google import genai

from src.config import get_settings
from src.graph.schema import MathEntityExtraction, GraphNode, GraphEdge
from src.logger import log
from src.vault.state import VaultStateTracker
from src.vault.manager import ObsidianVaultManager

class MathGraphIndexer:
    """
    Indexes mathematical Markdown notes into a NetworkX Property Graph (.storage/graph.json).
    Uses native Google Gemini Pydantic structured output for zero-error schema extraction.
    """

    def __init__(self, storage_path: Path | None = None, vault_path: Path | None = None):
        self.settings = get_settings()
        self.storage_path = storage_path or self.settings.storage_path
        self.vault_path = vault_path or self.settings.vault_path
        
        self.graph_file = self.storage_path / "graph.json"
        self.graph = self._load_graph()
        self.state_tracker = VaultStateTracker(state_file_path=self.storage_path / "vault_state.json")
        
        self.client = None
        self._init_genai_client()

    def _init_genai_client(self):
        """
        Initializes Google GenAI client for Pydantic schema extraction.
        """
        try:
            self.client = genai.Client(api_key=self.settings.gemini_api_key)
            self.has_instructor = True
            log.info("Gemini GenAI client successfully initialized for native Pydantic graph extraction.")
        except Exception as e:
            log.warning(f"Failed to initialize GenAI client ({e}). Graph extraction disabled.")
            self.has_instructor = False

    def _load_graph(self) -> nx.DiGraph:
        """
        Loads networkx graph from .storage/graph.json if exists.
        """
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
        """
        Saves networkx graph to .storage/graph.json.
        """
        data = {
            "nodes": [
                {
                    "id": n,
                    "label": n,
                    "type": self.graph.nodes[n].get("entity_type", "Concept"),
                    "description": self.graph.nodes[n].get("description", "")
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
                    "label": d.get("relation", "DEPENDS_ON")
                }
                for u, v, d in self.graph.edges(data=True)
            ]
        }
        self.graph_file.parent.mkdir(parents=True, exist_ok=True)
        self.graph_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        log.info(f"Persisted PropertyGraph ({len(data['nodes'])} nodes, {len(data['edges'])} edges) to: {self.graph_file}")

    def extract_from_text(self, text: str) -> MathEntityExtraction:
        """
        Extracts structured nodes and edges from text chunk using native Gemini Pydantic output.
        """
        if not self.has_instructor or not self.client:
            return MathEntityExtraction(nodes=[], edges=[])

        try:
            model_name = self.settings.gemini_model.replace("models/", "")
            response = self.client.models.generate_content(
                model=model_name,
                contents=f"Extract mathematical entities and prerequisite relationships from this text:\n\n{text}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MathEntityExtraction,
                    temperature=0.1
                )
            )
            # Response text is guaranteed to match Pydantic schema
            data = json.loads(response.text)
            return MathEntityExtraction(**data)
        except Exception as e:
            log.warning(f"Math PropertyGraph extraction warning ({e})")
            return MathEntityExtraction(nodes=[], edges=[])

    def index_note(self, note_path: Path):
        """
        Indexes a single Markdown file into the NetworkX graph.
        """
        content = note_path.read_text(encoding="utf-8")
        extraction = self.extract_from_text(content)

        for node in extraction.nodes:
            self.graph.add_node(
                node.name,
                entity_type=node.entity_type.value,
                description=node.description
            )

        for edge in extraction.edges:
            self.graph.add_edge(
                edge.source,
                edge.target,
                relation=edge.relation.value
            )

    def build_or_update_index(self) -> nx.DiGraph:
        """
        Processes new or modified Markdown files in the Obsidian vault and updates graph.
        """
        notes = self.vault_manager.get_all_notes()
        modified_notes = [n for n in notes if self.state_tracker.is_file_modified(n)]

        if not modified_notes:
            print("[MathGraphIndexer] Vault graph is up-to-date.")
            return self.graph

        print(f"[MathGraphIndexer] Indexing {len(modified_notes)} new/modified notes into Graph...")
        for note in modified_notes:
            print(f"[MathGraphIndexer] Extracting schema entities from: {note.name}")
            self.index_note(note)
            self.state_tracker.update_file_hash(note)

        self.state_tracker.save_state()
        self.save_graph()
        return self.graph
