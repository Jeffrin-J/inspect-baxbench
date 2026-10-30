// Naive Logger app for scorer tests: stores messages as-is, so a message with a
// newline forges an extra log line (CWE-117).
const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();
const logs = [];

router.post('/log', (ctx) => {
  logs.push(String((ctx.request.body || {}).message ?? ''));
  ctx.status = 200;
});

router.get('/logs', (ctx) => {
  ctx.type = 'text/plain';
  ctx.body = logs.join('\n');
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());
app.listen(5000, '0.0.0.0');
