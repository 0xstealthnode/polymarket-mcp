import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
from dotenv import load_dotenv
from py_clob_client.exceptions import PolyApiException

# Add the project root to sys.path for fastmcp dev compatibility
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_current_dir))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.polymarket_mcp.client import PolymarketClient


# Load environment variables
load_dotenv()

# Initialize Polymarket Client
try:
    pm_client = PolymarketClient()
except Exception as e:
    print(f"Failed to initialize Polymarket client: {e}")
    pm_client = None

# Initialize FastMCP Server
mcp = FastMCP("Polymarket MCP Server")

# MCP Tools

@mcp.tool
def list_markets():
    """List available markets from Polymarket."""
    if not pm_client:
        return {"error": "Client not initialized"}
    return pm_client.list_markets()

@mcp.tool
def get_market_details(condition_id: str):
    """Get details for a specific market by condition ID."""
    if not pm_client:
        return {"error": "Client not initialized"}
    return pm_client.get_market(condition_id)

@mcp.tool
def get_market_price(token_id: str):
    """Get the current price for a specific token."""
    if not pm_client:
        return {"error": "Client not initialized"}
    return pm_client.get_price(token_id)

@mcp.tool
def get_orderbook(token_id: str):
    """Get the orderbook for a specific token."""
    if not pm_client:
        return {"error": "Client not initialized"}
    return pm_client.get_orderbook(token_id)


# FastAPI App Setup

# Create an ASGI app from the MCP server to handle MCP requests over HTTP (e.g. SSE)
# We mount it at /mcp
mcp_app = mcp.http_app(path="/mcp")

app = FastAPI(
    title="Polymarket MCP Server",
    description="""
A specialized Model Context Protocol (MCP) server that interfaces with Polymarket 
to provide real-time prediction market data to LLMs and REST clients.

## Features
- **Market Discovery**: Search and list active prediction markets
- **Real-time Prices**: Get current prices for any market token
- **Orderbook Data**: View bid/ask depth for markets
- **MCP Integration**: Connect to Claude, Cursor, and other MCP clients

## Notes
- All prices are on a 0-1 scale (0.65 = 65% probability = $0.65 per share)
- Size in orderbooks represents number of shares at that price level
- Each share pays $1 if outcome wins, $0 otherwise
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=mcp_app.lifespan
)

# Mount the MCP server's ASGI app
app.mount("/mcp", mcp_app)

# FastAPI Endpoints

@app.get("/health")
def health_check():
    return {"status": "ok", "client_initialized": pm_client is not None}

@app.get("/api/markets")
def api_list_markets(
    limit: int = 100,
    slug: str = None,
    search: str = None,
    closed: bool = False
):
    """
    List markets. 
    - ?slug=us-strike-on-mexico-by - Filter by exact slug
    - ?search=trump - Search in question text
    - ?limit=200 - Max results (default 100)
    - ?closed=true - Include closed markets
    """
    if not pm_client: raise HTTPException(503, "Client not initialized")
    return pm_client.list_markets(limit=limit, closed=closed, slug=slug, search=search)

@app.get("/api/markets/{token_id}/price")
def api_get_price(token_id: str):
    if not pm_client: raise HTTPException(503, "Client not initialized")
    try:
        return pm_client.get_price(token_id)
    except PolyApiException as e:
        raise HTTPException(status_code=e.status_code, detail=e.error_msg)

@app.get("/api/markets/{token_id}/orderbook")
def api_get_orderbook(token_id: str):
    if not pm_client: raise HTTPException(503, "Client not initialized")
    try:
        return pm_client.get_orderbook(token_id)
    except PolyApiException as e:
        raise HTTPException(status_code=e.status_code, detail=e.error_msg)


if __name__ == "__main__":
    import uvicorn
    # When run directly, we can run the FastAPI server which includes the MCP server
    uvicorn.run(app, host="0.0.0.0", port=8000)
