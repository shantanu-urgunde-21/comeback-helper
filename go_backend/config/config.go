package config

import (
	"os"
	"path/filepath"
	"sync"

	"github.com/joho/godotenv"
)

type Config struct {
	GeminiAPIKey          string
	GeminiModel           string
	OCRProvider           string
	ObsidianVaultLocation string
	StorageDir            string
}

var (
	cfg  *Config
	once sync.Once
)

func LoadConfig() *Config {
	once.Do(func() {
		_ = godotenv.Load("../.env")
		_ = godotenv.Load(".env")

		vaultLoc := os.Getenv("OBSIDIAN_VAULT_LOCATION")
		if vaultLoc == "" {
			vaultLoc = os.Getenv("OBSIDIAN_VAULT_PATH")
		}
		if vaultLoc == "" {
			vaultLoc = "../.storage/vault"
		}

		model := os.Getenv("GEMINI_MODEL")
		if model == "" {
			model = "gemini-flash-latest"
		}

		provider := os.Getenv("OCR_PROVIDER")
		if provider == "" {
			provider = "gemini"
		}

		storage := os.Getenv("STORAGE_DIR")
		if storage == "" || storage == "./.storage" {
			storage = "../.storage"
		}

		absVault, _ := filepath.Abs(vaultLoc)
		absStorage, _ := filepath.Abs(storage)

		cfg = &Config{
			GeminiAPIKey:          os.Getenv("GEMINI_API_KEY"),
			GeminiModel:           model,
			OCRProvider:           provider,
			ObsidianVaultLocation: absVault,
			StorageDir:            absStorage,
		}
	})
	return cfg
}
