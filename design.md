# Neuroglancer Image Package — Requirements

**Status:** Draft, in progress **Package name:** ngsnap **Related:**

---

## 1. Purpose

A standalone Python package that turns a Neuroglancer state into a consistently styled static image. The immediate driver is the Neuroddities blog, where authors paste Neuroglancer links into markdown and the site build needs to turn those into figures automatically. The package should also be useful on its own for papers, talks, documentation, and other sites, so nothing in it should assume the blog.

## 2. Scope

**In scope**

- Accepting a Neuroglancer link (URL with encoded state) or a raw JSON state.
- Producing a static raster image of that state.
- Applying an opinionated, configurable house style to the render.
- Running unattended in CI.

**Out of scope**

- Managing a cache of rendered images (callers do this; the package just makes cache keys possible).
- Anything blog-specific: markdown parsing, badge rendering, site integration.
- Generating Neuroglancer states from scratch, or general-purpose state editing beyond the templated element swaps in P15.

---

## 3. Functional Requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| P1 | Standalone Python package in its own repo, published (PyPI or equivalent) so consumers can install it as a dependency. | Must |
| P2 | Input: a Neuroglancer link or JSON state. Output: a static image file (PNG). Other formats not required. | Must |
| P14 | Renders whatever view the state specifies — any layout, layer type, or view mode Neuroglancer itself supports (2D cross-sections, 3D meshes, multi-panel layouts, annotations, etc.). The package does not restrict to a subset of view types. | Must |
| P5 | Consistent visual style applied by the package, not left to the input state: framing/zoom rules, background, scale bar, color conventions, layer visibility defaults, resolution/aspect ratio. Style is configurable but ships with a single opinionated default. | Must |
| P8 | Fails loudly with an actionable error (bad link, unreachable data source, timeout) rather than emitting a blank or partial image. | Must |
| P9 | Usable both as a Python API and a CLI, so callers can integrate however suits them. | Should |
| P10 | Handles the datasets/data sources the team actually uses, including authentication where required. Credentials come from the environment (e.g. env vars), never baked in or written to disk by the package. | Must |
| P11 | Can render multiple states in one invocation (batch), amortizing browser or engine startup when there are several images to make. | Nice-to-have |
| P15 | State templating is a public interface, not an internal detail. Given a Neuroglancer state (link or JSON) and a template that names specific elements to replace, return a new state with only those elements changed. Callers can use this without rendering anything, for example to produce a restyled link. The render path uses the same interface to apply the house style (P5). | Must |

## 4. Operational Requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| P3 | Renders headlessly with no display and no GPU, so it runs on a standard CI runner (e.g. GitHub Actions `ubuntu-latest`). | Must |
| P4 | Runtime per image is bounded and predictable enough to run inside a site build without exhausting CI time. Concrete target to be set after the render spike. | Must |
| P6 | Deterministic: the same state and style config produce the same image, so cache keys are stable and re-renders are reproducible. | Must |
| P7 | Exposes a stable cache key derived from state + style config (or documents how callers should compute one), so callers can skip rendering for unchanged inputs. | Should |
| P12 | Installable with minimal system dependencies. If a headless browser is required, installation of it should be scripted or documented for CI. | Should |
| P13 | Clear logging at a configurable level, so failures in CI are diagnosable from logs alone. | Should |

*(IDs are kept stable across documents rather than renumbered by section.)*

---

## 5. Interface Sketch (non-binding)

Illustrative only; the real API follows from the spike.

```python
from ngsnap import render, cache_key, Style, apply_template, to_url

style = Style.default()                 # or Style.from_file("neuroddities.toml")
key = cache_key(state_or_url, style)    # stable string
render(state_or_url, "out/fig.png", style=style, timeout=60)

# P15: templating on its own, no browser involved
new_state = apply_template(state_or_url, {"layout": "3d", "showAxisLines": False})
print(to_url(new_state))                # restyled link
```

```
ngsnap render <url-or-state.json> -o fig.png [--style neuroddities.toml]
ngsnap key <url-or-state.json> [--style ...]
ngsnap batch manifest.json
ngsnap template <url-or-state.json> --set layout=3d [--style ...]   # prints new URL or JSON
```

---

## 6. Open Questions

- **Render backend:** headless browser driving real Neuroglancer (highest fidelity, heavy dependency) vs. a re-implementation of the rendering (light, but drifts from what users see in the viewer). P14 makes a re-implementation impractical, so the spike should focus on the headless-browser approach and confirm it is viable.
- **Style specification:** what format (TOML/YAML/Python object) and how much of the Neuroglancer state does style override vs. respect?
- **Template shape:** how does a template name the elements to swap? Candidates: a partial state dict merged over the input, JSON-pointer paths, or a small set of named knobs. It must handle both the viewer state (layout, axis lines, background) and the client config state (UI controls, panel borders, scale bar options, image size), because Neuroglancer keeps those in separate objects.
- **Render backend findings (2026-09-22):** the `neuroglancer` Python package already provides `Viewer.screenshot()`, which waits for all chunks to load before returning a PNG, and `neuroglancer.tool.screenshot`, which adds tiling and UI hiding. The browser only opens the viewer URL. Neuroglancer's README states that Chrome headless fails on Swiftshader bugs and Firefox headless lacks WebGL. Their CI uses Firefox under xvfb on ubuntu-latest. The spike must test whether that note still holds. See the backlog document "Render backend research".
- **Package name.**

---

## 7. Next Steps

1. **Render spike:** on a GitHub Actions `ubuntu-latest` runner, render a representative Neuroglancer state to PNG via a headless browser. Record: does it work, image quality, wall-clock time, install complexity. Outcome drives P3, P4, and the backend decision.
2. Pick a name.