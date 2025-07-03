# OpenRefine MCP Server – Product Requirements Document

## 1. Problem Statement

Analysts automate OpenRefine workflows (create project → apply operations →
export rows) through brittle shell scripts that invoke raw HTTP endpoints. A
Model Context Protocol (MCP) façade will expose these steps as typed,
discoverable primitives, allowing any MCP-capable client (e.g. Claude Desktop)
to orchestrate data-cleaning pipelines safely and reproducibly.

## 2. Goals / Scope (MVP)

* **Tools**
  1. `create_project(dataset_url: str, name: str | None = None)` →
     `ProjectInfo` (`project_id: int`, `name: str`).
  2. `apply_operations(project_id: int, operations_json: str | dict)` →
     `ApplySummary` (`applied: bool`, `last_modified_ms: int`).
* **Resource**
  * `export_csv(project_id: int)`
    – URI template: `refine://{project_id}/export.csv` → `bytes` (CSV, MIME
      `text/csv`).
* Reads base URL from `OPENREFINE_URL` (default `http://localhost:3333`).
  Uses `python-dotenv` to load optional `.env` file.
* No authentication required in MVP.
* Robust error handling and >95 % test coverage.

## 3. Non-Goals

* Endpoints beyond the three above.
* OAuth / token auth between MCP and OpenRefine.
* UI work; server only.

## 4. Success Metrics

| Metric                                     | Target          |
| ------------------------------------------ | --------------- |
| Unit-test pass rate                        | 100 %           |
| End-to-end demo on 10 k-row CSV            | < 10 s          |
| Lines over 88 chars (ruff check E501)      | 0               |
| Users replace shell scripts within         | < 1 h           |

## 5. Technical Overview

* **Language & libs**: Python ≥ 3.9, `mcp[cli]`, `httpx`, `python-dotenv`,
  `python-mimeparse`.
* **OpenRefine endpoints**
  * Create: `POST /command/core/create-project-from-upload?project-name=<name>`
    – multipart field `file`.
  * Apply:  `POST /command/core/apply-operations?project=<id>` – JSON body.
  * Export: `POST /command/core/export-rows?project=<id>&format=csv` – streamed.
* **OpenRefineClient** – single class encapsulating all API calls:

```python
class OpenRefineClient:
    def __init__(self, base_url: str, *, timeout: float = 30): ...

    async def create_project(self, dataset_url: str, name: str | None = None)
        -> ProjectInfo: ...

    async def apply_operations(self, project_id: int,
                               operations: str | dict) -> ApplySummary: ...

    async def export_csv(self, project_id: int) -> bytes: ...
```

* **Streaming**: all network I/O is async; downloads/uploads chunked to
  prevent large memory spikes.
* **Testing**: use **vcr.py** to record & replay HTTP interactions against a
  real OpenRefine instance once, ensuring determinism without heavy mocks.
  VCR cassettes stored under `tests/cassettes/`.

## 6. Risks & Mitigations

| Risk                                  | Mitigation                               |
| ------------------------------------- | ---------------------------------------- |
| Large dataset download                | Stream; enforce `MAX_DOWNLOAD_BYTES`.    |
| Dataset or OpenRefine unavailable     | Raise typed exceptions; expose message.  |
| HTML error pages from OpenRefine      | Detect non-JSON; include snippet in err. |

## 7. Execution Plan (Milestones & Tasks)

### Milestone 0 – Project Bootstrap

* **0.1** Create branch `feat/openrefine-mcp`.
* **0.2** `uv add "mcp[cli]" httpx python-dotenv python-mimeparse vcrpy` and
  dev-deps `pytest anyio`.
* **0.3** Add `.env.example` with `OPENREFINE_URL=http://localhost:3333`.

### Milestone 1 – Core Server Skeleton

* **1.1** `server/openrefine_server.py` with `FastMCP("OpenRefine")` instance.
* **1.2** `settings.py` loads `.env` and exposes `get_openrefine_url()`.
* **1.3** Implement `OpenRefineClient` (see signature above).
* **1.4** Add unit tests for client methods using vcr.py cassettes.

### Milestone 2 – Tool: `create_project`

* **2.1** Define `ProjectInfo` Pydantic model.
* **2.2** Tool implementation uses `OpenRefineClient.create_project()`.
* **2.3** Tests: dataset OK, 404 dataset URL, 400 from OpenRefine (vcr).

### Milestone 3 – Tool: `apply_operations`

* **3.1** Define `ApplySummary` model.
* **3.2** Tool calls `OpenRefineClient.apply_operations()`.
* **3.3** Tests: valid ops, malformed JSON, bad project ID (vcr).

### Milestone 4 – Resource: `export_csv`

* **4.1** Resource `refine://{project_id}/export.csv` calls
  `OpenRefineClient.export_csv()`.
* **4.2** Stream response; return bytes (or temp file URI if >50 MB).
* **4.3** Tests: normal CSV, huge CSV (>50 MB) streamed (vcr).

### Milestone 5 – End-to-End Demo & Docs

* **5.1** `demo/workflow.py` showcasing create→apply→export using
  `ClientSession`.
* **5.2** README section “OpenRefine MCP Server”.
* **5.3** `make demo` target sets up `.env` and runs demo.

### Milestone 6 – CI & Release

* **6.1** GitHub Actions: ruff, pyright, `uv run --frozen pytest`.
* **6.2** Version bump to 0.1.0; PR with reviewers `jerome3o-anthropic`,
  `jspahrsummers`.
* **6.3** CHANGELOG entry and tag.

## 8. Future Enhancements

* Support additional OpenRefine endpoints (reconciliation, faceting).
* Add OAuth/OIDC to secure access to protected OpenRefine instances.
* Async status polling & progress reporting for long-running operations.
