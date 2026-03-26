"""Configuration for the CoinGlass MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _parse_csv_env(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class AppConfig:
    api_key: str
    base_url: str
    transport: str
    host: str
    port: int
    path: str
    allowed_hosts: list[str]
    allowed_origins: list[str]


def load_app_config() -> AppConfig:
    api_key = os.getenv("COINGLASS_API_KEY", "")
    if not api_key:
        raise ValueError(
            "COINGLASS_API_KEY must be set. "
            "Get a free key at https://www.coinglass.com/pricing and add it to secrets/coinglass.env."
        )

    default_allowed_hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
    default_allowed_origins = [
        "http://127.0.0.1:*",
        "http://localhost:*",
        "http://[::1]:*",
    ]

    return AppConfig(
        api_key=api_key,
        base_url=os.getenv("COINGLASS_BASE_URL", "https://open-api.coinglass.com"),
        transport=os.getenv("MCP_TRANSPORT", "http"),
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "38090")),
        path=os.getenv("MCP_PATH", "/mcp"),
        allowed_hosts=default_allowed_hosts + _parse_csv_env(os.getenv("MCP_ALLOWED_HOSTS")),
        allowed_origins=default_allowed_origins
        + _parse_csv_env(os.getenv("MCP_ALLOWED_ORIGINS")),
    )
