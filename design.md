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
| P4 | Runtime per image is bounded and predictable enough to run inside a site build without exhausting CI time. Target (set by the TASK-1 spike): <= 30 s wall-clock per image cold on `ubuntu-latest` at 1600x1200, < 1 s for subsequent renders that reuse the browser session, default per-image timeout 60 s. **Browser CI job budget (TASK-9): <= 15 min on `ubuntu-latest`, covering the one-time pinned Chrome-for-Testing download plus the browser integration tests (5 renders); locally the browser suite runs in ~40 s once the browser is provisioned.** | Must |
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
- **Style specification (RESOLVED 2026-09-22):** a `Style` is task-4's two output objects declared up front — a viewer-state `template` and render-time `config` overrides — plus a `respects` list naming the state elements it deliberately leaves to the author. `Style.default()` is the single opinionated default in Python; `Style.from_file(path)` loads a **TOML** file with `[template]`, `[config]`, and a top-level `respects` array. TOML was chosen over YAML (needs a third-party parser; `tomllib` is stdlib) and over a Python object literal (not safe to load from arbitrary files, and not data-only). Applying a style goes through `apply_template`, so there is no second override mechanism. What it overrides vs. respects: the default **overrides** presentation — UI/panel chrome, output size, background colors, scale-bar visibility and size — and **respects** author intent — per-layer `visible` and `segments`, `position`, and the cross-section/projection scales (framing). `Style.to_json()` serializes template + config + respects canonically so two styles differing only in a render-time setting get different cache keys (P7). Deferred: framing rules that fit selected segments (design.md §6 "fit the selected segments"), which need a bounding box Neuroglancer does not store; the default respects the author's framing for now.
- **Template shape (RESOLVED 2026-09-22):** a template is a **partial dict deep-merged over the state's canonical JSON**. `apply_template(source, template, *, config=...)` takes viewer-state overrides in `template` and client config-state overrides in the keyword-only `config`, keeping the two Neuroglancer objects separate because only the viewer state is URL-encodable (P15). In `template`, mappings recurse, other values overwrite, a `REMOVE` sentinel deletes a key, and a `layers` mapping keyed by layer name patches/adds/removes individual layers. The result (`TemplatedState`) exposes the `ViewerState`, the config overrides separately, a canonical JSON string, and a Neuroglancer URL. Rejected alternatives: **JSON-pointer / path patches** (verbose and hard to read when setting many nested keys; deep-merge covers the same ground more ergonomically); **a fixed set of named knobs** like `neuroglancer.tool.screenshot.apply_state_modifications` (not general — can't reach arbitrary nested or per-layer properties, and every new knob needs code, violating P14/P15's "any element"); and **a single flat dict mixing viewer and config keys** (can't cleanly separate the two output objects and risks key collisions).
- **Input URL prefix (RESOLVED 2026-09-23):** `apply_template` captures an input URL's scheme, host, and path as provenance on `TemplatedState`; `TemplatedState.to_url()` preserves that prefix unless given an explicit override. Inputs without URL provenance use the existing Neuroglancer default. `parse_state` remains a normalization API returning `ViewerState`, and standalone `to_url` remains explicit about its prefix. Rejected alternatives: **returning a wrapper from `parse_state`** (breaks its public return type for metadata only templating needs) and **storing provenance outside the result** (hidden global or side-table state would make behavior non-local and fragile).
- **Package name.**

---

## 7. Next Steps

1. **Render spike:** on a GitHub Actions `ubuntu-latest` runner, render a representative Neuroglancer state to PNG via a headless browser. Record: does it work, image quality, wall-clock time, install complexity. Outcome drives P3, P4, and the backend decision.
2. Pick a name.