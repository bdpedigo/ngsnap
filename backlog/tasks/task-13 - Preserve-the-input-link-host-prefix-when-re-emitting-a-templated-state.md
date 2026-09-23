---
id: TASK-13
title: Preserve the input link host prefix when re-emitting a templated state
status: Done
assignee:
  - '@copilot'
created_date: '2026-09-22 22:27'
updated_date: '2026-09-23 16:19'
labels: []
milestone: m-1
dependencies:
  - TASK-4
references:
  - design.md
modified_files:
  - src/ngsnap/template.py
  - tests/test_template.py
  - design.md
priority: medium
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
parse_state keeps only the state fragment and discards the host, so the result of apply_template emits URLs against the default host. For the headline P15 use case (restyle a link and hand it back for a paper or talk), round-tripping a link silently changes its deployment host, e.g. spelunker.cave-explorer.org becomes neuroglancer-demo.appspot.com. When the input is a Neuroglancer URL, the templated result should re-emit against the same host by default, while still allowing an explicit override. A design decision is open: where the prefix is captured and stored (a field on TemplatedState, something surfaced by the parse flow, or elsewhere) and whether parse_state/to_url should expose it too. The CLI template command (TASK-11) should consume this so it preserves host from day one.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 When the input to apply_template is a Neuroglancer URL, the templated result to_url() defaults to the same scheme, host, and path (everything before the fragment) as the input
- [x] #2 An explicit prefix passed to to_url() overrides the preserved prefix
- [x] #3 For inputs without a host (dict, JSON string, file, ViewerState), to_url() falls back to the documented default prefix
- [x] #4 Existing templating and to_url round-trip behavior is unchanged, including deterministic canonical output
- [x] #5 Where the input prefix is captured and stored is decided and recorded (design.md or code) with the alternatives that were considered
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add focused template tests for preserving an input URL prefix, overriding it explicitly, and falling back for non-URL inputs.
2. Capture the pre-fragment URL prefix in apply_template and store it as provenance on TemplatedState while leaving parse_state unchanged.
3. Record the API-placement decision and rejected alternatives in design.md.
4. Run focused tests, then the full test suite and project checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented URL-prefix provenance on TemplatedState, added preservation/override/fallback tests, and recorded the design decision. Focused validation: uv run pytest tests/test_template.py (13 passed).

Final validation passed:
- uv run pytest tests/test_template.py: 13 passed
- uv run pytest: 46 passed, 5 browser tests deselected
- uv run ruff check src/ngsnap/template.py tests/test_template.py: passed
- uv run ruff format --check src/ngsnap/template.py tests/test_template.py: passed
- uv run mypy src: passed
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Preserved the input Neuroglancer URL prefix as TemplatedState provenance while retaining explicit override and default-prefix behavior. Added coverage for URL and all hostless input forms, documented the design alternatives, and verified with 46 non-browser tests, Ruff, and mypy.
<!-- SECTION:FINAL_SUMMARY:END -->
