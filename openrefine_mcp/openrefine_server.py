"""OpenRefine MCP Server implementation."""

from mcp.server.fastmcp import FastMCP
from openrefine_mcp.openrefine_client import OpenRefineClient

# Initialize FastMCP server
app = FastMCP("OpenRefine")

# Global client instance
_client: OpenRefineClient | None = None


def get_client() -> OpenRefineClient:
    """Get or create the OpenRefine client instance.

    Returns:
        OpenRefineClient instance
    """
    global _client
    if _client is None:
        _client = OpenRefineClient()
    return _client


if __name__ == "__main__":
    # Run the server
    app.run()
