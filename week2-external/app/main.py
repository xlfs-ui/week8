from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PACKAGE_ROOT / "frontend"

load_dotenv(PACKAGE_ROOT / ".env")

app = FastAPI(title="DeepSeek Chat Bot", description="HTTP JSON chat proxy for DeepSeek API")


class EnsureUtf8CharsetMiddleware(BaseHTTPMiddleware):
    """Some Windows browsers guess GBK for /static/*.js|*.css when charset is missing; force UTF-8."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        ct = response.headers.get("content-type", "")
        if not ct or "charset=" in ct.lower():
            return response
        path = request.url.path
        if path.startswith("/static/") and path.endswith(".js"):
            response.headers["content-type"] = "application/javascript; charset=utf-8"
        elif path.startswith("/static/") and path.endswith(".css"):
            response.headers["content-type"] = "text/css; charset=utf-8"
        elif ct.split(";")[0].strip() == "application/json":
            response.headers["content-type"] = "application/json; charset=utf-8"
        return response


app.add_middleware(EnsureUtf8CharsetMiddleware)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    # Serve file bytes (no server-side UTF-8 decode) so mixed-encoding files cannot 500 the app.
    html_path = FRONTEND_DIR / "index.html"
    if not html_path.is_file():
        raise HTTPException(
            status_code=500,
            detail=f"Missing index.html at {html_path}. Run uvicorn from week2-external with frontend present.",
        )
    return FileResponse(html_path, media_type="text/html; charset=utf-8")


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    from .services import deepseek_chat

    try:
        reply, model = deepseek_chat.completion(
            payload.messages,
            temperature=payload.temperature,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        logger.exception("DeepSeek API error")
        raise HTTPException(status_code=502, detail="Upstream model request failed") from e
    if not reply:
        raise HTTPException(status_code=502, detail="Empty model response")
    return ChatResponse(reply=reply, model=model)


if not FRONTEND_DIR.is_dir():
    raise RuntimeError(f"Missing frontend directory: {FRONTEND_DIR}")
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
