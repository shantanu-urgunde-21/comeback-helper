from pathlib import Path
from typing import List

from llama_index.core import SimpleDirectoryReader, PropertyGraphIndex, StorageContext
from llama_index.core.indices.property_graph import ImplicitPathExtractor, SimpleLLMPathExtractor
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.gemini import Gemini

from src.config import get_settings
from src.graph.schema import ALLOWED_ENTITIES, ALLOWED_RELATIONS, SCHEMA_SYSTEM_PROMPT
from src.vault.state import VaultStateTracker
from src.vault.manager import ObsidianVaultManager

class MathGraphIndexer:
    """
    Builds and updates the PropertyGraphIndex over the Obsidian Vault.
    """

    def __init__(self):
        self.settings = get_settings()
        self.vault_manager = ObsidianVaultManager(self.settings.vault_path)
        self.state_tracker = VaultStateTracker(self.settings.storage_path / "vault_state.json")
        
        # Initialize Gemini LLM using configurable model
        model_name = self.settings.gemini_model
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"

        self.llm = Gemini(
            model=model_name,
            api_key=self.settings.gemini_api_key
        )
        
        # Local BGE-M3 Embedder on CPU
        self.embed_model = HuggingFaceEmbedding(model_name=self.settings.embed_model)

    def build_or_update_index(self) -> PropertyGraphIndex:
        """
        Loads vault notes, runs incremental PropertyGraph extraction, and saves to storage.
        """
        vault_files = self.vault_manager.get_all_notes()
        modified_files = [f for f in vault_files if self.state_tracker.is_file_modified(f)]

        if not modified_files:
            print("[Indexer] Vault is up-to-date. Loading index from storage...")
            storage_context = StorageContext.from_defaults(persist_dir=str(self.settings.storage_path))
            return PropertyGraphIndex.from_existing(
                storage_context=storage_context,
                embed_model=self.embed_model,
                llm=self.llm
            )

        print(f"[Indexer] Processing {len(modified_files)} new/modified notes for PropertyGraph...")
        
        # Load modified documents
        reader = SimpleDirectoryReader(input_files=[str(f) for f in modified_files])
        documents = reader.load_data()

        # Schema-guided path extractor for math triplets
        kg_extractor = SimpleLLMPathExtractor(
            llm=self.llm,
            possible_entities=ALLOWED_ENTITIES,
            possible_relations=ALLOWED_RELATIONS,
            prompt_template=SCHEMA_SYSTEM_PROMPT,
            num_workers=2
        )

        index = PropertyGraphIndex.from_documents(
            documents,
            embed_model=self.embed_model,
            kg_extractors=[ImplicitPathExtractor(), kg_extractor],
            llm=self.llm
        )

        index.storage_context.persist(persist_dir=str(self.settings.storage_path))

        # Update state hash for processed files
        for f in modified_files:
            self.state_tracker.update_file_hash(f)
        self.state_tracker.save_state()

        print("[Indexer] Index successfully updated and persisted to storage.")
        return index
