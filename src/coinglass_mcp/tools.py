"""MCP tool definitions for the CoinGlass MCP server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from coinglass_mcp.client import CoinGlassClient
from coinglass_mcp.validation import (
    normalize_exchange,
    normalize_symbol,
    validate_chart_interval,
    validate_funding_history_interval,
)


def register_tools(app: FastMCP, client: CoinGlassClient) -> None:

    # ── Funding rates ─────────────────────────────────────────────────────

    @app.tool()
    async def get_funding_rates(symbol: str = "BTC") -> list[dict[str, Any]]:
        """
        Get current perpetual futures funding rates for a symbol across all major exchanges.
        Positive rate = longs pay shorts (market is bullish/overheated).
        Negative rate = shorts pay longs (market is bearish/oversold).
        symbol: e.g. 'BTC', 'ETH', 'SOL'
        """
        return await client.get_funding_rates(symbol=normalize_symbol(symbol))

    @app.tool()
    async def get_funding_rate_history(
        symbol: str = "BTC",
        exchange: str = "Binance",
        interval: str = "h8",
    ) -> list[dict[str, Any]]:
        """
        Get historical funding rates for a symbol on a specific exchange.
        symbol: e.g. 'BTC', 'ETH'
        exchange: e.g. 'Binance', 'OKX', 'Bybit', 'dYdX'
        interval: 'h1', 'h4', 'h8' (default), 'd1'
        """
        return await client.get_funding_rate_history(
            symbol=normalize_symbol(symbol),
            exchange=normalize_exchange(exchange),
            interval=validate_funding_history_interval(interval),
        )

    # ── Open interest ─────────────────────────────────────────────────────

    @app.tool()
    async def get_open_interest(symbol: str = "BTC") -> list[dict[str, Any]]:
        """
        Get current open interest (OI) by exchange for a symbol.
        Rising OI + rising price = new longs entering (bullish confirmation).
        Rising OI + falling price = new shorts entering (bearish pressure).
        Falling OI = positions closing (trend may be weakening).
        symbol: e.g. 'BTC', 'ETH'
        """
        return await client.get_open_interest(symbol=normalize_symbol(symbol))

    @app.tool()
    async def get_open_interest_history(
        symbol: str = "BTC",
        interval: str = "h4",
    ) -> list[dict[str, Any]]:
        """
        Get aggregated open interest history chart across all exchanges.
        symbol: e.g. 'BTC', 'ETH'
        interval: 'm15', 'h1', 'h4' (default), 'h8', 'd1'
        """
        return await client.get_open_interest_history(
            symbol=normalize_symbol(symbol),
            interval=validate_chart_interval(interval),
        )

    # ── Long / Short ratio ────────────────────────────────────────────────

    @app.tool()
    async def get_long_short_ratio(
        symbol: str = "BTC",
        exchange: str = "Binance",
        interval: str = "h4",
    ) -> list[dict[str, Any]]:
        """
        Get global long/short account ratio over time.
        Ratio > 1.0 = more accounts are long (potential squeeze if price drops).
        Ratio < 1.0 = more accounts are short (potential short squeeze if price rises).
        symbol: e.g. 'BTC', 'ETH'
        exchange: e.g. 'Binance', 'OKX', 'Bybit'
        interval: 'm15', 'h1', 'h4' (default), 'h8', 'd1'
        """
        return await client.get_long_short_ratio(
            symbol=normalize_symbol(symbol),
            exchange=normalize_exchange(exchange),
            interval=validate_chart_interval(interval),
        )

    # ── Liquidations ──────────────────────────────────────────────────────

    @app.tool()
    async def get_liquidation_info(symbol: str = "BTC") -> dict[str, Any]:
        """
        Get aggregated liquidation statistics for a symbol across timeframes (1h, 4h, 12h, 24h).
        Shows total liquidation amounts split by long and short positions.
        Large long liquidations = forced selling, often marks local bottoms.
        Large short liquidations = forced buying, often marks local tops.
        symbol: e.g. 'BTC', 'ETH'
        """
        return await client.get_liquidation_info(symbol=normalize_symbol(symbol))

    @app.tool()
    async def get_liquidation_history(
        symbol: str = "BTC",
        interval: str = "h4",
    ) -> list[dict[str, Any]]:
        """
        Get historical liquidation chart data (long + short liquidation amounts over time).
        Useful for identifying cascading liquidation events and key price levels.
        symbol: e.g. 'BTC', 'ETH'
        interval: 'm15', 'h1', 'h4' (default), 'h8', 'd1'
        """
        return await client.get_liquidation_history(
            symbol=normalize_symbol(symbol),
            interval=validate_chart_interval(interval),
        )

    # ── BTC Bubble Index ──────────────────────────────────────────────────

    @app.tool()
    async def get_btc_bubble_index() -> list[dict[str, Any]]:
        """
        Get the Bitcoin Bubble Index — a composite indicator combining on-chain data,
        market sentiment, and technical factors to gauge cycle position.
        High values (>80) suggest overheated market / potential cycle top.
        Low values (<20) suggest undervalued / potential cycle bottom.
        """
        return await client.get_btc_bubble_index()
