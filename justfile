# Install project and dev dependencies from a fresh clone
install:
    uv sync

# Run the test suite
test:
    uv run pytest

# Lint the source
lint:
    uv run ruff check .

# Format the source
format:
    uv run ruff format .

# Type-check the source
typecheck:
    uv run mypy src
