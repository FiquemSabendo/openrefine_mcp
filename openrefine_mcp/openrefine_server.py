"""OpenRefine MCP Server implementation."""

import fastmcp
from openrefine_mcp.openrefine_client import OpenRefineClient

# Initialize FastMCP server
app = fastmcp.FastMCP("OpenRefine")

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


@app.tool()
async def create_project(dataset_url: str, name: str | None = None) -> dict:
    """Create a new OpenRefine project from a dataset URL.

    Args:
        dataset_url: URL of the dataset to import
        name: Optional name for the project

    Returns:
        Project information containing project ID and name
    """
    client = get_client()
    result = await client.create_project(dataset_url, name)
    return {"project_id": result.project_id, "name": result.name}


@app.tool()
async def apply_operations(project_id: int, operations: str) -> dict:
    """Apply operations to an OpenRefine project.

    Args:
        project_id: ID of the project to apply operations to
        operations: Operations as JSON string

    Returns:
        Summary with application status and last modified time
    """
    client = get_client()
    result = await client.apply_operations(project_id, operations)
    return {"applied": result.applied, "last_modified_ms": result.last_modified_ms}


@app.tool()
async def export_csv(project_id: int) -> str:
    """Export CSV data from an OpenRefine project.

    Args:
        project_id: ID of the project to export

    Returns:
        CSV data as string
    """
    client = get_client()
    result = await client.export_csv(project_id)
    return result.decode("utf-8")


@app.tool()
async def delete_project(project_id: int) -> bool:
    """Delete an OpenRefine project.

    Args:
        project_id: ID of the project to delete

    Returns:
        True if the project was successfully deleted
    """
    client = get_client()
    return await client.delete_project(project_id)


@app.resource("openrefine://project/{project_id}/models")
async def get_project_models_resource(project_id: int) -> str:
    """Get project models information from OpenRefine.

    Returns structural information about the project including:
    - Column definitions and metadata
    - Record model configuration
    - Available scripting languages
    - Overlay models

    This resource provides the foundation for understanding project structure
    and enables intelligent column references and operation planning.
    """
    client = get_client()
    result = await client.get_project_models(project_id)
    return result.model_dump_json()


if __name__ == "__main__":
    # Run the server
    print("Starting OpenRefine MCP server...")
    app.run()
