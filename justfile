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

# Install the spike browser-driver dependencies (selenium, playwright, psutil)
spike-deps:
    uv sync --group spike

# Render the representative state headlessly: driver = chrome | firefox-xvfb | playwright
spike-render driver="chrome":
    cd spike && uv run python render_spike.py --driver {{driver}}

# Render a 4panel variant so 2D cross-sections and the 3D mesh are both visible
spike-render-4panel driver="chrome":
    cd spike && uv run python render_spike.py --driver {{driver}} --layout 4panel --out-dir out-4panel
