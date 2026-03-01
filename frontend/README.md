# MarkItDown Frontend

Nuxt 3 web interface for the MarkItDown API. Upload any file, click **Convert to Markdown**, and get the result instantly in a copyable textarea.

---

## Features

- **Drag & drop** or click-to-browse file selection
- Shows file name and size after selection
- Loading spinner during conversion
- Resizable Markdown output textarea with **Copy to clipboard**
- **API Docs** link that opens the Swagger UI
- Dark theme, no external CSS framework

---

## Running with Docker Compose

```bash
# From the repo root
docker compose --profile frontend up -d
```

The UI will be available at **http://localhost:4000**.

---

## Local development

**Requirements:** Node.js 20+

```bash
cd frontend
npm install
npm run dev
```

The dev server starts at `http://localhost:3000`.

> **Note:** For the `/api/*` proxy to work locally you need the API running at `http://localhost:8000`. Start it with `docker compose up -d` from the repo root, or run it directly — see [`api/README.md`](../api/README.md).
>
> Update `nuxt.config.ts` to proxy to `http://localhost:8000` instead of `http://api:8000` during local dev.

---

## How it works

The Nuxt config (`nuxt.config.ts`) uses route rules to proxy requests to the API container:

| Frontend path | Proxied to |
|---|---|
| `/api/**` | `http://api:8000/**` |
| `/docs` | `http://api:8000/docs` (Swagger UI) |
| `/redoc` | `http://api:8000/redoc` |
| `/openapi.json` | `http://api:8000/openapi.json` |

This means the frontend and API are served under the same origin in production — no CORS issues, no separate port to remember.

---

## Stack

| Dependency | Version | Purpose |
|---|---|---|
| [Nuxt](https://nuxt.com) | 4 | Vue meta-framework (SSR + proxy) |
| [Vue](https://vuejs.org) | 3 | UI framework |

The Docker image is a **multi-stage build** — Node 22 Alpine builds the app, and only the `.output/` folder is copied into the final image.
