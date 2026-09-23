---
id: TASK-14
title: >-
  Setting groups: classify a deployment's state properties and extract a group
  from a state into a reusable style TOML
status: Done
assignee:
  - '@ben'
created_date: '2026-09-22 23:39'
updated_date: '2026-09-23 18:56'
labels: []
dependencies:
  - TASK-5
  - TASK-16
references:
  - design.md
priority: medium
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Authors want to reuse the "look" of a curated Neuroglancer link across many new links without hand-copying settings. Today a spec (TASK-16) is authored by hand in TOML, and there is no shared vocabulary for which state properties are appearance vs sources vs selection vs camera for the deployments the team uses. Because of that there is also no way to lift, say, all the appearance settings out of an existing good-looking state and save them for later application. This task introduces named setting groups for the current NGL deployment and an extract operation (`Spec.from_state`) that pulls a chosen group out of a given state and writes it as a spec TOML that `Spec.from_file` can load and apply through the existing templating path. It builds on the same parse (TASK-3) and templating/Spec (TASK-4, TASK-16) machinery rather than inventing a second mechanism; the extracted TOML is just a spec authored automatically from a source state instead of by hand.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A documented, deployment-scoped classification maps Neuroglancer state properties into named groups covering at least appearance, sources, selection, and camera
- [x] #2 Given a state (link, JSON, file, or dict) and a group name, the package returns the subset of that state that belongs to that group
- [x] #3 The extracted subset can be written to a spec TOML (template/config sections) that `Spec.from_file` loads and applies via the existing templating interface, no new merge mechanism
- [x] #4 An appearance extraction excludes non-appearance properties such as sources/layer sources, selected objects, and camera/position
- [x] #5 Round trip is idempotent: applying the extracted TOML to the source state reproduces the extracted group of properties
- [x] #6 Properties that are not classified into any group are handled in a documented, predictable way (dropped or flagged, not silently mixed in)
- [x] #7 Tests cover extracting the appearance group from a representative multi-layer state and the extract-then-apply round trip
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add src/ngsnap/groups.py: a deployment-scoped SettingGroup classification (appearance, sources, selection, camera) over top-level and per-layer Neuroglancer JSON keys, plus extract_group(state, group) that lifts a group into a template dict (per-layer props keyed by layer name), dropping unclassified properties.
2. Add Spec.from_state(source, group) that parses the state (TASK-3) and returns a Spec whose template is the extracted group; add Spec.to_toml()/Spec.to_file() serialization using a TOML writer (tomli-w dep) so Spec.from_file can reload it.
3. Export group names/helpers from ngsnap package __init__.
4. Document the classification and drop-unclassified behavior in design.md as a RESOLVED decision.
5. Tests: extract appearance from a representative multi-layer state (excludes sources/segments/camera/position), extract-then-apply round-trip idempotency, unknown-group error, unclassified-dropped.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added ngsnap.groups (SettingGroup + GROUPS: appearance/sources/selection/camera classification over top-level and per-layer JSON keys) and extract_group(state, group). Added Spec.from_state(source, group), Spec.to_toml(), Spec.to_file() (tomli-w dep). Exported GROUPS/SettingGroup/extract_group. Documented classification + drop-unclassified behavior in design.md. New tests in tests/test_groups.py cover appearance extraction from a multi-layer state, group partitioning, unclassified-dropped, unknown-group error, round-trip idempotency, and TOML reload/apply. Full suite: 62 passed; ruff + mypy clean.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Introduced deployment-scoped setting groups (ngsnap.groups: appearance/sources/selection/camera) classifying top-level and per-layer Neuroglancer JSON keys, plus extract_group() and Spec.from_state(source, group) that lift a group into a spec template through the existing templating path. Added Spec.to_toml()/to_file() (tomli-w) so an extracted spec reloads via Spec.from_file. Unclassified properties are dropped, not mixed in. Documented in design.md. Verified by tests/test_groups.py (appearance extraction from a multi-layer state, group partitioning, unclassified-dropped, unknown-group error, extract-then-apply idempotency, TOML reload+apply); full suite 62 passed, ruff + mypy clean.
<!-- SECTION:FINAL_SUMMARY:END -->
