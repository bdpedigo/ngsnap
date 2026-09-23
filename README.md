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

## Python API

> **Target API.** This section describes the intended shape of the public API. Lines
> marked `# planned` are not implemented yet; everything else works today. It exists so
> we can agree on the surface before filling in the gaps.

<!-- TODO style might someday encompass other fixed aspects of state, such as data sources or things like that - i wonder if it is worth making this more general early, or if that is confusing/clunky? it is kind of a stencil/template etc. but not sure what else we could call it -->

A `Style` is the unit of reuse: a named look you can **apply** to make links uniform,
**check** links against, and **extract** from a link you already like. Rendering is a
separate step that takes a style.

```python
from ngsnap import Style, render, render_all, cache_key

# the link you are starting with
link = "https://neuroglancer-demo.appspot.com/#!..."
```

### Styles

```python
style = Style.default()                    # the one opinionated house style
style = Style.from_file("my_style.toml")

# Generate a new style FROM a link by lifting a named setting group out of it.
style = Style.from_state(link, groups=["cosmetic"])   # planned
style.to_file("my_style.toml")                    # planned — round-trips with from_file
```

### Apply a style — make one or more links uniform

```python
templated = style.apply(link)              # -> TemplatedState
templated.to_url()                         # restyled Neuroglancer link (host prefix preserved)
templated.to_json()                        # canonical viewer-state JSON

for templated in style.apply_all(links):   # planned — one or more links
    templated.to_url()
```

`apply` never touches a browser, so it is cheap and usable purely to produce restyled
links or JSON. Under the hood it goes through the general templating interface:

<!-- TODO why do we need a different API here? could the same apply just accept either a Style object or a dict or a path to a TOML? -->
```python
from ngsnap import apply_template, REMOVE

# Ad-hoc, one-off overrides without authoring a Style.
apply_template(link, {"showAxisLines": False, "layers": {"seg": {"visible": True}}})
apply_template(link, {"crossSectionScale": REMOVE})   # delete a key
```

### Check a style — are these links already uniform?

<!-- TODO same comments as the above about whether to just have one functional interface -->
```python
report = style.check(link)                 # planned -> StyleReport
report.ok                                  # bool: does the state already match the style?
report.mismatches                          # {property: (expected, actual)} for what diverges

reports = style.check_all(links)           # planned — one report per link
all(r.ok for r in reports)                 # is the whole batch uniform?
```

Checking is strict: a property matches only when it is explicitly present and equal.
It is the read-only counterpart of `apply` — applying a style and then checking against
it always passes.

### Render one or more links with a style

```python
render(link, "fig.png", style=style)       # one-shot browser session

render_all(                                # planned — one browser session for the batch
    {link_a: "a.png", link_b: "b.png"},
    style=style,
)
```

For finer control over a long batch, drive the session directly:

```python
from ngsnap import RenderSession

with RenderSession() as session:           # browser starts once (P11)
    session.render(link_a, "a.png", style=style)
    session.render(link_b, "b.png", style=style)
```

### Cache keys

```python
key = cache_key(link, style)               # planned — stable string over state + style (P7)
```

Callers own the cache; `cache_key` just gives a deterministic key so unchanged
inputs can skip rendering.

## CLI

> **Target API.** The CLI is a thin wrapper over the Python API above and does not exist
> yet; this is the intended command surface.

```
# Render one or more links with a style.
ngsnap render <url-or-file>... -o fig.png [--style s.toml] [--timeout 60]

# Apply a style and emit the restyled states (uniform links/JSON), no browser.
ngsnap apply  <url-or-file>... [--style s.toml] [--url | --json]

# Check whether links already conform to a style; exit non-zero if any diverge.
ngsnap check  <url-or-file>... [--style s.toml] [--strict]

# Generate a new style from a link by extracting a named setting group.
ngsnap extract <url-or-file> [--group cosmetic] -o style.toml

# Ad-hoc templating without a Style; print the new state as a URL or JSON.
ngsnap template <url-or-file> --set showAxisLines=false [--url | --json]

# Stable cache key over state + style.
ngsnap key <url-or-file> [--style s.toml]

# Render many links from a manifest through one browser session.
ngsnap batch <manifest.json> [--style s.toml]
```

Every command accepts a link, a JSON file, or `-` for JSON on stdin, so the tool
composes in shell pipelines and site builds.

## Installation

The render engine needs the `render` extra (pinned Chrome for Testing via Selenium):

```
uv sync --extra render      # or: pip install "ngsnap[render]"
```

Selenium Manager downloads the pinned Chrome-for-Testing build on first render, so no
system Chrome is required. To provision it ahead of time (one step, no `apt`, no `xvfb`):

```
just install-browser
# or: uv run python -c "from ngsnap.render import install_browser; install_browser()"
```

- **CI (`ubuntu-latest`):** `uv sync --extra render` then the provision command above. The
  runner already has the shared libraries Chrome needs; the render engine runs headless with
  software WebGL2 (no GPU, no display).
- **Local macOS (Apple Silicon):** identical — Selenium Manager fetches the `mac-arm64`
  Chrome-for-Testing build, so local renders match CI.

Define your own style by copying [src/ngsnap/styles/default.toml](src/ngsnap/styles/default.toml)
and pointing `Style.from_file(...)` at it.