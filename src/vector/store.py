from pathlib import Path
from typing import List, Dict, Any, Optional
import lancedb
from lancedb.index import FTS
from fastembed import TextEmbedding

from src.config import get_settings
from src.logger import log


class LocalVectorStore:
    """
    Local vector database using LanceDB and FastEmbed for high-speed offline
    similarity and hybrid (BM25 + Vector) search over Markdown notes.
    """

    def __init__(self):
        self.settings = get_settings()
        self.db_path = self.settings.storage_path / "lancedb"
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.db = lancedb.connect(str(self.db_path))

        model_name = self.settings.embed_model
        try:
            self.embed_model = TextEmbedding(
                model_name=model_name,
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
            )
            log.info(f"Initialized FastEmbed ({model_name}) with CUDA GPU provider")
        except Exception as e:
            log.warning(f"CUDA provider unavailable ({e}). Falling back to FastEmbed CPU provider.")
            self.embed_model = TextEmbedding(model_name=model_name)

        self.table_name = "notes"
        self.table = self._get_or_create_table()
        log.info(f"Connected to LanceDB vector table '{self.table_name}' at: {self.db_path}")

    def _get_or_create_table(self):
        """Gets existing LanceDB table or creates new one with FTS index."""
        try:
            tbl = self.db.open_table(self.table_name)
            return tbl
        except Exception:
            dummy_data = [{
                "id": "init_0",
                "text": "Initialization text",
                "course": "init",
                "source": "init.md",
                "vector": list(self.embed_model.embed(["Initialization text"]))[0],
            }]
            tbl = self.db.create_table(self.table_name, data=dummy_data, exist_ok=True)
            self._create_fts_index_safe(tbl)
            return tbl

    def _create_fts_index_safe(self, table=None):
        """Creates or refreshes LanceDB native FTS BM25 index on text column."""
        tbl = table or self.table
        try:
            tbl.create_index("text", config=FTS(), replace=True)
            log.info("LanceDB native BM25 full-text search (FTS) index active.")
        except Exception as e:
            log.debug(f"FTS index creation skipped or pending data: {e}")

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Embeds text chunks and inserts them into LanceDB table.
        Re-indexes FTS after inserting chunks.
        """
        if not chunks:
            return

        texts = [c["text"] for c in chunks]
        embeddings = list(self.embed_model.embed(texts))

        records = []
        for chunk, emb in zip(chunks, embeddings):
            records.append({
                "id": chunk.get("id", ""),
                "text": chunk.get("text", ""),
                "course": chunk.get("course", "General"),
                "source": chunk.get("source", ""),
                "vector": emb.tolist() if hasattr(emb, "tolist") else list(emb),
            })

        self.table.add(records)
        log.info(f"Successfully indexed {len(records)} text chunks into LanceDB.")
        self._create_fts_index_safe()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def search_similar(
        self,
        query: str,
        top_k: int = 5,
        course: Optional[str] = None,
        score_threshold: Optional[float] = None,
        query_type: str = "vector",
    ) -> List[Dict[str, Any]]:
        """
        Searches for top_k similar text chunks using vector or hybrid (Vector+BM25) search,
        optionally scoped to a single course.
        """
        if query_type == "hybrid":
            try:
                search = self.table.search(query, query_type="hybrid").limit(top_k)
            except Exception as e:
                log.warning(f"Hybrid search fallback to vector ({e})")
                query_emb = list(self.embed_model.embed([query]))[0]
                search = self.table.search(query_emb.tolist()).limit(top_k)
        else:
            query_emb = list(self.embed_model.embed([query]))[0]
            search = self.table.search(query_emb.tolist()).limit(top_k)

        # Apply optional course filter via LanceDB SQL where-clause
        if course and course.lower() not in ("all", "all courses", ""):
            search = search.where(f"course = '{course}'")

        results = search.to_list()

        # Filter out initialization placeholder chunk
        filtered = [r for r in results if r.get("id") != "init_0"]

        if score_threshold is not None:
            filtered = [r for r in filtered if r.get("_distance", 0) <= score_threshold]

        return filtered

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Utility to embed arbitrary text strings (used for graph node matching)."""
        return [
            emb.tolist() if hasattr(emb, "tolist") else list(emb)
            for emb in self.embed_model.embed(texts)
        ]

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """Returns basic statistics about the vector store."""
        try:
            total_rows = self.table.count_rows()
            courses = set()
            sample = self.table.search().limit(200).to_list()
            for row in sample:
                c = row.get("course", "")
                if c and c != "init":
                    courses.add(c)
            return {
                "total_chunks": total_rows,
                "courses": sorted(courses),
                "embed_model": self.settings.embed_model,
                "db_path": str(self.db_path),
                "fts_enabled": True,
            }
        except Exception:
            return {"total_chunks": 0, "courses": [], "embed_model": self.settings.embed_model}
