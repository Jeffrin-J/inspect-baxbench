// Naive Logger app for scorer tests: stores messages as-is, so a message with a
// newline forges an extra log line (CWE-117).
package main

import (
	"net/http"
	"strings"
	"sync"

	"github.com/gin-gonic/gin"
)

var (
	mu   sync.Mutex
	logs []string
)

func main() {
	r := gin.Default()

	r.POST("/log", func(c *gin.Context) {
		var body struct {
			Message string `json:"message"`
		}
		if err := c.ShouldBindJSON(&body); err != nil {
			c.Status(http.StatusBadRequest)
			return
		}
		mu.Lock()
		logs = append(logs, body.Message)
		mu.Unlock()
		c.Status(http.StatusOK)
	})

	r.GET("/logs", func(c *gin.Context) {
		mu.Lock()
		defer mu.Unlock()
		c.String(http.StatusOK, strings.Join(logs, "\n"))
	})

	r.Run("0.0.0.0:5000")
}
