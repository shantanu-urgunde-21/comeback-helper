from pathlib import Path
from typing import List, Dict, Any
import lancedb
from fastembed import TextEmbedding

from src.config import get_settings
from src.logger import log

class LocalVectorStore:
    """
    Local vector database using LanceDB and FastEmbed for high-speed offline similarity search over Markdown notes.
    Accelerated with CUDA GPU execution provider.
    """

    def __init__(self):
        self.settings = get_settings()
        self.db_path = self.settings.storage_path / "lancedb"
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.db = lancedb.connect(str(self.db_path))
        # Enable CUDA GPU execution provider for FastEmbed
        try:
            self.embed_model = TextEmbedding(
                model_name="BAAI/bge-small-en-v1.5",
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
            )
            log.info("Initialized FastEmbed (BAAI/bge-small-en-v1.5) with CUDA GPU execution provider")
        except Exception as e:
            log.warning(f"CUDA provider unavailable ({e}). Falling back to FastEmbed CPU provider.")
            self.embed_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            
        self.table_name = "notes"
        self.table = self._get_or_create_table()
        log.info(f"Connected to LanceDB vector table '{self.table_name}' at: {self.db_path}")

    def _get_or_create_table(self):
        """
        Gets existing LanceDB table or creates new one.
        """
        try:
            return self.db.open_table(self.table_name)
        except Exception:
            dummy_data = [{
                "id": "init_0",
                "text": "Initialization text",
                "course": "init",
                "source": "init.md",
                "vector": list(self.embed_model.embed(["Initialization text"]))[0]
            }]
            return self.db.create_table(self.table_name, data=dummy_data, exist_ok=True)

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Embeds text chunks and inserts them into LanceDB table.
        Each chunk is a dict: {"id": str, "text": str, "course": str, "source": str}
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
                "vector": emb.tolist() if hasattr(emb, "tolist") else list(emb)
            })

        self.table.add(records)
        print(f"[LocalVectorStore] Successfully indexed {len(records)} text chunks into LanceDB.")

    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches for top_k semantically similar text chunks for a query string.
        """
        query_emb = list(self.embed_model.embed([query]))[0]
        results = self.table.search(query_emb.tolist()).limit(top_k).to_list()
        
        # Filter out initialization placeholder chunk if present
        filtered = [r for r in results if r.get("id") != "init_0"]
        return filtered
