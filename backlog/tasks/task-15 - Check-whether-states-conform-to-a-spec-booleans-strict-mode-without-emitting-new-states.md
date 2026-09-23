---
id: TASK-15
title: >-
  Check whether states conform to a spec (booleans, strict mode) without
  emitting new states
status: To Do
assignee: []
created_date: '2026-09-22 23:39'
updated_date: '2026-09-23 18:26'
labels: []
dependencies:
  - TASK-4
  - TASK-16
references:
  - design.md
priority: medium
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Maintainers want to verify that a Neuroglancer link already matches a spec in some properties - for example that a link already carries the house appearance - without producing a new state. This is the read-only counterpart to `apply`: given a spec (a `Spec`, a mapping, or a TOML path, the same thing `apply` takes), report whether the state already matches instead of returning a modified state. It reuses the same deep-merge/templating comparison used to modify state (TASK-4), differing only in the terminal action: compare-and-report instead of write. `check(source, spec)` returns a report that is truthy when the state matches and carries per-property mismatch detail. A known challenge is that Neuroglancer defaults are not known to the package, so a state can match a spec by omission (relying on a client default) in ways we cannot reason about reliably. Start with a strict mode that refuses to lean on defaults: a property matches only if it is explicitly present in the state and equal to the spec. The feature must be idempotent with apply/extract (TASK-16, TASK-14): a state produced by applying spec S must check truthy against S. Multiple-input batch is out of scope for now (single input), matching the settled single-IO API.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 check(source, spec) reports whether the state already matches the spec without emitting a new state; spec is a Spec, a mapping, or a TOML path, as apply accepts
- [ ] #2 The returned report is truthy when the state matches and exposes per-property results plus an overall pass/fail, so a caller can see which properties diverge
- [ ] #3 Strict mode: a property matches only when it is explicitly present in the state and equal to the spec; a missing property is non-conforming and Neuroglancer client defaults are never assumed
- [ ] #4 Idempotent with apply: for any state and spec, applying the spec and then checking against the same spec returns a truthy (all-matching) report
- [ ] #5 Reuses the existing deep-merge/templating comparison and key addressing (nested keys and per-layer-by-name) rather than a parallel implementation
- [ ] #6 Default-aware (non-strict) checking is explicitly out of scope for now and documented as a follow-up, since client defaults are unknown to the package
- [ ] #7 Tests cover a conforming state, a non-conforming state with mismatch detail, and the apply-then-check idempotence property
<!-- AC:END -->
