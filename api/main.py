import ipaddress
import logging
import os
import socket
import tempfile
from typing import Optional

from fastapi import Depends, FastAPI, File, HTTPException, Request, Security, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from markitdown import MarkItDown
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("markitdown-api")

# ── Config ────────────────────────────────────────────────────────────────────
MAX_FILE_SIZE  = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024
RATE_LIMIT     = os.getenv("RATE_LIMIT", "20/minute")
API_KEY        = os.getenv("API_KEY", "").strip()
CORS_ORIGINS   = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
DOCS_ENABLED   = os.getenv("DOCS_ENABLED", "true").lower() == "true"

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls",
    ".html", ".htm", ".csv", ".json", ".xml", ".epub",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff",
    ".wav", ".mp3", ".mp4", ".zip", ".txt", ".md", ".rst",
}

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="MarkItDown API",
    version="1.0.0",
    docs_url="/docs" if DOCS_ENABLED else None,
    redoc_url="/redoc" if DOCS_ENABLED else None,
    openapi_url="/openapi.json" if DOCS_ENABLED else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)

# ── Auth ──────────────────────────────────────────────────────────────────────
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(key: Optional[str] = Security(api_key_header)):
    if not API_KEY:
        return  # auth disabled
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# ── Converter ─────────────────────────────────────────────────────────────────
md = MarkItDown(enable_plugins=False)


# ── Routes ────────────────────────────────────────────────────────────────────
@app.post("/v1/convert")
@limiter.limit(RATE_LIMIT)
async def convert(
    request: Request,
    file: UploadFile = File(...),
    _: None = Depends(verify_api_key),
):
    # A02 / A10 — extension allowlist
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext}'. "
                   f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # A04 — size limit (read in chunks to avoid loading everything at once)
    chunks = []
    total = 0
    while chunk := await file.read(1024 * 256):  # 256 KB chunks
        total += len(chunk)
        if total > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)} MB",
            )
        chunks.append(chunk)
    content = b"".join(chunks)

    tmp_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        result = md.convert(tmp_path)
        return {"filename": file.filename, "markdown": result.text_content}

    except HTTPException:
        raise
    except Exception:
        # A03 — never leak internal error details to the caller
        logger.exception("Conversion failed for file '%s'", file.filename)
        raise HTTPException(status_code=500, detail="Conversion failed")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.get("/health")
async def health():
    return {"status": "ok"}
