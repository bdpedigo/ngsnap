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
| P4 | Runtime per image is bounded and predictable enough to run inside a site build without exhausting CI time. Target (set by the TASK-1 spike): <= 30 s wall-clock per image cold on `ubuntu-latest` at 1600x1200, < 1 s for subsequent renders that reuse the browser session, default per-image timeout 60 s. | Must |
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

- **Render backend (RESOLVED 2026-09-22):** the headless-browser approach is viable. The TASK-1 spike rendered a public MICrONS state (2D EM + 3D mesh) to PNG on GitHub Actions `ubuntu-latest` with no GPU and no display, using software WebGL2 (ANGLE/SwiftShader). All three candidate drivers worked — Chrome/Selenium, Firefox-under-xvfb, and Playwright-Chromium — and each produced byte-identical renders across runs (P6). Default backend is **Chrome for Testing via Selenium**, with the browser build pinned (Selenium Manager auto-downloads a fixed Chrome-for-Testing version for both linux-x64 and mac-arm64) so renders are reproducible and local dev on Apple Silicon matches CI; Firefox-under-xvfb is a fallback. The `neuroglancer` README note about broken headless WebGL is stale for this runner. Full results and rationale are in the backlog document "Render backend research" (doc-1).
- **Style specification:** what format (TOML/YAML/Python object) and how much of the Neuroglancer state does style override vs. respect?
- **Template shape:** how does a template name the elements to swap? Candidates: a partial state dict merged over the input, JSON-pointer paths, or a small set of named knobs. It must handle both the viewer state (layout, axis lines, background) and the client config state (UI controls, panel borders, scale bar options, image size), because Neuroglancer keeps those in separate objects.
- **Package name.**

---

## 7. Next Steps

1. **Render spike:** on a GitHub Actions `ubuntu-latest` runner, render a representative Neuroglancer state to PNG via a headless browser. Record: does it work, image quality, wall-clock time, install complexity. Outcome drives P3, P4, and the backend decision.
2. Pick a name.