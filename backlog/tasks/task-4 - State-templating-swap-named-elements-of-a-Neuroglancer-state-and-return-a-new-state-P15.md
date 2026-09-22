---
id: TASK-4
title: >-
  State templating: swap named elements of a Neuroglancer state and return a new
  state (P15)
status: Done
assignee:
  - '@ben'
created_date: '2026-09-22 19:32'
updated_date: '2026-09-22 22:20'
labels: []
milestone: m-1
dependencies:
  - TASK-3
references:
  - design.md
priority: high
type: feature
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Taking a Neuroglancer state and replacing specific elements of it while leaving the rest alone is useful on its own, without any rendering: restyle a link for a paper, force a layout for a talk, turn off axis lines across a batch of links, or swap a data source. Requirement P15 in design.md makes this a public interface. The render path then uses the same interface to apply the house style, so style becomes "a template plus defaults" instead of a separate mechanism.

Two facts shape the design. First, Neuroglancer keeps knobs in two objects: the viewer state (in the link: layout, showAxisLines, background colors, scale, layer visibility) and the client config state (not in the link: showUIControls, showPanelBorders, viewerSize, scaleBarOptions). The template must be able to address both, and the output must keep them separate because only the viewer state can go back into a URL. Second, output must be deterministic and canonical (stable key order, no incidental reordering), because the cache key (P7) hashes it.

The open question in design.md is the template shape: partial dict merged over the input, path-based patches, or named knobs. Decide during the task and record the decision. `neuroglancer.tool.screenshot.apply_state_modifications` is a small existing example of the kind of overrides the template must express.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A public function takes a state (any input accepted by the parsing task) and a template and returns a new state; the input state object is not mutated
- [x] #2 The template can set, override, and remove top-level and nested viewer-state elements, including per-layer properties addressed by layer name
- [x] #3 The template can carry client config-state overrides (at minimum UI controls, panel borders, viewer size, scale bar options) and they are returned separately from the viewer state
- [x] #4 Elements not named by the template are unchanged, verified by a test that diffs input and output
- [x] #5 Applying the same template to the same state twice yields byte-identical canonical JSON
- [x] #6 The result can be emitted as a ViewerState, a canonical JSON string, or a Neuroglancer URL
- [x] #7 The template shape decision is recorded in design.md under Open Questions with the alternatives that were rejected
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Decide template shape: partial-dict deep-merged over the state's canonical JSON. Viewer-state overrides via a positional `template` mapping; client-config-state overrides via a keyword-only `config` mapping (kept separate because config is not URL-encodable). Per-layer addressing via a name->partial mapping under `layers`. A `REMOVE` sentinel deletes keys/layers. Record decision + rejected alternatives (JSON-pointer paths, fixed named knobs, single flat dict) in design.md Open Questions (AC7).
2. Implement src/ngsnap/template.py: apply_template(source, template=None, *, config=None) -> TemplatedState. Reuse parse_state; operate on state.to_json() so the input is never mutated (AC1). Deep-merge helper + special-cased layer merge by name (AC2). Validate config via neuroglancer ConfigState; return it separately on the result (AC3). Add StateTemplateError for actionable failures.
3. TemplatedState result: .viewer_state (ViewerState), .config (dict), .to_json() canonical sorted JSON string, .to_url(prefix) Neuroglancer URL (AC6). Canonicalization guarantees byte-identical output across repeated applies (AC5).
4. Export apply_template, TemplatedState, REMOVE, StateTemplateError from ngsnap.__init__.
5. Tests in tests/test_template.py: no-mutation + input/output diff (AC1/AC4), set/override/remove nested + per-layer (AC2), config separation (AC3), determinism byte-identical (AC5), emit as ViewerState/JSON/URL (AC6).
6. Record decision in design.md (AC7). Run just lint/format/typecheck/test.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented src/ngsnap/template.py (apply_template + TemplatedState + REMOVE sentinel) and StateTemplateError; exported from ngsnap. Template shape decision (partial-dict deep-merge, viewer vs config split, per-layer-by-name, REMOVE) recorded in design.md Open Questions with rejected alternatives (JSON-pointer paths, fixed named knobs, single flat dict). Verified: just lint (All checks passed), ruff format --check (7 files already formatted), mypy src (Success, no issues), pytest (29 passed). AC coverage in tests/test_template.py: AC1 test_input_state_not_mutated; AC2 top-level set/override/remove + per-layer override/add/remove; AC3 test_config_returned_separately; AC4 test_unnamed_elements_unchanged (input/output diff); AC5 test_deterministic_canonical_json (byte-identical); AC6 test_emit_as_viewer_state_json_and_url + test_url_round_trips_with_prefix.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added public state templating (src/ngsnap/template.py): apply_template(source, template, *, config) deep-merges a partial dict over the parsed state's canonical JSON without mutating the input, addresses per-layer properties by name, supports a REMOVE sentinel, and returns a TemplatedState exposing the ViewerState, separate client config-state overrides, a canonical JSON string, and a Neuroglancer URL. Config validated via neuroglancer ConfigState; errors surface as StateTemplateError. Recorded the template-shape decision and rejected alternatives in design.md. Verified with 29 passing pytest tests, ruff lint/format, and mypy.
<!-- SECTION:FINAL_SUMMARY:END -->
