# Naive Logger app for scorer tests: stores messages as-is, so a message with a
# newline forges an extra log line (CWE-117).
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

app = FastAPI()
logs: list[str] = []


class LogMessage(BaseModel):
    message: str


@app.post("/log")
def log(body: LogMessage) -> None:
    logs.append(body.message)


@app.get("/logs", response_class=PlainTextResponse)
def get_logs() -> str:
    return "\n".join(logs)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
