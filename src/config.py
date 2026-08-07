from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, AliasChoices


class Settings(BaseSettings):
    gemini_api_key: str = Field(
        ..., validation_alias=AliasChoices("GEMINI_API_KEY", "gemini_api_key")
    )
    obsidian_vault_location: str = Field(
        ...,
        validation_alias=AliasChoices(
            "OBSIDIAN_VAULT_LOCATION",
            "OBSIDIAN_VAULT_PATH",
            "obsidian_vault_location",
        ),
    )
    ocr_provider: str = Field(
        default="gemini", validation_alias=AliasChoices("OCR_PROVIDER", "ocr_provider")
    )
    gemini_model: str = Field(
        default="gemini-flash-latest",
        validation_alias=AliasChoices("GEMINI_MODEL", "gemini_model"),
    )
    embed_model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        validation_alias=AliasChoices("EMBED_MODEL", "embed_model"),
    )
    storage_dir: str = Field(
        default="./.storage",
        validation_alias=AliasChoices("STORAGE_DIR", "storage_dir"),
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def vault_path(self) -> Path:
        return Path(self.obsidian_vault_location).resolve()

    @property
    def storage_path(self) -> Path:
        p = Path(self.storage_dir).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p


@lru_cache()
def get_settings() -> Settings:
    return Settings()

