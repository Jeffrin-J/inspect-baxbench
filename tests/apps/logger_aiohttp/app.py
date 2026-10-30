# Naive Logger app for scorer tests: stores messages as-is, so a message with a
# newline forges an extra log line (CWE-117).
from aiohttp import web

logs: list[str] = []


async def log(request: web.Request) -> web.Response:
    body = await request.json()
    logs.append(str(body.get("message", "")))
    return web.Response(status=200)


async def get_logs(request: web.Request) -> web.Response:
    return web.Response(text="\n".join(logs), content_type="text/plain")


app = web.Application()
app.add_routes([web.post("/log", log), web.get("/logs", get_logs)])

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)
