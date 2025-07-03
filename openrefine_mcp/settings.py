"""Settings module for OpenRefine MCP Server."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

OPENREFINE_URL = os.getenv("OPENREFINE_URL", "http://localhost:3333")
