"""Server bootstrap for the CoinGlass MCP server."""

from __future__ import annotations

import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
import uvicorn

from coinglass_mcp.client import CoinGlassClient
from coinglass_mcp.config import AppConfig, load_app_config
from coinglass_mcp.tools import register_tools


SERVER_INSTRUCTIONS = """
This MCP server provides crypto derivatives market data from CoinGlass.

Available tools:
- get_funding_rates          — Current funding rates across all exchanges (BTC/ETH/etc.)
- get_funding_rate_history   — Historical funding rate for a symbol on one exchange
- get_open_interest          — Current open interest by exchange
- get_open_interest_history  — Aggregated OI history chart
- get_long_short_ratio       — Global long/short account ratio over time
- get_liquidation_info       — Liquidation stats (1h/4h/12h/24h)
- get_liquidation_history    — Historical liquidation chart (long vs short)
- get_btc_bubble_index       — BTC Bubble Index for cycle position analysis

Use these tools together with market data (CoinGecko) and exchange data (Pionex)
to build a complete picture of market structure before making trading decisions.
""".strip()


async def _oauth_disabled_endpoint(_request) -> JSONResponse:
    return JSONResponse({"error": "OAuth is disabled for this MCP server."}, status_code=404)


def _wrap_trailing_slash_compat(app, request_path: str):
    normalized_path = request_path if request_path.startswith("/") else f"/{request_path}"
    canonical_path = normalized_path.rstrip("/") or "/"
    alternate_path = canonical_path if normalized_path.endswith("/") else f"{canonical_path}/"

    async def wrapped(scope, receive, send):
        if scope["type"] == "http" and scope.get("path") == alternate_path:
            scope = dict(scope)
            scope["path"] = canonical_path
            root_path = scope.get("root_path", "")
            scope["raw_path"] = f"{root_path}{canonical_path}".encode()
        await app(scope, receive, send)

    return wrapped


def _wrap_octet_stream_compat(app, request_path: str):
    normalized_path = request_path if request_path.startswith("/") else f"/{request_path}"
    canonical_path = normalized_path.rstrip("/") or "/"

    async def wrapped(scope, receive, send):
        if scope["type"] == "http" and scope.get("method") == "POST":
            path = scope.get("path", "")
            if path in {canonical_path, f"{canonical_path}/"}:
                raw_headers = scope.get("headers", [])
                rewritten_headers = []
                changed = False
                saw_accept = False
                for key, value in raw_headers:
                    if key.lower() == b"content-type" and value.split(b";", 1)[0].strip() == b"application/octet-stream":
                        rewritten_headers.append((key, b"application/json"))
                        changed = True
                    elif key.lower() == b"accept":
                        saw_accept = True
                        lowered = value.lower()
                        has_json = b"application/json" in lowered
                        has_sse = b"text/event-stream" in lowered
                        has_wildcard = b"*/*" in lowered
                        if has_wildcard or not (has_json and has_sse):
                            rewritten_headers.append((key, b"application/json, text/event-stream"))
                            changed = True
                        else:
                            rewritten_headers.append((key, value))
                    else:
                        rewritten_headers.append((key, value))
                if not saw_accept:
                    rewritten_headers.append((b"accept", b"application/json, text/event-stream"))
                    changed = True
                if changed:
                    scope = dict(scope)
                    scope["headers"] = rewritten_headers
        await app(scope, receive, send)

    return wrapped


def _wrap_http_app(http_app, config: AppConfig) -> Starlette:
    wrapped_app = _wrap_trailing_slash_compat(http_app, config.path)
    wrapped_app = _wrap_octet_stream_compat(wrapped_app, config.path)

    lifespan = getattr(http_app.router, "lifespan_context", None)
    root_app = Starlette(
        lifespan=lifespan,
        routes=[
            Route("/.well-known/oauth-protected-resource", _oauth_disabled_endpoint, methods=["GET"]),
            Route("/.well-known/oauth-protected-resource/{transport:path}", _oauth_disabled_endpoint, methods=["GET"]),
            Route("/.well-known/oauth-authorization-server", _oauth_disabled_endpoint, methods=["GET"]),
            Route("/oauth/authorize", _oauth_disabled_endpoint, methods=["GET"]),
            Mount("", app=wrapped_app),
        ],
    )
    root_app.state.config = config
    return root_app


def build_app() -> tuple[FastMCP, AppConfig]:
    load_dotenv()
    config = load_app_config()
    client = CoinGlassClient(api_key=config.api_key, base_url=config.base_url)

    app = FastMCP(
        name="CoinGlass MCP",
        instructions=SERVER_INSTRUCTIONS,
    )
    app.settings.streamable_http_path = config.path
    app.settings.stateless_http = True
    app.settings.json_response = True
    app.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=config.allowed_hosts,
        allowed_origins=config.allowed_origins,
    )
    register_tools(app, client)
    return app, config


def main() -> None:
    try:
        app, config = build_app()
    except Exception as err:
        print(f"Server bootstrap failed: {err}", file=sys.stderr)
        raise

    print(f"CoinGlass MCP starting. Transport={config.transport} port={config.port}", file=sys.stderr)

    if config.transport in {"stdio", "STDIO"}:
        app.run()
        return

    transport = config.transport.lower()
    if transport in {"http", "streamable-http"}:
        http_app = _wrap_http_app(app.streamable_http_app(), config)
        uvicorn.run(http_app, host=config.host, port=config.port)
        return

    if transport == "sse":
        sse_app = app.sse_app(mount_path=config.path)
        uvicorn.run(sse_app, host=config.host, port=config.port)
        return

    raise ValueError(f"Unsupported transport '{config.transport}'.")


if __name__ == "__main__":
    main()
