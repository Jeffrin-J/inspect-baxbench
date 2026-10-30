// Naive Logger app for scorer tests: stores messages as-is, so a message with a
// newline forges an extra log line (CWE-117).
package main

import (
	"encoding/json"
	"net/http"
	"strings"
	"sync"
)

var (
	mu   sync.Mutex
	logs []string
)

func main() {
	http.HandleFunc("/log", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}
		var body struct {
			Message string `json:"message"`
		}
		if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		mu.Lock()
		logs = append(logs, body.Message)
		mu.Unlock()
		w.WriteHeader(http.StatusOK)
	})
	http.HandleFunc("/logs", func(w http.ResponseWriter, r *http.Request) {
		mu.Lock()
		defer mu.Unlock()
		w.Header().Set("Content-Type", "text/plain")
		w.Write([]byte(strings.Join(logs, "\n")))
	})
	http.ListenAndServe("0.0.0.0:5000", nil)
}
