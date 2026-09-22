---
id: TASK-3
title: >-
  Parse and normalize Neuroglancer state input from link, JSON text, file, or
  dict
status: Done
assignee:
  - '@ben'
created_date: '2026-09-22 19:31'
updated_date: '2026-09-22 21:55'
labels: []
milestone: m-1
dependencies: []
priority: high
type: feature
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every entry point in the package (render, cache key, templating, CLI) takes "a Neuroglancer link or JSON state" (P2). Blog authors paste links from several Neuroglancer hosts (neuroglancer-demo.appspot.com, spelunker, institute deployments), and links use Neuroglancer's URL-safe JSON variant with single quotes and underscores. Some links carry a `#!` fragment with inline JSON, others point at a JSON state URL. A single normalization step keeps that mess out of every other module and gives the cache key a canonical input.

The `neuroglancer.url_state` module already parses fragments and round-trips to URLs, so this task is a thin, well-tested layer over it that also handles file paths, raw JSON strings, and Python dicts, and produces one consistent error type for bad input (P8).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A single public function accepts a Neuroglancer URL, a JSON string, a path to a JSON file, a dict, or a neuroglancer ViewerState and returns a ViewerState
- [x] #2 URLs from at least three different Neuroglancer host prefixes parse to the same state when they carry the same fragment
- [x] #3 Links whose fragment is a URL to a remote JSON state are either fetched or rejected with a clear error, and the choice is documented
- [x] #4 Malformed input raises one package-specific exception with a message that names what was wrong
- [x] #5 A state can be encoded back to a URL with a configurable host prefix, and parse then encode then parse round-trips to an equal state
- [x] #6 Unit tests cover each input kind and each failure mode without a browser
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add src/ngsnap/errors.py: NgsnapError base + StateInputError(NgsnapError) as the single package-specific exception for bad state input (AC#4).
2. Add src/ngsnap/state.py:
   - parse_state(source) -> ViewerState, the single public normalization entry (AC#1). Dispatch on type: ViewerState (returned as-is), Mapping/dict, pathlib.Path (file), str (URL vs inline JSON vs file path).
   - str dispatch: scheme://... => URL; starts with '{' => JSON string; else => treated as file path.
   - URL handling reads only the fragment via neuroglancer.url_state, so three different host prefixes with the same fragment yield equal states (AC#2).
   - Remote-state fragments (fragment is a URL): public http(s) json_url is fetched now via urllib (http/https only, with timeout); auth-backed refs (middleauth+, gs://, other schemes) raise StateInputError naming the problem and documenting the future caveclient+token path (AC#3).
   - to_url(source, prefix=DEFAULT_PREFIX) -> str: normalize then encode with configurable host prefix (AC#5).
   - All malformed input (bad JSON, missing file, unfetchable/JSON-invalid remote, unsupported type, non-http scheme) wrapped in StateInputError with a message naming what was wrong (AC#4).
3. Export parse_state, to_url, StateInputError, NgsnapError from src/ngsnap/__init__.py.
4. Add tests/test_state.py covering each input kind (URL, JSON string, file, dict, ViewerState), multi-host equality, remote fetch (mocked, no network), auth-backed rejection, round-trip parse->to_url->parse equality, and each failure mode. No browser/network in tests (AC#6).
5. Run just lint/format/typecheck/test; iterate to green.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented in src/ngsnap/state.py (parse_state, to_url) + src/ngsnap/errors.py (NgsnapError, StateInputError), exported from ngsnap package. parse_state dispatches on type: ViewerState (identity), Mapping/dict, pathlib.Path (file), str (scheme:// or #! => URL; { or [ => JSON string; else => file path). URL parsing reads only the fragment via neuroglancer.url_state, so different hosts with the same fragment yield equal states. Remote-state decision (per user): public http(s) json_url fragments are fetched now via urllib (http/https only, 30s timeout); auth-backed refs (middleauth+, gs://, other schemes) raise StateInputError naming the problem, with a NOTE documenting the future caveclient+token feature. All bad input raised as StateInputError with a message naming the fault. Verified with 18 passing tests in tests/test_state.py (each input kind, 3-host equality, mocked public fetch, network-error and non-JSON fetch failures, auth-backed rejection, custom-prefix round-trip, and each failure mode) plus tests/test_import.py. All browser/network-free (fetch mocked via monkeypatch). Full suite green: ruff check (All checks passed), ruff format (5 files unchanged), mypy src (no issues; added [[tool.mypy.overrides]] ignore_missing_imports for neuroglancer.*), pytest (18 passed).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added a thin normalization layer over neuroglancer.url_state: parse_state(source) -> ViewerState accepting a Neuroglancer URL, JSON string, JSON file path, dict, or ViewerState, and to_url(source, prefix) for the inverse with a configurable host prefix. Introduced NgsnapError/StateInputError as the single package-specific error for all bad input. Remote-state fragments: public http(s) json_url is fetched via urllib now; auth-backed (middleauth+/gs://) is rejected with a clear error and a documented future caveclient+token path. Verified with 18 tests (all input kinds, 3-host fragment equality, mocked public fetch, fetch failures, auth-backed rejection, custom-prefix parse->encode->parse round-trip, every failure mode) plus lint/format/typecheck all green.
<!-- SECTION:FINAL_SUMMARY:END -->
