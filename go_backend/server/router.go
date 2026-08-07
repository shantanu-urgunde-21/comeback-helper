package server

import (
	"encoding/json"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"time"

	"comeback-helper/config"
	"comeback-helper/graph"
	"comeback-helper/vault"
)

type Server struct {
	Config  *config.Config
	Indexer *graph.MathGraphIndexer
}

func NewServer() *Server {
	cfg := config.LoadConfig()
	indexer := graph.NewMathGraphIndexer(cfg.StorageDir)
	return &Server{
		Config:  cfg,
		Indexer: indexer,
	}
}

func (s *Server) RegisterRoutes(mux *http.ServeMux) {
	pyURL, _ := url.Parse("http://127.0.0.1:8000")
	pyProxy := httputil.NewSingleHostReverseProxy(pyURL)

	mux.Handle("GET /static/", http.StripPrefix("/static/", http.FileServer(http.Dir("../static"))))
	mux.HandleFunc("GET /", s.handleRoot)
	mux.HandleFunc("GET /api/vault", s.handleVault)
	mux.HandleFunc("GET /api/graph", s.handleGraph)
	mux.HandleFunc("GET /api/settings", s.handleSettings)
	mux.HandleFunc("GET /api/health/ollama", s.handleOllamaHealth)

	// Proxy heavy AI & ingestion endpoints to Python backend (port 8000)
	mux.Handle("POST /api/ingest", pyProxy)
	mux.Handle("POST /api/query", pyProxy)
	mux.Handle("POST /api/rebuild/", pyProxy)
	mux.Handle("POST /api/clear", pyProxy)
}

func (s *Server) handleRoot(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, "../static/index.html")
}

func (s *Server) handleVault(w http.ResponseWriter, r *http.Request) {
	notes, err := vault.ScanVault(s.Config.ObsidianVaultLocation)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	vaultData := make(map[string][]map[string]any)
	for _, n := range notes {
		course := n.Course
		if course == "" {
			course = "General"
		}
		vaultData[course] = append(vaultData[course], map[string]any{
			"title": n.Title,
			"path":  n.Path,
			"size":  len(n.Content),
		})
	}

	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]any{"vault": vaultData})
}

func (s *Server) handleGraph(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	
	// If graph.json exists, serve it directly
	if graphBytes, err := os.ReadFile(s.Indexer.GraphFile); err == nil && len(graphBytes) > 0 {
		w.Write(graphBytes)
		return
	}

	var nodeList []map[string]any
	for _, n := range s.Indexer.Nodes {
		nodeList = append(nodeList, map[string]any{
			"id":          n.ID,
			"label":       n.Name,
			"type":        n.EntityType,
			"taxonomy":    n.Taxonomy,
			"aliases":     n.Aliases,
			"description": n.Description,
			"provenance":  n.Provenance,
		})
	}

	var edgeList []map[string]any
	for _, e := range s.Indexer.Edges {
		edgeList = append(edgeList, map[string]any{
			"from":     e.Source,
			"to":       e.Target,
			"source":   e.Source,
			"target":   e.Target,
			"relation": e.Relation,
			"label":    e.Relation,
		})
	}

	_ = json.NewEncoder(w).Encode(map[string]any{
		"nodes": nodeList,
		"edges": edgeList,
	})
}

func (s *Server) handleSettings(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]any{
		"gemini_model": s.Config.GeminiModel,
		"ocr_provider": s.Config.OCRProvider,
		"vault_path":   s.Config.ObsidianVaultLocation,
		"storage_path": s.Config.StorageDir,
	})
}

func (s *Server) handleOllamaHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "no-store, no-cache, must-revalidate")

	client := &http.Client{Timeout: 2 * time.Second}
	resp, err := client.Get("http://127.0.0.1:11434/api/tags")

	if err != nil || resp.StatusCode != 200 {
		_ = json.NewEncoder(w).Encode(map[string]any{
			"service_online":  false,
			"target_model":    "qwen2.5vl:3b",
			"model_available": false,
			"message":         "Ollama service unreachable.",
		})
		return
	}
	defer resp.Body.Close()

	_ = json.NewEncoder(w).Encode(map[string]any{
		"service_online":  true,
		"target_model":    "qwen2.5vl:3b",
		"model_available": true,
		"message":         "Ollama Active.",
	})
}
