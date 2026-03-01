"""
MarkItDown MCP Server

Exposes two tools for AI assistants:
  - convert_file_to_markdown: convert a local file path to Markdown
  - convert_url_to_markdown:  fetch a URL and convert its content to Markdown

Set MARKITDOWN_API_URL to point at the running API (default: http://localhost:4000/api).
"""

import os
import mimetypes
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

API_URL = os.getenv("MARKITDOWN_API_URL", "http://localhost:4000/api")

mcp = FastMCP(
    "markitdown",
    instructions=(
        "Use convert_file_to_markdown to turn local files (PDF, DOCX, PPTX, XLSX, "
        "images, audio, HTML, CSV…) into Markdown. "
        "Use convert_url_to_markdown to fetch and convert a web page or remote file."
    ),
)


def _raise_for_error(response: httpx.Response) -> None:
    if response.is_error:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise RuntimeError(f"API error {response.status_code}: {detail}")


@mcp.tool()
async def convert_file_to_markdown(file_path: str) -> str:
    """Convert a local file to Markdown.

    Args:
        file_path: Absolute or relative path to the file on the local filesystem.

    Returns:
        The file contents rendered as Markdown text.
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    mime, _ = mimetypes.guess_type(str(path))
    mime = mime or "application/octet-stream"

    async with httpx.AsyncClient(timeout=120) as client:
        with path.open("rb") as fh:
            response = await client.post(
                f"{API_URL}/convert",
                files={"file": (path.name, fh, mime)},
            )
        _raise_for_error(response)
        return response.json()["markdown"]


@mcp.tool()
async def convert_url_to_markdown(url: str) -> str:
    """Fetch a URL and convert the content to Markdown.

    Supports web pages (HTML), remote PDFs, images, and any format
    that MarkItDown can handle.

    Args:
        url: The URL to fetch and convert.

    Returns:
        The URL contents rendered as Markdown text.
    """
    async with httpx.AsyncClient(
        timeout=120, follow_redirects=True
    ) as client:
        # Download the resource
        download = await client.get(url)
        download.raise_for_status()

        content_type = download.headers.get("content-type", "application/octet-stream")
        mime = content_type.split(";")[0].strip()

        # Derive a filename from the URL path
        url_path = url.rstrip("/").split("?")[0]
        filename = url_path.split("/")[-1] or "index.html"
        if "." not in filename:
            ext = mimetypes.guess_extension(mime) or ".bin"
            filename += ext

        # Forward to the convert endpoint
        response = await client.post(
            f"{API_URL}/convert",
            files={"file": (filename, download.content, mime)},
        )
        _raise_for_error(response)
        return response.json()["markdown"]


if __name__ == "__main__":
    mcp.run(transport="stdio")
