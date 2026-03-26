"""CoinGlass API client.

API reference: https://coinglass.com/api_doc_v2
Base URL: https://open-api.coinglass.com
Auth header: CG-API-KEY

Key endpoint groups used:
  /api/pro/v1/futures/fundingRate/current      — current funding rates across exchanges
  /api/pro/v1/futures/openInterest/list        — open interest by exchange
  /api/pro/v1/futures/globalLongShortAccountRatio/list  — long/short account ratio
  /api/pro/v1/futures/liquidation/info         — aggregated liquidation data
  /api/pro/v1/futures/liquidation/chart        — liquidation history chart
  /api/pro/v1/index/bitcoin-bubble-index       — BTC bubble index
"""

from __future__ import annotations

from typing import Any

import httpx

_TIMEOUT = httpx.Timeout(15.0)


class CoinGlassClient:
    def __init__(self, api_key: str, base_url: str) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "accept": "application/json",
                "CG-API-KEY": api_key,
            },
            timeout=_TIMEOUT,
        )

    async def _get(self, path: str, params: dict | None = None) -> Any:
        r = await self._http.get(path, params=params or {})
        r.raise_for_status()
        body = r.json()
        # CoinGlass wraps responses in {"code":"0","data":...}
        if isinstance(body, dict):
            code = str(body.get("code", "0"))
            if code != "0":
                message = body.get("msg") or body.get("message") or "CoinGlass API error"
                raise ValueError(f"{message} (code={code})")
        if isinstance(body, dict) and "data" in body:
            return body["data"]
        return body

    # ── Funding rates ─────────────────────────────────────────────────────

    async def get_funding_rates(self, symbol: str = "BTC") -> list[dict[str, Any]]:
        """Current funding rates for a symbol across all exchanges."""
        return await self._get(
            "/api/pro/v1/futures/fundingRate/current",
            params={"symbol": symbol},
        )

    async def get_funding_rate_history(
        self, symbol: str = "BTC", exchange: str = "Binance", interval: str = "h8"
    ) -> list[dict[str, Any]]:
        """Funding rate history for a symbol on a specific exchange.
        interval: h1, h4, h8, d1
        """
        return await self._get(
            "/api/pro/v1/futures/fundingRate/chart",
            params={"symbol": symbol, "exchangeName": exchange, "interval": interval},
        )

    # ── Open interest ─────────────────────────────────────────────────────

    async def get_open_interest(self, symbol: str = "BTC") -> list[dict[str, Any]]:
        """Open interest by exchange for a symbol."""
        return await self._get(
            "/api/pro/v1/futures/openInterest/list",
            params={"symbol": symbol},
        )

    async def get_open_interest_history(
        self, symbol: str = "BTC", interval: str = "h4"
    ) -> list[dict[str, Any]]:
        """Aggregated open interest history.
        interval: m15, h1, h4, h8, d1
        """
        return await self._get(
            "/api/pro/v1/futures/openInterest/chart",
            params={"symbol": symbol, "interval": interval},
        )

    # ── Long / Short ratio ────────────────────────────────────────────────

    async def get_long_short_ratio(
        self, symbol: str = "BTC", exchange: str = "Binance", interval: str = "h4"
    ) -> list[dict[str, Any]]:
        """Global long/short account ratio (big traders + retail).
        interval: m15, h1, h4, h8, d1
        """
        return await self._get(
            "/api/pro/v1/futures/globalLongShortAccountRatio/list",
            params={"symbol": symbol, "exchangeName": exchange, "interval": interval},
        )

    # ── Liquidations ──────────────────────────────────────────────────────

    async def get_liquidation_info(self, symbol: str = "BTC") -> dict[str, Any]:
        """Aggregated liquidation stats (1h, 4h, 12h, 24h)."""
        return await self._get(
            "/api/pro/v1/futures/liquidation/info",
            params={"symbol": symbol},
        )

    async def get_liquidation_history(
        self, symbol: str = "BTC", interval: str = "h4"
    ) -> list[dict[str, Any]]:
        """Liquidation history chart (long + short liquidation amounts).
        interval: m15, h1, h4, h8, d1
        """
        return await self._get(
            "/api/pro/v1/futures/liquidation/chart",
            params={"symbol": symbol, "interval": interval},
        )

    # ── BTC Bubble Index ──────────────────────────────────────────────────

    async def get_btc_bubble_index(self) -> list[dict[str, Any]]:
        """BTC Bubble Index — composite indicator for cycle top detection."""
        return await self._get("/api/pro/v1/index/bitcoin-bubble-index")

    async def aclose(self) -> None:
        await self._http.aclose()
