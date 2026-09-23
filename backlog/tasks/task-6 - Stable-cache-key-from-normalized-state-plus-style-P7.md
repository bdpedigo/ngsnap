---
id: TASK-6
title: Stable cache key from normalized state plus spec (P7)
status: To Do
assignee: []
created_date: '2026-09-22 19:32'
updated_date: '2026-09-23 18:25'
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
- [ ] #1 A public cache_key(source, spec) function returns a short string that is stable across Python processes and platforms
- [ ] #2 Two links with the same state but different host prefixes, key order, or URL-safe quoting produce the same key
- [ ] #3 Changing any state element that the spec does not override, or changing the spec, changes the key
- [ ] #4 The key format and what goes into it are documented, including whether and how engine version is included
<!-- AC:END -->
