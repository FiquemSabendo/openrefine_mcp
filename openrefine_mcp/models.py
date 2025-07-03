"""Data models for OpenRefine MCP Server."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ProjectInfo(BaseModel):
    """Information about a created OpenRefine project."""

    project_id: int
    name: str


class ApplySummary(BaseModel):
    """Summary of applied operations on an OpenRefine project."""

    applied: bool
    last_modified_ms: int


class ColumnInfo(BaseModel):
    """Information about a column in an OpenRefine project."""

    cell_index: int = Field(alias="cellIndex")
    original_name: str = Field(alias="originalName")
    name: str


class ColumnModel(BaseModel):
    """Column model information for an OpenRefine project."""

    columns: List[ColumnInfo]
    key_cell_index: int = Field(alias="keyCellIndex")
    key_column_name: str = Field(alias="keyColumnName")
    column_groups: List[Any] = Field(default=[], alias="columnGroups")

    class Config:
        populate_by_name = True


class RecordModel(BaseModel):
    """Record model information for an OpenRefine project."""

    has_records: bool = Field(alias="hasRecords")

    class Config:
        populate_by_name = True


class ScriptingLanguage(BaseModel):
    """Information about a scripting language supported by OpenRefine."""

    name: str
    default_expression: str = Field(alias="defaultExpression")

    class Config:
        populate_by_name = True


class ScriptingInfo(BaseModel):
    """Scripting information for an OpenRefine project."""

    grel: ScriptingLanguage
    jython: ScriptingLanguage
    clojure: ScriptingLanguage


class ProjectModels(BaseModel):
    """Complete project models information from OpenRefine."""

    column_model: ColumnModel = Field(alias="columnModel")
    record_model: RecordModel = Field(alias="recordModel")
    overlay_models: Dict[str, Any] = Field(default={}, alias="overlayModels")
    scripting: ScriptingInfo

    class Config:
        populate_by_name = True
