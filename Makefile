.PHONY = install test

install:
	uv sync
	uv run pre-commit install

test:
	uv run pyright
	uv run pytest

docs/dependencies/mcp-python-sdk.md:
	wget https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/refs/heads/main/README.md -O $@

docs/dependencies/openrefine-api.md:
	wget https://raw.githubusercontent.com/OpenRefine/openrefine.org/refs/heads/master/docs/technical-reference/openrefine-api.md -qO - \
	| grep -B 9999999 "## Third-party software libraries" \
	> $@
	wget https://raw.githubusercontent.com/wiki/OpenRefine/OpenRefine/Changes-for-3.3.md -qO- \
	| grep -A 999999 "## CSRF protection changes" \
	>> $@
