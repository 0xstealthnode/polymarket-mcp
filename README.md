# Fortune Teller - Polymarket MCP Server

A specialized Model Context Protocol (MCP) server that interfaces with Polymarket to provide real-time prediction market data to LLMs. It also exposes a REST API via FastAPI.

## Features

- **MCP Tools**: Connect LLMs (Claude, Cursor, etc.) to Polymarket data.
- **REST API**: Standard JSON endpoints for market data.
- **Read-Only**: Fetches public market data (prices, order books) without requiring authentication.
- **FastAPI Integration**: Built using `fastmcp` mounted on a `fastapi` app.

## Prerequisites

- Python 3.11+
- `uv` package manager (recommended)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Fortune-teller
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

## Configuration

Duplicate the example environment file:

```bash
cp .env.example .env
```

Since the server is running in **Read-Only** mode, no API keys are required for basic data fetching.

## Usage

### Running the Server

Start the server using `uv`:

```bash
uv run python -m src.polymarket_mcp.server
```

The server will be available at `http://0.0.0.0:8000`.

### REST API Endpoints

- `GET /health` - Server status
- `GET /api/markets` - List simplified markets
- `GET /api/markets/{token_id}/price` - Get price for a token
- `GET /api/markets/{token_id}/orderbook` - Get order book

### MCP Tools

This server exposes the following tools to connected MCP clients:

1. `list_markets` - Fetch available markets
2. `get_market_price` - Check price of a specific outcome
3. `get_orderbook` - View market depth

## Development

Use the `fastmcp` CLI for inspecting tools during development:

```bash
uv run fastmcp dev src/polymarket_mcp/server.py
```
