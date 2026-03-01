# MarkItDown MCP Server

[Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that exposes MarkItDown's file conversion capabilities as tools for AI assistants — Claude Desktop, VS Code Copilot, and any other MCP-compatible client.

---

## Tools

### `convert_file_to_markdown`

Convert a local file to Markdown.

| Parameter | Type | Description |
|---|---|---|
| `file_path` | `string` | Absolute or relative path to the file |

**Returns:** The file contents as a Markdown string.

**Example prompt:** _"Convert ~/Documents/report.pdf to Markdown"_

---

### `convert_url_to_markdown`

Fetch a URL and convert its content to Markdown.

| Parameter | Type | Description |
|---|---|---|
| `url` | `string` | The URL to fetch and convert |

**Returns:** The page or file contents as a Markdown string.

**Example prompt:** _"Summarise https://example.com/whitepaper.pdf as Markdown"_

---

## How it works

The MCP server communicates over **stdio** (standard input/output). It forwards files to the MarkItDown REST API and streams the Markdown result back to the AI client. The API endpoint is configurable via the `MARKITDOWN_API_URL` environment variable.

```
AI Client  ──stdio──►  MCP Server  ──HTTP──►  MarkItDown API
```

---

## Setup

### Prerequisites

- The MarkItDown API must be running (see [api/README.md](../api/README.md))
- Docker (recommended) **or** Python 3.10+

---

### Option A — Docker (recommended)

The MCP server is included in `docker-compose.yml` under the `mcp` profile. Because it uses stdio transport it is run **on-demand**, not as a persistent service.

**Claude Desktop config** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "docker",
      "args": [
        "compose",
        "--profile", "mcp",
        "-f", "/absolute/path/to/docs-for-ai/docker-compose.yml",
        "run", "--rm", "-T", "mcp"
      ]
    }
  }
}
```

Replace `/absolute/path/to/docs-for-ai` with the real path on your machine. A template is provided in [`claude_desktop_config.example.json`](./claude_desktop_config.example.json).

---

### Option B — Python (without Docker)

```bash
cd mcp

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

**Claude Desktop config:**

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "/absolute/path/to/docs-for-ai/mcp/.venv/bin/python",
      "args": ["/absolute/path/to/docs-for-ai/mcp/server.py"],
      "env": {
        "MARKITDOWN_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `MARKITDOWN_API_URL` | `http://localhost:4000/api` | Base URL of the MarkItDown REST API |

When running inside Docker Compose the default is overridden to `http://api:8000` automatically.

---

## Local testing

You can test the MCP server manually by piping JSON-RPC messages:

```bash
# List available tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  | MARKITDOWN_API_URL=http://localhost:8000 python server.py
```

---

## Stack

| Dependency | Purpose |
|---|---|
| [mcp](https://github.com/modelcontextprotocol/python-sdk) | MCP Python SDK (FastMCP) |
| [httpx](https://www.python-httpx.org) | Async HTTP client |
