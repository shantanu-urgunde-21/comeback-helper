package vault

import (
	"crypto/sha256"
	"encoding/hex"
	"io"
	"os"
	"path/filepath"
	"sync"
)

type NoteFile struct {
	Path    string `json:"path"`
	Title   string `json:"title"`
	Course  string `json:"course"`
	Hash    string `json:"hash"`
	Content string `json:"content,omitempty"`
}

// ScanVault scans all .md notes concurrently using goroutines
func ScanVault(rootPath string) ([]NoteFile, error) {
	var notes []NoteFile
	var mu sync.Mutex
	var wg sync.WaitGroup

	absRoot, err := filepath.Abs(rootPath)
	if err != nil {
		return nil, err
	}

	err = filepath.WalkDir(absRoot, func(path string, d os.DirEntry, err error) error {
		if err != nil || d.IsDir() || filepath.Ext(path) != ".md" {
			return nil
		}

		wg.Add(1)
		go func(p string) {
			defer wg.Done()
			hash, content, err := ReadAndHashFile(p)
			if err != nil {
				return
			}

			rel, _ := filepath.Rel(absRoot, p)
			course := "General"
			dir := filepath.Dir(rel)
			if dir != "." && dir != "" {
				course = filepath.Base(dir)
			}

			title := filepath.Base(p)
			title = title[:len(title)-len(filepath.Ext(title))]

			note := NoteFile{
				Path:    p,
				Title:   title,
				Course:  course,
				Hash:    hash,
				Content: content,
			}

			mu.Lock()
			notes = append(notes, note)
			mu.Unlock()
		}(path)

		return nil
	})

	wg.Wait()
	return notes, err
}

func ReadAndHashFile(path string) (string, string, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", "", err
	}
	defer f.Close()

	contentBytes, err := io.ReadAll(f)
	if err != nil {
		return "", "", err
	}

	h := sha256.New()
	h.Write(contentBytes)
	hashStr := hex.EncodeToString(h.Sum(nil))

	return hashStr, string(contentBytes), nil
}
