---
id: TASK-13
title: Preserve the input link host prefix when re-emitting a templated state
status: To Do
assignee: []
created_date: '2026-09-22 22:27'
labels: []
milestone: m-1
dependencies:
  - TASK-4
references:
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
- [ ] #1 When the input to apply_template is a Neuroglancer URL, the templated result to_url() defaults to the same scheme, host, and path (everything before the fragment) as the input
- [ ] #2 An explicit prefix passed to to_url() overrides the preserved prefix
- [ ] #3 For inputs without a host (dict, JSON string, file, ViewerState), to_url() falls back to the documented default prefix
- [ ] #4 Existing templating and to_url round-trip behavior is unchanged, including deterministic canonical output
- [ ] #5 Where the input prefix is captured and stored is decided and recorded (design.md or code) with the alternatives that were considered
<!-- AC:END -->
