.PHONY = install test

install:
	uv sync
	uv run pre-commit install

test:
	uv run pyright
