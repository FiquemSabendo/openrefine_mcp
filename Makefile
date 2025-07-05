.PHONY = install test inspector claude_desktop_config

install:
	uv sync
	uv run pre-commit install

test:
	uv run pyright
	uv run pytest

inspector:
	npx @modelcontextprotocol/inspector \
		uv \
		--directory openrefine_mcp \
		run \
		openrefine_server.py

claude_desktop_config:
	@echo '{'
	@echo '  "mcpServers": {'
	@echo '    "openrefine": {'
	@echo '      "command": "uv",'
	@echo '      "args": ['
	@echo '        "--directory",'
	@echo '        "$(shell pwd)",'
	@echo '        "run",'
	@echo '        "openrefine_mcp/openrefine_server.py"'
	@echo '      ],'
	@echo '      "env": {'
	@echo '        "OPENREFINE_URL": "http://localhost:3333"'
	@echo '      }'
	@echo '    }'
	@echo '  }'
	@echo '}'

docs/dependencies/mcp-python-sdk.md:
	wget https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/refs/heads/main/README.md -O $@

docs/dependencies/openrefine-api.md:
	wget https://raw.githubusercontent.com/OpenRefine/openrefine.org/refs/heads/master/docs/technical-reference/openrefine-api.md -qO - \
	| grep -B 9999999 "## Third-party software libraries" \
	> $@
	wget https://raw.githubusercontent.com/wiki/OpenRefine/OpenRefine/Changes-for-3.3.md -qO- \
	| grep -A 999999 "## CSRF protection changes" \
	>> $@
