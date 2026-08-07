package vault

import (
	"fmt"
	"regexp"
	"strings"
)

type Chunk struct {
	ID     string `json:"id"`
	Text   string `json:"text"`
	Course string `json:"course"`
	Source string `json:"source"`
}

var (
	pageMarkerRegex = regexp.MustCompile(`(?i)<!--\s*Page\s+\d+\s*-->`)
	headingRegex    = regexp.MustCompile(`(?m)^(#{1,3}\s+.+)$`)
)

// ChunkMathMarkdown splits Markdown+LaTeX content into math-aware chunks
func ChunkMathMarkdown(content, course, sourceName string, maxChunkSize, overlapChars int) []Chunk {
	if strings.TrimSpace(content) == "" {
		return nil
	}

	pageBlocks := pageMarkerRegex.Split(content, -1)
	var sections []string

	for _, block := range pageBlocks {
		trimmed := strings.TrimSpace(block)
		if trimmed == "" {
			continue
		}
		parts := headingRegex.Split(trimmed, -1)
		for _, part := range parts {
			t := strings.TrimSpace(part)
			if t != "" {
				sections = append(sections, t)
			}
		}
	}

	if len(sections) == 0 {
		sections = []string{strings.TrimSpace(content)}
	}

	var chunks []Chunk
	for i, text := range sections {
		if len(text) < 20 {
			continue
		}

		chunkText := text
		if i > 0 && overlapChars > 0 && len(sections[i-1]) >= overlapChars {
			prevTail := sections[i-1][len(sections[i-1])-overlapChars:]
			chunkText = "..." + prevTail + "\n\n" + text
		}

		chunkID := fmt.Sprintf("%s_%d", strings.TrimSuffix(sourceName, ".md"), i)
		chunks = append(chunks, Chunk{
			ID:     chunkID,
			Text:   chunkText,
			Course: course,
			Source: sourceName,
		})
	}

	return chunks
}
