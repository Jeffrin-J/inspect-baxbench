// Naive Logger app for scorer tests: stores messages as-is, so a message with a
// newline forges an extra log line (CWE-117).
package main

import (
	"strings"
	"sync"

	"github.com/gofiber/fiber/v2"
)

var (
	mu   sync.Mutex
	logs []string
)

func main() {
	app := fiber.New()

	app.Post("/log", func(c *fiber.Ctx) error {
		var body struct {
			Message string `json:"message"`
		}
		if err := c.BodyParser(&body); err != nil {
			return c.SendStatus(fiber.StatusBadRequest)
		}
		mu.Lock()
		logs = append(logs, body.Message)
		mu.Unlock()
		return c.SendStatus(fiber.StatusOK)
	})

	app.Get("/logs", func(c *fiber.Ctx) error {
		mu.Lock()
		defer mu.Unlock()
		c.Set(fiber.HeaderContentType, fiber.MIMETextPlain)
		return c.SendString(strings.Join(logs, "\n"))
	})

	app.Listen("0.0.0.0:5000")
}
