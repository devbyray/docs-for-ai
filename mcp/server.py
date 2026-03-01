"""
MarkItDown MCP Server

Exposes two tools for AI assistants:
  - convert_file_to_markdown: convert a local file path to Markdown
  - convert_url_to_markdown:  fetch a URL and convert its content to Markdown

Set MARKITDOWN_API_URL to point at the running API (default: http://localhost:4000/api).
"""

import ipaddress
import mimetypes
import os
import socket
from pathlib import Path
from urllib.parse import urlparse

import httpx
from mcp.server.fastmcp import FastMCP

API_URL = os.getenv("MARKITDOWN_API_URL", "http://localhost:4000/api")

# A07 — cap how much data we download from remote URLs (10 MB)
MAX_REMOTE_SIZE = int(os.getenv("MAX_REMOTE_SIZE_MB", "10")) * 1024 * 1024

# RFC-1918 / loopback / link-local ranges blocked for SSRF protection
_BLOCKED_NETWORKS = [
    ipaddress.ip_network(r) for r in (
        "127.0.0.0/8",       # loopback
        "10.0.0.0/8",        # private
        "172.16.0.0/12",     # private
        "192.168.0.0/16",    # private
        "169.254.0.0/16",    # link-local / cloud metadata
        "::1/128",           # IPv6 loopback
        "fc00::/7",          # IPv6 unique local
        "fe80::/10",         # IPv6 link-local
    )
]


def _assert_safe_url(url: str) -> None:
    """Raise ValueError if the URL targets a private/internal address (SSRF guard)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"URL scheme '{parsed.scheme}' is not allowed — use http or https")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL has no hostname")

    try:
        addr = ipaddress.ip_address(socket.gethostbyname(hostname))
    except socket.gaierror as exc:
        raise ValueError(f"Could not resolve hostname '{hostname}': {exc}") from exc

    for network in _BLOCKED_NETWORKS:
        if addr in network:
            raise ValueError(
                f"Requests to internal/private addresses are not allowed ({addr})"
            )


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
                f"{API_URL}/v1/convert",
                files={"file": (path.name, fh, mime)},
            )
        _raise_for_error(response)
        return response.json()["markdown"]


@mcp.tool()
async def convert_url_to_markdown(url: str) -> str:
    """Fetch a URL and convert the content to Markdown.

    Supports web pages (HTML), remote PDFs, images, and any format
    that MarkItDown can handle. Internal/private URLs are blocked.

    Args:
        url: The public URL to fetch and convert.

    Returns:
        The URL contents rendered as Markdown text.
    """
    # A07 — SSRF guard
    try:
        _assert_safe_url(url)
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        async with client.stream("GET", url) as download:
            download.raise_for_status()

            content_type = download.headers.get("content-type", "application/octet-stream")
            mime = content_type.split(";")[0].strip()

            # Enforce download size cap
            chunks = []
            total = 0
            async for chunk in download.aiter_bytes(1024 * 64):
                total += len(chunk)
                if total > MAX_REMOTE_SIZE:
                    raise RuntimeError(
                        f"Remote resource exceeds maximum allowed size of "
                        f"{MAX_REMOTE_SIZE // (1024 * 1024)} MB"
                    )
                chunks.append(chunk)
            content = b"".join(chunks)

    # Derive a filename from the URL path
    url_path = url.rstrip("/").split("?")[0]
    filename = url_path.split("/")[-1] or "index.html"
    if "." not in filename:
        ext = mimetypes.guess_extension(mime) or ".bin"
        filename += ext

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{API_URL}/v1/convert",
            files={"file": (filename, content, mime)},
        )
    _raise_for_error(response)
    return response.json()["markdown"]


if __name__ == "__main__":
    mcp.run(transport="stdio")
