from coinglass_mcp.validation import (
    normalize_exchange,
    normalize_symbol,
    validate_chart_interval,
    validate_funding_history_interval,
)


def test_normalize_symbol_uppercases_and_trims() -> None:
    assert normalize_symbol(" eth ") == "ETH"


def test_normalize_exchange_requires_value() -> None:
    try:
        normalize_exchange("   ")
    except ValueError as exc:
        assert "exchange must not be empty" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_validate_funding_history_interval_rejects_invalid_values() -> None:
    try:
        validate_funding_history_interval("m15")
    except ValueError as exc:
        assert "interval must be one of" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_validate_chart_interval_accepts_h4() -> None:
    assert validate_chart_interval("H4") == "h4"
