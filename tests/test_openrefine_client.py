import csv
import io
import json
import pytest
import pytest_asyncio
from openrefine_mcp.openrefine_client import OpenRefineClient
from openrefine_mcp.models import ProjectInfo, ApplySummary, ProjectModels


class TestOpenRefineClient:
    @pytest.mark.vcr
    @pytest.mark.asyncio
    async def test_create_project_success(self, client, test_dataset_url):
        """Test successful project creation."""
        project_info = await client.create_project(
            test_dataset_url, name="Test Project"
        )

        assert isinstance(project_info, ProjectInfo)
        assert project_info.project_id is not None
        assert project_info.name == "Test Project"

    @pytest.mark.vcr
    @pytest.mark.asyncio
    async def test_create_project_without_name(self, client, test_dataset_url):
        """Test project creation without explicit name."""
        project_info = await client.create_project(test_dataset_url)

        assert isinstance(project_info, ProjectInfo)
        assert project_info.project_id is not None
        assert project_info.name  # Should have some name

    @pytest.mark.vcr
    @pytest.mark.asyncio
    async def test_create_project_invalid_dataset_url(self, client):
        """Test project creation with invalid dataset URL."""
        with pytest.raises(Exception):  # Should raise httpx.HTTPStatusError
            await client.create_project("https://invalid-url.example.com/data.csv")

    @pytest.mark.vcr
    @pytest.mark.asyncio
    async def test_apply_operations_success(self, client, sample_project):
        """Test successful operations application."""
        # Sample operations JSON
        operations = [
            {
                "op": "core/row-addition",
                "rows": [{"starred": False, "flagged": False, "cells": []}],
                "index": 0,
                "description": "Add rows",
            }
        ]

        summary = await client.apply_operations(sample_project.project_id, operations)

        assert isinstance(summary, ApplySummary)
        assert isinstance(summary.applied, bool)
        assert isinstance(summary.last_modified_ms, int)

    @pytest.mark.vcr
    @pytest.mark.asyncio
    async def test_apply_operations_with_string(self, client, sample_project):
        """Test operations application with JSON string."""
        operations_json = json.dumps(
            [
                {
                    "op": "core/row-addition",
                    "rows": [{"starred": False, "flagged": False, "cells": []}],
                    "index": 0,
                    "description": "Add rows",
                }
            ]
        )

        summary = await client.apply_operations(
            sample_project.project_id, operations_json
        )

        assert isinstance(summary, ApplySummary)
        assert isinstance(summary.applied, bool)
        assert isinstance(summary.last_modified_ms, int)

    @pytest.mark.vcr
    @pytest.mark.asyncio
    async def test_apply_operations_invalid_project(self, client):
        """Test operations application with invalid project ID."""
        operations = [{"op": "core/text-transform"}]

        with pytest.raises(Exception):  # Should raise httpx.HTTPStatusError
            await client.apply_operations(99999, operations)

    @pytest.mark.vcr
    @pytest.mark.asyncio
    async def test_export_csv_success(self, client, sample_project):
        """Test successful CSV export."""
        csv_data = await client.export_csv(sample_project.project_id)
        csv_fp = io.StringIO(csv_data.decode("utf-8"))
        data = list(csv.reader(csv_fp))

        assert isinstance(csv_data, bytes)
        assert len(data) > 400

    @pytest.mark.vcr
    @pytest.mark.asyncio
    async def test_export_csv_invalid_project(self, client):
        """Test CSV export with invalid project ID."""
        with pytest.raises(Exception):  # Should raise httpx.HTTPStatusError
            await client.export_csv(99999)

    @pytest.mark.vcr
    @pytest.mark.asyncio
    async def test_delete_project_success(self, client, sample_project):
        """Test successful project deletion."""
        # Delete the project
        deleted = await client.delete_project(sample_project.project_id)

        assert deleted is True

    @pytest.mark.vcr
    @pytest.mark.asyncio
    async def test_delete_project_invalid_project(self, client):
        """Test project deletion with invalid project ID."""
        # OpenRefine returns success even for non-existent projects (idempotent)
        deleted = await client.delete_project(99999)
        assert deleted is True

    @pytest.mark.vcr
    @pytest.mark.asyncio
    async def test_get_project_models_success(self, client, sample_project):
        """Test successful project models retrieval."""
        models = await client.get_project_models(sample_project.project_id)

        assert isinstance(models, ProjectModels)
        assert len(models.column_model.columns) == 11

    @pytest.mark.vcr
    @pytest.mark.asyncio
    async def test_get_project_models_invalid_project(self, client):
        """Test project models retrieval with invalid project ID."""
        with pytest.raises(Exception):  # Should raise httpx.HTTPStatusError
            await client.get_project_models(99999)

    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test that client works as async context manager."""
        async with OpenRefineClient("http://localhost:3333") as client:
            assert client is not None
        # Client should be closed after context

    def test_client_initialization(self):
        """Test client initialization."""
        client = OpenRefineClient("http://localhost:3333", timeout=60)

        assert client.base_url == "http://localhost:3333"
        assert client.timeout == 60

        # Test URL stripping
        client_with_slash = OpenRefineClient("http://localhost:3333/", timeout=30)
        assert client_with_slash.base_url == "http://localhost:3333"


@pytest.fixture
def client():
    """Create a test OpenRefine client."""
    return OpenRefineClient()


@pytest.fixture
def test_dataset_url():
    """Sample dataset URL for testing."""
    return "https://raw.githubusercontent.com/vitorbaptista/birmingham_schools/refs/heads/master/data/birmingham_schools.csv"


@pytest_asyncio.fixture
async def sample_project(client, test_dataset_url):
    """Create a sample project for testing and clean it up afterward."""
    project_info = await client.create_project(
        test_dataset_url, name="Sample Test Project"
    )
    try:
        yield project_info
    finally:
        # Clean up: delete the project after the test
        await client.delete_project(project_info.project_id)
