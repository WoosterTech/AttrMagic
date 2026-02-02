.PHONY: install-dev test docs-build docs-serve docs-clean

install-dev:
	uv sync --all-groups --all-extras

test:
	uv run tox

docs-build:
	uv run mkdocs build

docs-serve:
	uv run mkdocs serve

docs-clean:
	rm -rf site/
