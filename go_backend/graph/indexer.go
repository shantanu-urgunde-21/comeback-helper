package graph

import (
	"encoding/json"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"sync"
)

var (
	headingExtractRegex = regexp.MustCompile(`(?m)^(#{1,3})\s+(?:(Theorem|Definition|Concept|Lemma|Proof|Formula|Example|Axiom|Corollary):\s*)?(.+)$`)
	wikilinkRegex       = regexp.MustCompile(`\[\[(.*?)\]\]`)
)

type GraphData struct {
	Nodes []GraphNode `json:"nodes"`
	Edges []GraphEdge `json:"edges"`
}

type MathGraphIndexer struct {
	StoragePath string
	GraphFile   string
	Nodes       map[string]GraphNode
	Edges       []GraphEdge
	mu          sync.RWMutex
}

func NewMathGraphIndexer(storagePath string) *MathGraphIndexer {
	indexer := &MathGraphIndexer{
		StoragePath: storagePath,
		GraphFile:   filepath.Join(storagePath, "graph.json"),
		Nodes:       make(map[string]GraphNode),
		Edges:       make([]GraphEdge, 0),
	}
	indexer.LoadGraph()
	return indexer
}

func (idx *MathGraphIndexer) LoadGraph() {
	idx.mu.Lock()
	defer idx.mu.Unlock()

	dataBytes, err := os.ReadFile(idx.GraphFile)
	if err != nil {
		return
	}

	var data GraphData
	if err := json.Unmarshal(dataBytes, &data); err == nil {
		for _, n := range data.Nodes {
			idx.Nodes[n.Name] = n
		}
		idx.Edges = data.Edges
	}
}

func (idx *MathGraphIndexer) SaveGraph() error {
	idx.mu.RLock()
	defer idx.mu.RUnlock()

	var nodes []GraphNode
	for _, n := range idx.Nodes {
		nodes = append(nodes, n)
	}

	data := GraphData{
		Nodes: nodes,
		Edges: idx.Edges,
	}

	dataBytes, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return err
	}

	_ = os.MkdirAll(idx.StoragePath, 0755)
	return os.WriteFile(idx.GraphFile, dataBytes, 0644)
}

func (idx *MathGraphIndexer) ExtractLocal(text string) MathEntityExtraction {
	var nodes []GraphNode
	var edges []GraphEdge
	nodeNames := make(map[string]bool)

	headingMatches := headingExtractRegex.FindAllStringSubmatch(text, -1)
	for _, match := range headingMatches {
		if len(match) >= 4 {
			entityTypeStr := match[2]
			name := strings.TrimSpace(strings.TrimSuffix(match[3], ":"))
			if name != "" && !strings.HasPrefix(name, "<!--") && !nodeNames[name] {
				nodeNames[name] = true
				eType := Concept
				if entityTypeStr != "" {
					eType = MathEntityType(strings.Title(strings.ToLower(entityTypeStr)))
				}
				nodes = append(nodes, GraphNode{
					ID:          name,
					Name:        name,
					EntityType:  eType,
					Description: "Extracted from heading: " + name,
				})
			}
		}
	}

	wikilinks := wikilinkRegex.FindAllStringSubmatch(text, -1)
	for _, match := range wikilinks {
		if len(match) >= 2 {
			linkClean := strings.TrimSpace(strings.Split(match[1], "|")[0])
			if linkClean != "" && !strings.HasSuffix(linkClean, ".png") && !strings.HasSuffix(linkClean, ".jpg") {
				if !nodeNames[linkClean] {
					nodeNames[linkClean] = true
					nodes = append(nodes, GraphNode{
						ID:          linkClean,
						Name:        linkClean,
						EntityType:  Concept,
						Description: "Wikilink reference from note",
					})
				}
				if len(nodes) > 0 {
					src := nodes[0].Name
					if src != linkClean {
						edges = append(edges, GraphEdge{
							Source:   src,
							Target:   linkClean,
							Relation: DependsOn,
						})
					}
				}
			}
		}
	}

	return MathEntityExtraction{Nodes: nodes, Edges: edges}
}
