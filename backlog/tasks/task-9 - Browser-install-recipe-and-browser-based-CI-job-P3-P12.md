---
id: TASK-9
title: 'Browser install recipe and browser-based CI job (P3, P12)'
status: To Do
assignee: []
created_date: '2026-09-22 19:33'
labels: []
milestone: m-2
dependencies:
  - TASK-1
  - TASK-2
priority: high
type: chore
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Consumers of this package run it inside their own CI, so installing the browser must be one documented command or script, not a page of apt instructions (P12). The spike (task-1) records what worked; this task turns that into a maintained recipe and a CI job in this repo that runs the browser integration tests on every push, so regressions in the render path are caught here rather than in the blog build.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A justfile recipe or shell script installs the chosen browser and its system dependencies on ubuntu-latest in one step
- [ ] #2 The README documents the install step for CI and for a local macOS developer machine
- [ ] #3 A GitHub Actions job runs the browser integration tests on ubuntu-latest and passes
- [ ] #4 The browser CI job completes within a documented time budget and the budget is recorded in design.md next to P4
<!-- AC:END -->
