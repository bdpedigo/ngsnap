# Install project and dev dependencies from a fresh clone
install:
    uv sync

# Install with the headless render engine (selenium + Chrome for Testing)
install-render:
    uv sync --extra render

# Download the pinned Chrome for Testing build (Selenium Manager; no system Chrome needed)
install-browser:
    uv run --extra render python -c "from ngsnap.render import install_browser; install_browser()"

# Run the test suite (browser integration tests excluded)
test:
    uv run pytest

# Run the browser integration tests (needs the render extra)
test-browser:
    uv run pytest -m browser

# Lint the source
lint:
    uv run ruff check .

# Format the source
format:
    uv run ruff format .

# Type-check the source
typecheck:
    uv run mypy src

# Run lint, format, typecheck, and tests
check: lint format typecheck test

# Render the default-style example image for the README (needs the render extra)
readme-example:
    uv run --extra render python scripts/render_readme_example.py
