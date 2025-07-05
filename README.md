# OpenRefine MCP Server

[![Test](https://github.com/FiquemSabendo/openrefine_mcp/actions/workflows/test.yml/badge.svg)](https://github.com/FiquemSabendo/openrefine_mcp/actions/workflows/test.yml)

A Model Context Protocol (MCP) server that provides a typed, discoverable interface to OpenRefine's HTTP API. This allows any MCP-capable client (like Claude Desktop) to orchestrate data-cleaning pipelines safely and reproducibly.

## Installation

### Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- OpenRefine instance running (default: `http://localhost:3333`)

### Install the Package

```bash
# Clone the repository
git clone <repository-url>
cd openrefine_mcp

# Install dependencies using uv
uv sync
```

### Setup Claude Desktop

1. Create or edit your Claude Desktop configuration file:
   ```bash
   # On macOS/Linux
   ~/.config/claude_desktop_config.json

   # On Windows
   %APPDATA%\claude_desktop_config.json
   ```

2. Add the OpenRefine MCP server to your configuration:
   ```json
   {
     "mcpServers": {
       "openrefine": {
         "command": "uv",
         "args": [
           "--directory",
           "path/to/your/openrefine_mcp",
           "run",
           "openrefine_mcp/openrefine_server.py"
         ],
         "env": {
           "OPENREFINE_URL": "http://localhost:3333"
         }
       }
     }
   }
   ```

3. Restart Claude Desktop to load the new MCP server.

## Features

This MCP server implements the following OpenRefine API endpoints:

| OpenRefine API Endpoint | MCP Implementation | Status |
|-------------------------|-------------------|---------|
| `POST /command/core/create-project-from-upload` | `create_project(dataset_url: str, name: str \| None = None)` | ✅ |
| `GET /command/core/get-models` | `get_project_models(project_id: int)` resource | ✅ |
| `POST /command/core/apply-operations` | `apply_operations(project_id: int, operations: str)` | ✅ |
| `POST /command/core/export-rows` | `export_csv(project_id: int)` | ✅ |
| `POST /command/core/delete-project` | `delete_project(project_id: int)` | ✅ |
| `POST /command/core/set-project-metadata` | - | ❌ |
| `POST /command/core/set-project-tags` | - | ❌ |
| `GET /command/core/get-all-project-metadata` | - | ❌ |
| `POST /command/core/preview-expression` | - | ❌ |
| `GET /command/core/get-processes` | - | ❌ |

### Available Tools

- **`create_project(dataset_url: str, name: str | None = None)`** → Creates a new OpenRefine project from a dataset URL
- **`apply_operations(project_id: int, operations: str)`** → Applies operations to an OpenRefine project
- **`export_csv(project_id: int)`** → Exports CSV data from an OpenRefine project
- **`delete_project(project_id: int)`** → Deletes an OpenRefine project

### Available Resources

- **`openrefine://project/{project_id}/models`** → Returns structural information about the project including column definitions, record model configuration, available scripting languages, and overlay models

## Development

### Running Tests

```bash
make test
```

### Running the MCP Inspector server

```bash
make inspector
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
