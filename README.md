# ngsnap

Turn a Neuroglancer state (a link or a JSON state) into a consistently styled static PNG,
headlessly and reproducibly — in CI, a paper, a talk, or a blog build.

## The default house style

ngsnap applies its own look to a render rather than trusting whatever the input link happened
to look like. `Style.default()` is the single opinionated default:

- **Chrome off:** hides Neuroglancer's UI controls and panel borders.
- **Fixed size:** renders at 1600×1200 so figures are uniform.
- **Neutral background:** black cross-section and projection backgrounds.
- **Scale bar on:** shown at its natural size.
- **Respects the author:** per-layer visibility and selected segments, the position, and the
  cross-section/projection zoom are left as the state specifies.

The example below is a 4-panel view (2D EM cross-sections plus a 3D mesh) of public FIB-25 data,
rendered with `Style.default()`:

![Default-style render of FIB-25 EM data with a 3D mesh](assets/default-style-example.png)

Regenerate it with `just readme-example` (see [scripts/render_readme_example.py](scripts/render_readme_example.py)).

## Usage

```python
from ngsnap import render, Style

# One-shot render with the default style.
render("https://neuroglancer-demo.appspot.com/#!...", "fig.png")

# Load a site's own style from a TOML file.
render(state_or_url, "fig.png", style=Style.from_file("neuroddities.toml"))
```

The render engine needs the `render` extra (pinned Chrome for Testing via Selenium):

```
uv sync --extra render      # or: pip install "ngsnap[render]"
```

Define your own style by copying [src/ngsnap/styles/default.toml](src/ngsnap/styles/default.toml)
and pointing `Style.from_file(...)` at it.