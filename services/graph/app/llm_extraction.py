"""Tier 1/2 extraction: the two LLM passes, each degrading Gemini -> Ollama
via `shared.llm.fallback.with_gemini_then_ollama`. Tier 3 (no LLM at all) is
`block_extractor.block_extraction`.

Pass 1 (`extract_nodes_pass`) extracts concept nodes from one chunk of text.
Pass 2 (`extract_edges_pass`) links relationships between already-resolved
node ids, once per document — see indexer.py's `index_note` for how the two
are sequenced.
"""

import json
from typing import List

from google.genai import types

from shared.llm.fallback import with_gemini_then_ollama
from shared.llm.ollama import get_ollama_client
from shared.logger import log
from .prompts import PASS1_NODE_PROMPT, PASS2_EDGE_PROMPT
from .schema import GraphEdge, GraphNode, MathEdgeExtraction, MathNodeExtraction


def extract_nodes_pass(text: str, course_domain: str) -> tuple[List[GraphNode], str]:
    """Executes Pass 1 (Node & Taxonomy Extraction) via Gemini or Ollama.

    Returns (nodes, method) — method is "gemini" or "ollama" on success,
    "none" if every tier failed or was unavailable (index_note's caller
    then falls back to the block parser and re-tags the chunk
    "block_parser"). See graph_store.EXTRACTION_METHODS.
    """

    def try_gemini(client, model_name: str) -> List[GraphNode]:
        prompt = PASS1_NODE_PROMPT.format(text=text)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MathNodeExtraction,
                temperature=0.1,
            ),
        )
        data = json.loads(response.text)
        nodes = MathNodeExtraction(**data).nodes
        log.info(f"Pass 1 (Gemini {model_name}): Extracted {len(nodes)} concept nodes.")
        return nodes

    def try_ollama(model: str) -> "List[GraphNode] | None":
        ollama = get_ollama_client()
        prompt = PASS1_NODE_PROMPT.format(text=text[:3000])
        prompt += (
            "\n\nRespond ONLY with valid JSON matching:\n"
            '{"nodes": [{"name": "Concept Name", "kind": "Object|Statement|Definition|Method|Formula|Proof|Example", '
            '"role": "Theorem|Lemma|Corollary|Axiom|Proposition|Conjecture or omit", '
            '"description": "formal definition", "taxonomy": {"domain": "...", "subdomain": "...", "topic": "..."}}]}'
        )
        resp = ollama.chat(prompt=prompt, model=model, response_format="json", timeout=60)
        if not resp:
            return None
        try:
            data = json.loads(resp)
            nodes = MathNodeExtraction(**data).nodes
            log.info(f"Pass 1 (Ollama {model}): Extracted {len(nodes)} concept nodes.")
            return nodes
        except Exception:
            return None

    result, method = with_gemini_then_ollama(try_gemini, try_ollama)
    return (result if result is not None else []), method


def extract_edges_pass(
    text: str,
    doc_concept_map: dict[str, str],       # surface name -> canonical_id (this document)
    existing_concept_map: dict[str, str],   # canonical_id -> label (existing graph)
    node_types: "dict[str, dict]",          # canonical_id -> {"kind":..., "role":...}
) -> "tuple[list[GraphEdge], str]":
    """Executes Pass 2 (Relationship & Edge Linker) via Gemini or Ollama.

    `node_types` is what lets the LLM pick type-appropriate relations —
    without it, Pass 2 was type-blind and emitted USES_LEMMA at theorems
    and PROVES at definitions (docs/vocabulary-diagnosis.md V3).

    Returns (edges, method) — see `extract_nodes_pass` for the method tag.
    """
    if not doc_concept_map:
        return [], "none"

    # Build the id->name view the prompt exposes to the LLM
    id_to_name: dict[str, str] = {v: k for k, v in doc_concept_map.items()}
    id_to_name.update(existing_concept_map)

    entity_dict = {
        cid: {
            "name": name,
            "kind": node_types.get(cid, {}).get("kind", "Object"),
            "role": node_types.get(cid, {}).get("role"),
        }
        for cid, name in id_to_name.items()
    }

    concept_id_map_json = json.dumps(entity_dict, ensure_ascii=False)
    new_concept_ids_json = json.dumps(list(doc_concept_map.values()))
    existing_concept_ids_json = json.dumps(list(existing_concept_map.keys()))

    def try_gemini(client, model_name: str) -> List[GraphEdge]:
        prompt = PASS2_EDGE_PROMPT.format(
            concept_id_map=concept_id_map_json,
            new_concept_ids=new_concept_ids_json,
            existing_concept_ids=existing_concept_ids_json,
            text=text,
        )
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MathEdgeExtraction,
                temperature=0.1,
            ),
        )
        data = json.loads(response.text)
        edges = MathEdgeExtraction(**data).edges
        log.info(f"Pass 2 (Gemini {model_name}): Linked {len(edges)} relationship edges.")
        return edges

    def try_ollama(model: str) -> "List[GraphEdge] | None":
        ollama = get_ollama_client()
        prompt = PASS2_EDGE_PROMPT.format(
            concept_id_map=concept_id_map_json,
            new_concept_ids=new_concept_ids_json,
            existing_concept_ids=existing_concept_ids_json,
            text=text[:3000],
        )
        prompt += (
            "\n\nRespond ONLY with valid JSON matching:\n"
            '{"edges": [{"source": "id", "target": "id", "relation": "DEPENDS_ON|HAS_HYPOTHESIS|USES_DEFINITION|USES_IN_PROOF|PROVES|COROLLARY_OF|GENERALIZES|SPECIAL_CASE_OF|EQUIVALENT_TO|CHARACTERIZES|INSTANCE_OF", "description": "evidence quote"}]}'
        )
        resp = ollama.chat(prompt=prompt, model=model, response_format="json", timeout=60)
        if not resp:
            return None
        try:
            data = json.loads(resp)
            edges = MathEdgeExtraction(**data).edges
            log.info(f"Pass 2 (Ollama {model}): Linked {len(edges)} relationship edges.")
            return edges
        except Exception:
            return None

    result, method = with_gemini_then_ollama(try_gemini, try_ollama)
    return (result if result is not None else []), method
