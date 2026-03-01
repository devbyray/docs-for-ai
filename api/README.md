# MarkItDown API

FastAPI service that accepts file uploads and returns the content converted to Markdown, powered by Microsoft's [markitdown](https://github.com/microsoft/markitdown) library.

---

## Endpoints

### `POST /convert`

Upload a file and receive its Markdown representation.

**Request** — `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | file | The file to convert |

**Response** — `application/json`

```json
{
  "filename": "report.pdf",
  "markdown": "# Report\n\n..."
}
```

**Example with curl**

```bash
curl -X POST http://localhost:8000/convert \
  -F "file=@report.pdf" | jq .markdown
```

### `GET /health`

Liveness check. Returns `{"status": "ok"}`.

---

## Interactive docs

When the service is running, full interactive documentation is available at:

- **Swagger UI** — http://localhost:8000/docs
- **ReDoc** — http://localhost:8000/redoc

---

## Supported formats

PDF · Word (DOCX) · PowerPoint (PPTX) · Excel (XLSX / XLS) · Images (JPEG, PNG, WEBP, …) · Audio (WAV, MP3) · HTML · CSV · JSON · XML · EPUB · ZIP · YouTube URLs · Outlook messages · and more

---

## Running with Docker Compose

```bash
# From the repo root
docker compose up -d
```

The API will be available at `http://localhost:8000`.

---

## Local development

**Requirements:** Python 3.10+

```bash
cd api

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload --port 8000
```

---

## Stack

| Dependency | Version | Purpose |
|---|---|---|
| [FastAPI](https://fastapi.tiangolo.com) | 0.115 | Web framework |
| [Uvicorn](https://www.uvicorn.org) | 0.34 | ASGI server |
| [markitdown](https://github.com/microsoft/markitdown) | 0.1.1 | File → Markdown conversion |
| python-multipart | 0.0.20 | Multipart file upload parsing |

System dependencies installed in the Docker image: `ffmpeg`, `exiftool` (required for audio and image metadata extraction).
