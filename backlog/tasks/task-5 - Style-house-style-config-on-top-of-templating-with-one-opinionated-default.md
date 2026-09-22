---
id: TASK-5
title: 'Style: house-style config on top of templating, with one opinionated default'
status: In Progress
assignee: []
created_date: '2026-09-22 19:32'
updated_date: '2026-09-22 22:41'
labels: []
milestone: m-1
dependencies:
  - TASK-4
  - TASK-1
references:
  - design.md
priority: high
type: feature
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Requirement P5 says the package, not the input state, decides how a figure looks: framing and zoom rules, background, scale bar, color conventions, layer visibility defaults, resolution and aspect ratio. Without this, every blog figure inherits whatever the author's viewer happened to look like. Style must ship with a single opinionated default and be loadable from a file so other sites can define their own.

Style is a template (task-4) plus render-time settings, so this task should not invent a second override mechanism. Two open questions from design.md land here: the file format (TOML, YAML, or Python object) and how much of the input state a style overrides versus respects. Framing rules such as "fit the selected segments" or "keep the author's zoom" are the hard part, because Neuroglancer stores scale and position but not a bounding box. The render spike (task-1) tells us which settings, such as image size and scale bar, must live in the client config state.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A Style object exists with a default() constructor and a from_file() constructor, and the file format decision is recorded in design.md
- [x] #2 The default style hides Neuroglancer UI controls and panel borders, sets a fixed output size and aspect ratio, sets background colors, and sets scale bar visibility and size
- [x] #3 A style declares which state elements it overrides and which it respects, and a test shows an author's layer visibility surviving when the style says to respect it
- [x] #4 Applying a style to a state goes through the templating interface from task-4 and produces a viewer state plus config-state overrides
- [x] #5 Two styles that differ only in a render-time setting produce different canonical serializations, so the cache key can tell them apart
- [ ] #6 The default style is documented in the README with a rendered example once the render engine exists
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
POC implementation. Added src/ngsnap/style.py: frozen Style dataclass with default() (Python) and from_file() (TOML via stdlib tomllib) constructors, .apply() routing through apply_template (task-4), .overrides derived from template+config keys, .respects declaration, and .to_json() canonical serialization (template+config+respects) for cache keys. Added StyleError; exported Style + StyleError from ngsnap. Shipped src/ngsnap/styles/default.toml as a from_file example that round-trips to Style.default(). Default overrides UI/panel chrome + viewerSize [1600,1200] + backgrounds + scale bar; respects layer visible/segments, position, and cross-section/projection scales. File-format decision (TOML over YAML/Python object) recorded in design.md open questions. 10 tests in tests/test_style.py; full suite 39 passed; ruff + mypy clean. AC#6 (README rendered example) deferred: needs the render engine (task-8). Framing 'fit selected segments' deferred (no bbox in NG state); default respects author framing for now.
<!-- SECTION:NOTES:END -->
