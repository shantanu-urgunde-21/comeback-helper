package main

import (
	"fmt"
	"log"
	"net/http"

	"comeback-helper/server"
)

func main() {
	srv := server.NewServer()
	mux := http.NewServeMux()
	srv.RegisterRoutes(mux)

	port := ":8080"
	fmt.Printf("🚀 Comeback Helper Go Backend starting on http://127.0.0.1%s\n", port)
	if err := http.ListenAndServe(port, mux); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
