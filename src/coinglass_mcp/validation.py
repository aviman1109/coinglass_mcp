"""Input validation helpers for coinglass_mcp."""

from __future__ import annotations


_FUNDING_HISTORY_INTERVALS = {"h1", "h4", "h8", "d1"}
_CHART_INTERVALS = {"m15", "h1", "h4", "h8", "d1"}


def normalize_symbol(symbol: str) -> str:
    value = symbol.strip().upper()
    if not value:
        raise ValueError("symbol must not be empty")
    return value


def normalize_exchange(exchange: str) -> str:
    value = exchange.strip()
    if not value:
        raise ValueError("exchange must not be empty")
    return value


def validate_funding_history_interval(interval: str) -> str:
    value = interval.strip().lower()
    if value not in _FUNDING_HISTORY_INTERVALS:
        allowed = ", ".join(sorted(_FUNDING_HISTORY_INTERVALS))
        raise ValueError(f"interval must be one of: {allowed}")
    return value


def validate_chart_interval(interval: str) -> str:
    value = interval.strip().lower()
    if value not in _CHART_INTERVALS:
        allowed = ", ".join(sorted(_CHART_INTERVALS))
        raise ValueError(f"interval must be one of: {allowed}")
    return value
