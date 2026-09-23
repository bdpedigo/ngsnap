---
id: TASK-6
title: Stable cache key from normalized state plus spec (P7)
status: Done
assignee:
  - '@claude'
created_date: '2026-09-22 19:32'
updated_date: '2026-09-23 19:18'
labels: []
milestone: m-1
dependencies:
  - TASK-4
  - TASK-16
priority: medium
type: feature
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The blog build renders many figures and must skip the ones whose inputs did not change. Design.md keeps cache management out of scope but requires that the package expose a stable key (P7) so callers can implement their own cache. The key has to be a pure function of the templated state and the spec, with no dependence on dict ordering, float formatting, the host prefix of the link, or the package version unless the rendering actually changed. This depends on the canonical serialization from the templating task. One design question to settle: whether the key includes a render-engine version component so that a browser or neuroglancer upgrade that changes pixels invalidates old images.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A public cache_key(source, spec) function returns a short string that is stable across Python processes and platforms
- [x] #2 Two links with the same state but different host prefixes, key order, or URL-safe quoting produce the same key
- [x] #3 Changing any state element that the spec does not override, or changing the spec, changes the key
- [x] #4 The key format and what goes into it are documented, including whether and how engine version is included
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add public cache_key(source, spec=None) in spec.py: coerce spec, apply it to the normalized source, and hash the canonical applied viewer-state JSON (TemplatedState.to_json) combined with the canonical spec JSON (Spec.to_json) using sha256; return a short hex string.
2. Base the key on the APPLIED state so elements the spec overrides do not affect the key (only non-overridden state + the spec matter), and drop host prefix by hashing only the viewer_state. Do NOT include an engine/package version component by default; document that callers namespace their cache by engine version if a browser/neuroglancer upgrade changes pixels.
3. Export cache_key from ngsnap/__init__.py.
4. Add tests/test_cache.py: stability across calls, prefix/key-order/quoting invariance, non-overridden element changes the key, overridden element does NOT change the key, spec change changes the key, short-string shape.
5. Document the key format, inputs, and engine-version decision in design.md (P7 resolution).
6. Run pytest, ruff, mypy.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added cache_key(source, spec=None) in ngsnap.spec (exported from the package): a SHA-256 hex key (32 chars) over two canonical JSON inputs — the APPLIED viewer state (spec merged over the normalized source via TemplatedState.to_json, sorted keys, host prefix dropped) and Spec.to_json (template+config+respects, sorted). Hashing the applied state makes elements the spec overrides irrelevant to the key while any non-overridden state element or any spec change alters it. Engine/package version is intentionally excluded (key identifies inputs, not the renderer); callers namespace their cache by engine version if a pixel-changing upgrade needs invalidation. Documented in design.md (Cache key RESOLVED). Verified by tests/test_cache.py: short hex shape, cross-call stability, host-prefix/key-order/URL-quoting invariance (AC#2), non-overridden element and spec template/config changes flip the key while an overridden element does not (AC#3). Full suite 72 passed, ruff + mypy clean.
<!-- SECTION:FINAL_SUMMARY:END -->
