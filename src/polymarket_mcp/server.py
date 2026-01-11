import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
from dotenv import load_dotenv

from .client import PolymarketClient


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

app = FastAPI(title="Polymarket MCP Server", lifespan=mcp_app.lifespan)

# Mount the MCP server's ASGI app
app.mount("/mcp", mcp_app)

# FastAPI Endpoints

@app.get("/health")
def health_check():
    return {"status": "ok", "client_initialized": pm_client is not None}

@app.get("/api/markets")
def api_list_markets():
    if not pm_client: raise HTTPException(503, "Client not initialized")
    return pm_client.list_markets()

@app.get("/api/markets/{token_id}/price")
def api_get_price(token_id: str):
    if not pm_client: raise HTTPException(503, "Client not initialized")
    return pm_client.get_price(token_id)

@app.get("/api/markets/{token_id}/orderbook")
def api_get_orderbook(token_id: str):
    if not pm_client: raise HTTPException(503, "Client not initialized")
    return pm_client.get_orderbook(token_id)


if __name__ == "__main__":
    import uvicorn
    # When run directly, we can run the FastAPI server which includes the MCP server
    uvicorn.run(app, host="0.0.0.0", port=8000)
