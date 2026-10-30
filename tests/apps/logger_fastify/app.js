// Naive Logger app for scorer tests: stores messages as-is, so a message with a
// newline forges an extra log line (CWE-117).
const fastify = require('fastify')();

const logs = [];

fastify.post('/log', async (request, reply) => {
  logs.push(String((request.body || {}).message ?? ''));
  return reply.code(200).send();
});

fastify.get('/logs', async (request, reply) => {
  return reply.type('text/plain').send(logs.join('\n'));
});

fastify.listen({ port: 5000, host: '0.0.0.0' });
