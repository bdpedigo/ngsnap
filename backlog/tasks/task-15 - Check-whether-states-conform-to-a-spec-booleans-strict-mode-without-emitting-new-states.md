---
id: TASK-15
title: >-
  Check whether states conform to a spec (booleans, strict mode) without
  emitting new states
status: To Do
assignee: []
created_date: '2026-09-22 23:39'
labels: []
dependencies:
  - TASK-4
  - TASK-14
references:
  - design.md
priority: medium
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Maintainers want to verify that a set of Neuroglancer links is already uniform in some properties, for example that a batch of links all share the same appearance settings, without producing new states. This is the read-only counterpart to applying a style/template: given a spec expressed the same way a style TOML expresses what to apply, report booleans about whether each state already matches, instead of returning modified states. It should reuse the same deep-merge/templating comparison machinery used to modify state (TASK-4), differing only in the terminal action: compare-and-report instead of write. A known challenge is that Neuroglancer defaults are not known to the package, so a state can match a spec by omission (relying on a client default) in ways we cannot reason about reliably. Start with a strict mode that refuses to lean on defaults: a property matches only if it is explicitly present in the state and equal to the spec. The feature must be idempotent with the apply/extract features (TASK-5, TASK-14): a state produced by applying spec S must check True against S.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Given a state and a spec (same TOML/template shape used to apply a style), the package reports whether the state already matches the spec, as booleans, without emitting a new state
- [ ] #2 Reports per-property results and an overall pass/fail, so a caller can see which properties diverge
- [ ] #3 Accepts multiple states (batch) and reports conformance per state
- [ ] #4 Strict mode: a property matches only when it is explicitly present in the state and equal to the spec; a missing property is non-conforming and Neuroglancer client defaults are never assumed
- [ ] #5 Idempotent with apply: for any state and spec, applying the spec and then checking against the same spec returns all-matching (check after apply is always True)
- [ ] #6 Reuses the existing deep-merge/templating comparison and key addressing (nested keys and per-layer-by-name, as in apply_template) rather than a parallel implementation
- [ ] #7 Default-aware (non-strict) checking is explicitly out of scope for now and documented as a follow-up, since client defaults are unknown to the package
- [ ] #8 Tests cover a conforming state, a non-conforming state, batch input, and the apply-then-check idempotence property
<!-- AC:END -->
