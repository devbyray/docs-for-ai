# MarkItDown

> Convert any file to Markdown — with a web UI, a REST API, and an MCP server for AI assistants.

Built on top of Microsoft's [markitdown](https://github.com/microsoft/markitdown) library.

---

## What's inside

| Package | Description |
|---|---|
| [`api/`](./api) | FastAPI service — accepts file uploads, returns Markdown |
| [`frontend/`](./frontend) | Nuxt 3 web UI — drag-and-drop converter with live output |
| [`mcp/`](./mcp) | MCP server — exposes conversion tools to AI assistants (Claude Desktop, VS Code, etc.) |

## Supported formats

PDF · Word (DOCX) · PowerPoint (PPTX) · Excel (XLSX / XLS) · Images (JPEG, PNG, …) · Audio (WAV, MP3) · HTML · CSV · JSON · XML · EPUB · ZIP · YouTube URLs · and more

---

## Quick start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/)

### Run everything

```bash
git clone https://github.com/YOUR_USERNAME/docs-for-ai.git
cd docs-for-ai

# API + Frontend
docker compose --profile frontend up --build -d
```

| Service | URL |
|---|---|
| Web UI | http://localhost:4000 |
| REST API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs (or http://localhost:4000/docs when frontend is running) |

### API only (no frontend)

```bash
docker compose up --build -d
```

The API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### All services including MCP

```bash
docker compose --profile frontend --profile mcp up --build -d
```

---

## Docker Compose profiles

| Profile flag | Services started |
|---|---|
| _(none)_ | `api` only |
| `--profile frontend` | `api` + `frontend` |
| `--profile mcp` | adds `mcp` (run on-demand via stdin/stdout) |

```bash
# Stop everything
docker compose --profile frontend --profile mcp down
```

---

## Project structure

```
docs-for-ai/
├── docker-compose.yml
├── api/                  # FastAPI backend
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── frontend/             # Nuxt 3 frontend
│   ├── Dockerfile
│   ├── nuxt.config.ts
│   └── app/
│       └── app.vue
└── mcp/                  # MCP server
    ├── Dockerfile
    ├── server.py
    ├── requirements.txt
    └── claude_desktop_config.example.json
```

---

## Development

Each package can be run independently. See the README in each subfolder for local dev instructions.

- [API →](./api/README.md)
- [Frontend →](./frontend/README.md)
- [MCP server →](./mcp/README.md)

---

## License

MIT
