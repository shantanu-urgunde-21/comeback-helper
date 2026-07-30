import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, AliasChoices

class Settings(BaseSettings):
    gemini_api_key: str = Field(
        ...,
        validation_alias=AliasChoices("GEMINI_API_KEY", "gemini_api_key")
    )
    obsidian_vault_location: str = Field(
        ...,
        validation_alias=AliasChoices(
            "OBSIDIAN_VAULT_LOCATION",
            "OBSIDIAN_VAULT_PATH",
            "obsidian_vault_location"
        )
    )
    embed_model: str = Field(
        default="BAAI/bge-m3",
        validation_alias=AliasChoices("EMBED_MODEL", "embed_model")
    )
    storage_dir: str = Field(
        default="./.storage",
        validation_alias=AliasChoices("STORAGE_DIR", "storage_dir")
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def vault_path(self) -> Path:
        return Path(self.obsidian_vault_location).resolve()

    @property
    def storage_path(self) -> Path:
        p = Path(self.storage_dir).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p


_settings: Settings | None = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
