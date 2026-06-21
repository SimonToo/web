import os
import json
import sys
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx


if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

try:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)
except Exception as e:
    print(f"Error: cannot read config.json: {e}")
    print("Make sure config.json exists next to this executable.")
    sys.exit(1)

API_KEY = config.get("api_key", "")
PORT = config.get("port", 8000)

if not API_KEY:
    print("Error: api_key is empty in config.json")
    sys.exit(1)

UNLIMITED_BASE = "https://unlimited.surf"

client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global client
    client = httpx.AsyncClient(timeout=120.0)
    yield
    await client.aclose()


app = FastAPI(title="Unlimited Proxy", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list
    stream: bool = False
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    last_content = ""
    for msg in reversed(req.messages):
        if msg.get("role") == "user" and msg.get("content"):
            last_content = msg["content"]
            break
    if not last_content:
        raise HTTPException(400, "No user message found")

    payload = {"message": last_content, "model": req.model}
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    if req.stream:
        return StreamingResponse(
            _stream_chat(payload, headers, req.model),
            media_type="text/event-stream",
        )

    return await _non_stream_chat(payload, headers, req.model)


async def _stream_chat(payload: dict, headers: dict, model: str):
    async with client.stream(
        "POST", f"{UNLIMITED_BASE}/api/chat", json=payload, headers=headers
    ) as resp:
        if resp.status_code != 200:
            body = await resp.aread()
            yield f"data: {json.dumps({'error': body.decode(errors='replace')})}\n\n"
            return

        sent_role = False
        async for line in resp.aiter_lines():
            line = line.strip()
            if not line.startswith("data: "):
                continue
            raw = line[6:]
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if "delta" in data:
                if not sent_role:
                    yield f"data: {json.dumps({'choices': [{'delta': {'role': 'assistant'}, 'index': 0}]})}\n\n"
                    sent_role = True
                yield f"data: {json.dumps({'choices': [{'delta': {'content': data['delta']}, 'index': 0}]})}\n\n"
            elif "finish" in data:
                reason = data.get("reason", "stop")
                yield f"data: {json.dumps({'choices': [{'delta': {}, 'finish_reason': reason, 'index': 0}]})}\n\n"
            elif "done" in data:
                yield "data: [DONE]\n\n"


async def _non_stream_chat(payload: dict, headers: dict, model: str):
    content = ""
    finish_reason = "stop"

    async with client.stream(
        "POST", f"{UNLIMITED_BASE}/api/chat", json=payload, headers=headers
    ) as resp:
        if resp.status_code != 200:
            body = await resp.aread()
            raise HTTPException(resp.status_code, body.decode(errors="replace"))

        async for line in resp.aiter_lines():
            line = line.strip()
            if not line.startswith("data: "):
                continue
            raw = line[6:]
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if "delta" in data:
                content += data["delta"]
            elif "finish" in data:
                finish_reason = data.get("reason", "stop")

    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": finish_reason,
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


@app.get("/v1/models")
async def list_models():
    resp = await client.get(f"{UNLIMITED_BASE}/v1/models")
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Failed to fetch models")
    data = resp.json()
    data["object"] = "list"
    for item in data.get("data", []):
        item["object"] = "model"
    return data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
