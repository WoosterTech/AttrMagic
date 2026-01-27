.PHONY: install-dev test

install-dev:
	uv sync --all-groups --all-extras

test:
	uv run tox
