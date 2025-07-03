"""Data models for OpenRefine MCP Server."""

from pydantic import BaseModel


class ProjectInfo(BaseModel):
    """Information about a created OpenRefine project."""

    project_id: int
    name: str


class ApplySummary(BaseModel):
    """Summary of applied operations on an OpenRefine project."""

    applied: bool
    last_modified_ms: int
