# coinglass-mcp

`coinglass-mcp` is an MCP server for CoinGlass derivatives data. It exposes funding rates, open interest, long/short ratios, liquidation metrics, and the BTC Bubble Index for LLM workflows that need market structure context.

## What It Covers

- Current funding rates across major exchanges
- Funding rate history for one exchange and symbol
- Open interest snapshots and aggregated OI history
- Global long/short account ratio history
- Liquidation summaries and liquidation chart history
- Bitcoin Bubble Index

## Why This Server Exists

CoinGlass is useful for derivatives structure, but its API is not ergonomic for agent tool use. This project wraps the API in MCP tools with:

- cleaner tool descriptions
- interval validation
- normalized symbols
- HTTP and stdio transport support
- safer defaults for local deployment

## Requirements

- Python 3.11+
- A CoinGlass API key

Get a key from: <https://www.coinglass.com/pricing>

## Quick Start

1. Create your local env file:

```bash
cp secrets/coinglass.env.example secrets/coinglass.env
```

2. Fill in `COINGLASS_API_KEY` in `secrets/coinglass.env`.

3. Run locally:

```bash
pip install -e .
python -m coinglass_mcp
```

## Docker

```bash
docker build -t coinglass-mcp .
docker run --rm -p 38090:38090 --env-file secrets/coinglass.env coinglass-mcp
```

## Claude / Codex MCP Registration

```bash
claude mcp add coinglass --transport http http://127.0.0.1:38090/mcp
```

## Tools

| Tool | Purpose |
|------|---------|
| `get_funding_rates` | Current perpetual funding rates across exchanges |
| `get_funding_rate_history` | Historical funding rates for a symbol on one exchange |
| `get_open_interest` | Current open interest by exchange |
| `get_open_interest_history` | Aggregated open interest history |
| `get_long_short_ratio` | Global long/short account ratio history |
| `get_liquidation_info` | 1h / 4h / 12h / 24h liquidation summary |
| `get_liquidation_history` | Historical liquidation chart |
| `get_btc_bubble_index` | BTC Bubble Index for cycle analysis |

## Interpreting the Data

| Signal | Typical Interpretation |
|--------|------------------------|
| Funding rate > 0.1% | Longs crowded, higher squeeze risk |
| Funding rate < -0.05% | Shorts crowded, rebound or squeeze setup |
| OI rising + price rising | Trend confirmation |
| OI rising + price falling | Short pressure building |
| OI falling | Position unwinding |
| Long/short ratio > 1.5 | Retail long crowding |
| Large long liquidations | Forced selling, can mark local panic |
| Large short liquidations | Short squeeze / forced upside |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `COINGLASS_API_KEY` | required | CoinGlass API key |
| `COINGLASS_BASE_URL` | `https://open-api.coinglass.com` | API base URL |
| `MCP_TRANSPORT` | `http` | `http`, `streamable-http`, `sse`, or `stdio` |
| `MCP_HOST` | `0.0.0.0` | Bind host |
| `PORT` | `38090` | HTTP listen port |
| `MCP_PATH` | `/mcp` | MCP endpoint path |
| `MCP_ALLOWED_HOSTS` | empty | Extra allowed hosts, comma-separated |
| `MCP_ALLOWED_ORIGINS` | empty | Extra allowed origins, comma-separated |

## Development

Install test dependencies and run tests:

```bash
pip install -e ".[test]"
pytest
```

## Security Notes

- Do not commit `secrets/coinglass.env`
- Prefer using a restricted API key when possible
- Expose the HTTP transport behind your own auth layer if you open it beyond localhost
