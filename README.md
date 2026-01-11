# Polymarket MCP Server

A specialized Model Context Protocol (MCP) server that interfaces with Polymarket to provide real-time prediction market data to LLMs and REST clients.

## Features

- **MCP Tools**: Connect LLMs (Claude, Cursor, etc.) to Polymarket data
- **REST API**: Standard JSON endpoints for market data
- **Market Search**: Search markets by slug or text
- **Swagger UI**: Interactive API documentation at `/docs`
- **Read-Only**: Fetches public market data without authentication

## Prerequisites

- Python 3.11+
- `uv` package manager (recommended)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/0xstealthnode/polymarket-mcp.git
   cd polymarket-mcp
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

## Configuration

```bash
cp .env.example .env
```

No API keys required for read-only data fetching.

## Usage

### Running the Server

```bash
uv run python -m src.polymarket_mcp.server
```

Server starts at `http://0.0.0.0:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### REST API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Server health check |
| `GET /api/markets` | List active markets |
| `GET /api/markets?slug=<event-slug>` | Get markets by event slug |
| `GET /api/markets?search=<text>` | Search markets by title |
| `GET /api/markets/{token_id}/price` | Get price for a token |
| `GET /api/markets/{token_id}/orderbook` | Get orderbook for a token |

#### Query Parameters for `/api/markets`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 100 | Max results to return |
| `slug` | string | - | Filter by event slug (e.g., `us-strike-on-mexico-by`) |
| `search` | string | - | Search in event/market titles |
| `closed` | bool | false | Include closed markets |

### Example Requests

```bash
# List active markets
curl http://localhost:8000/api/markets

# Search for specific market
curl "http://localhost:8000/api/markets?slug=us-strike-on-mexico-by"

# Search by text
curl "http://localhost:8000/api/markets?search=trump"

# Get price for a token
curl http://localhost:8000/api/markets/TOKEN_ID/price

# Get orderbook
curl http://localhost:8000/api/markets/TOKEN_ID/orderbook
```

## MCP Integration

### Claude Desktop

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "polymarket": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.polymarket_mcp.server"],
      "cwd": "/path/to/polymarket-mcp"
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "polymarket": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.polymarket_mcp.server"],
      "cwd": "/path/to/polymarket-mcp"
    }
  }
}
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `list_markets` | Fetch active prediction markets |
| `get_market_details` | Get details for a market by condition ID |
| `get_market_price` | Get current price for a token |
| `get_orderbook` | View market orderbook depth |

## Development

### MCP Inspector

```bash
uv run fastmcp dev src/polymarket_mcp/server.py
```

## Understanding Polymarket Data

- **Price**: 0-1 scale (0.65 = 65% probability = $0.65 per share)
- **Size**: Number of shares at a price level
- **Token ID**: Unique identifier for each outcome in a market
- **Condition ID**: Identifier for the market itself

Each share pays **$1** if the outcome wins, **$0** if it loses.

## License

MIT
