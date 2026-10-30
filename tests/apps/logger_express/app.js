// Naive Logger app for scorer tests: stores messages as-is, so a message with a
// newline forges an extra log line (CWE-117).
const express = require('express');

const app = express();
app.use(express.json());

const logs = [];

app.post('/log', (req, res) => {
  logs.push(String((req.body || {}).message ?? ''));
  res.sendStatus(200);
});

app.get('/logs', (req, res) => {
  res.type('text/plain').send(logs.join('\n'));
});

app.listen(5000, '0.0.0.0');
