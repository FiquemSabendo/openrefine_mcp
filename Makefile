.PHONY = install test

install:
	uv sync
	uv run pre-commit install

test:
	uv run pyright

docs/dependencies/mcp-python-sdk.md:
	wget https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/refs/heads/main/README.md -O $@

docs/dependencies/openrefine-api.md:
	wget https://github.com/OpenRefine/openrefine.org/blob/master/docs/technical-reference/openrefine-api.md -O $@
