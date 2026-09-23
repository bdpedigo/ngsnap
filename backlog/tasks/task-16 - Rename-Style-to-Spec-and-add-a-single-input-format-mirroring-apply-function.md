---
id: TASK-16
title: 'Rename Style to Spec and add a single-input, format-mirroring apply function'
status: Done
assignee:
  - '@ben'
created_date: '2026-09-23 18:25'
updated_date: '2026-09-23 18:43'
labels: []
milestone: m-1
dependencies:
  - TASK-4
  - TASK-5
  - TASK-8
references:
  - design.md
  - README.md
type: feature
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The settled public-API decisions (design.md, 2026-09-23) make the headline surface a `Spec` (renamed from `Style`) with a single-input, format-mirroring `apply(source, spec)` that returns the restyled result in the same shape as its input (link to link, JSON to JSON), so callers never have to reason about a `TemplatedState`. Today the shipped code exposes `Style`, a `Style.apply` that returns a `TemplatedState`, and `apply_template`; this task renames the type and adds the simpler free function so downstream tasks (TASK-6 cache_key, TASK-14 extract, TASK-15 check, TASK-11 CLI) build on stable names. A `spec` may be a `Spec`, a plain mapping, or a TOML path (an anonymous spec). `TemplatedState`, `RenderSession`, and `apply_template` stay available as lower-level, unadvertised escape hatches and keep their current behavior. Multiple-input batch (apply_all, render_all) is out of scope for now.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Spec is the public type (with Spec.default() and Spec.from_file()); Style is no longer part of the public API
- [x] #2 apply(source, spec) returns the restyled state in the same shape as its input: a URL string returns a URL string with the host prefix preserved, and a JSON/dict/ViewerState returns JSON
- [x] #3 spec accepts a Spec, a plain mapping, or a TOML path, all routed through the existing templating deep-merge, with the REMOVE sentinel and per-layer-by-name addressing still working
- [x] #4 render and the render session take the spec through a spec= parameter, replacing style=
- [x] #5 TemplatedState, RenderSession, and apply_template remain importable with unchanged behavior but are not the headline API
- [x] #6 Tests cover the format-mirroring of apply (URL in gives URL out, JSON in gives JSON out) and are updated to the Spec and spec= names
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Rename module src/ngsnap/style.py -> spec.py (git mv) and class Style -> Spec; rename errors.StyleError -> SpecError. Keep styles/default.toml path as-is (internal resource, not public API).
2. Add a top-level free function apply(source, spec) in spec.py that is format-mirroring: URL string in -> restyled URL string (prefix preserved via TemplatedState.to_url), JSON string in -> canonical JSON string, and Mapping/ViewerState/Path/filename in -> restyled JSON dict. Config (render-only) is intentionally dropped from apply output.
3. Add _coerce_spec(spec) accepting Spec | Mapping (anonymous template) | str/Path (TOML file); keep Spec.apply(source) -> TemplatedState as the lower-level method the render path and free apply both use.
4. Add state.looks_like_url(text) helper (refactor parse_state to use it) so apply can classify string inputs without duplicating the scheme regex.
5. render() and RenderSession.render() take spec= (replacing style=) and coerce via _coerce_spec; default None -> Spec.default().
6. Update __init__.py exports: Spec, apply, SpecError in; Style, StyleError out. Keep TemplatedState, apply_template, RenderSession, REMOVE, parse_state, to_url as unadvertised lower-level API.
7. Update tests: rename test_style.py -> test_spec.py (Spec/SpecError, keep TemplatedState assertions via Spec.apply); add apply format-mirroring tests (url->url, json->json, dict->dict, anonymous-dict spec, toml-path spec). Update test_render.py, test_render_browser.py, scripts/render_readme_example.py to Spec/spec=.
8. Run just check (lint, format, typecheck, unit tests).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Renamed src/ngsnap/style.py -> spec.py and tests/test_style.py -> test_spec.py (git mv). Class Style -> Spec; errors.StyleError -> SpecError. Added state.looks_like_url() and refactored parse_state to use it. Added free apply(source, spec) in spec.py (format-mirroring: URL->URL prefix-preserved, JSON str->JSON str, mapping/ViewerState/file->dict; render-only config dropped) plus _coerce_spec (Spec | Mapping | str/Path TOML) and type SpecInput. render()/RenderSession.render() take spec= via _coerce_spec (was style=). __init__ exports Spec, apply, SpecError; TemplatedState, apply_template, RenderSession, REMOVE kept as lower-level. Updated test_render.py, test_render_browser.py, scripts/render_readme_example.py. Kept styles/default.toml path as-is (internal resource). just check: ruff+format+mypy clean, 52 unit tests pass (5 browser deselected, not run locally).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Renamed Style->Spec (module style.py->spec.py, StyleError->SpecError) and added a single-input, format-mirroring free function apply(source, spec): URL->URL with host prefix preserved, JSON string->JSON string, mapping/ViewerState/file->JSON dict, with render-only config dropped. spec accepts a Spec, a plain mapping, or a TOML path via _coerce_spec; render()/RenderSession.render() now take spec=. TemplatedState/apply_template/RenderSession/REMOVE remain as lower-level API. Verified with just check (ruff, ruff format, mypy clean; 52 unit tests pass, 5 browser deselected) and a scripted import/behavior check confirming Spec present, Style/StyleError absent, and REMOVE working through apply.
<!-- SECTION:FINAL_SUMMARY:END -->
