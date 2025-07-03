"""OpenRefine HTTP client for API interactions."""

import json
import httpx
from openrefine_mcp.models import ProjectInfo, ApplySummary, ProjectModels
from openrefine_mcp.settings import OPENREFINE_URL


class OpenRefineClient:
    """Client for interacting with OpenRefine API."""

    def __init__(self, base_url: str = OPENREFINE_URL, *, timeout: float = 30):
        """Initialize OpenRefine client.

        Args:
            base_url: Base URL of the OpenRefine instance
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)
        self._csrf_token: str | None = None

    async def _get_csrf_token(self) -> str:
        """Get CSRF token from OpenRefine.

        Returns:
            CSRF token string

        Raises:
            httpx.HTTPStatusError: If the token request fails
        """
        if self._csrf_token is None:
            url = f"{self.base_url}/command/core/get-csrf-token"
            response = await self._client.get(url)
            self._validate_openrefine_response(response)
            result = response.json()
            self._csrf_token = result.get("token")
            if not self._csrf_token:
                raise ValueError("Failed to get CSRF token: no token returned")
        return self._csrf_token

    async def _get(self, *args, **kwargs) -> httpx.Response:
        """Make a GET request to OpenRefine API.

        Args:
            *args: Positional arguments passed to httpx.AsyncClient.post
            **kwargs: Keyword arguments passed to httpx.AsyncClient.post

        Returns:
            httpx.Response: Validated response from OpenRefine API

        Raises:
            httpx.HTTPStatusError: If the request fails
            ValueError: If OpenRefine returns an error in the response body
        """
        response = await self._client.get(*args, **kwargs)
        return self._validate_openrefine_response(response)

    async def _post(
        self,
        *args,
        **kwargs,
    ) -> httpx.Response:
        """Make a POST request to OpenRefine API.

        Args:
            *args: Positional arguments passed to httpx.AsyncClient.post
            **kwargs: Keyword arguments passed to httpx.AsyncClient.post

        Returns:
            httpx.Response: Validated response from OpenRefine API

        Raises:
            httpx.HTTPStatusError: If the request fails or returns an error status
            ValueError: If OpenRefine returns an error in the response body
        """
        # Get CSRF token if required
        csrf_token = await self._get_csrf_token()
        if kwargs.get("params") is None:
            kwargs["params"] = {}
        kwargs["params"]["csrf_token"] = csrf_token

        response = await self._client.post(
            *args,
            **kwargs,
        )
        return self._validate_openrefine_response(response)

    async def create_project(
        self, dataset_url: str, name: str | None = None
    ) -> ProjectInfo:
        """Create a new OpenRefine project from a dataset URL.

        Args:
            dataset_url: URL of the dataset to import
            name: Optional name for the project

        Returns:
            ProjectInfo containing project ID and name

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        # Download the dataset first
        async with httpx.AsyncClient(timeout=self.timeout) as download_client:
            response = await download_client.get(dataset_url)
            self._validate_openrefine_response(response)
            dataset_content = response.content

        # Prepare multipart form data
        files = {"project-file": ("dataset.csv", dataset_content, "text/csv")}
        data = {}
        if name:
            data["project-name"] = name

        # Build the create project URL
        url = f"{self.base_url}/command/core/create-project-from-upload"

        # Make the create project request
        response = await self._post(url, data=data, files=files)

        # For successful project creation, OpenRefine returns a 302 redirect
        # with the project ID in the Location header
        if response.status_code == 302:
            location = response.headers.get("location", "")
            # Extract project ID from redirect URL: /project?project=<id>
            if "project=" in location:
                project_id = location.split("project=")[1]
                return ProjectInfo(project_id=int(project_id), name=name or "Untitled")
            else:
                raise ValueError("Failed to create project: no project ID in redirect")

        # Try to parse JSON response as fallback
        try:
            result = response.json()
            project_id = result.get("projectID")
            project_name = result.get("projectName", name or "Untitled")

            if project_id is None:
                raise ValueError("Failed to create project: no project ID returned")

            return ProjectInfo(project_id=project_id, name=project_name)
        except json.JSONDecodeError:
            raise ValueError("Failed to create project: unexpected response format")

    async def apply_operations(
        self, project_id: int, operations: str | dict
    ) -> ApplySummary:
        """Apply operations to an OpenRefine project.

        Args:
            project_id: ID of the project to apply operations to
            operations: Operations as JSON string or dict

        Returns:
            ApplySummary with application status and last modified time

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        # Convert operations to JSON string if it's a dict
        if isinstance(operations, str):
            operations_json = operations
        else:
            operations_json = json.dumps(operations)

        # Build the apply operations URL
        url = f"{self.base_url}/command/core/apply-operations"
        params = {"project": str(project_id)}

        # Make the apply operations request
        response = await self._post(
            url,
            params=params,
            data={"operations": operations_json},
        )

        # Parse the response
        result = response.json()

        # Extract summary info from response
        applied = result.get("code", "error") == "ok"
        last_modified = result.get("lastModified", 0)

        return ApplySummary(applied=applied, last_modified_ms=last_modified)

    async def export_csv(self, project_id: int) -> bytes:
        """Export CSV data from an OpenRefine project.

        Args:
            project_id: ID of the project to export

        Returns:
            CSV data as bytes

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        # Build the export URL
        url = f"{self.base_url}/command/core/export-rows"
        params = {"project": str(project_id), "format": "csv"}

        # Make the export request (CSRF required for export)
        response = await self._post(url, params=params)

        return response.content

    async def delete_project(self, project_id: int) -> bool:
        """Delete an OpenRefine project.

        Args:
            project_id: ID of the project to delete

        Returns:
            True if the project was successfully deleted

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        # Build the delete project URL
        url = f"{self.base_url}/command/core/delete-project"
        params = {"project": str(project_id)}

        # Make the delete project request
        response = await self._post(url, params=params)

        # Parse the response
        result = response.json()

        # Check if deletion was successful
        return result.get("code", "error") == "ok"

    async def get_project_models(self, project_id: int) -> ProjectModels:
        """Get project models information from OpenRefine.

        Args:
            project_id: ID of the project to get models for

        Returns:
            ProjectModels containing column, record, overlay models and scripting info

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        # Build the get models URL
        url = f"{self.base_url}/command/core/get-models"
        params = {"project": str(project_id)}

        # Make the get models request
        response = await self._get(url, params=params)

        # Parse the response
        result = response.json()

        # Return the project models
        return ProjectModels(**result)

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    def _validate_openrefine_response(self, response: httpx.Response) -> httpx.Response:
        """Validate the response from OpenRefine.

        Args:
            response: HTTP response to validate

        Returns:
            The validated response

        Raises:
            httpx.HTTPStatusError: If the response indicates an error
            ValueError: If OpenRefine returns an error in the response body
        """
        # Don't raise for redirects (302) as they're expected for project creation
        if response.status_code != 302:
            response.raise_for_status()

        try:
            data = response.json()
            if data.get("code") == "error":
                raise ValueError(
                    f"OpenRefine API returned error: {data.get('message', 'Unknown error')}"
                )
        except json.JSONDecodeError:
            # Not JSON response, which is fine for some endpoints like export
            pass

        return response

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
