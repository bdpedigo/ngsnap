---
id: TASK-10
title: 'Actionable errors and configurable logging (P8, P13)'
status: To Do
assignee: []
created_date: '2026-09-22 19:33'
labels: []
milestone: m-2
dependencies:
  - TASK-8
priority: medium
type: feature
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When the blog build fails at 2 a.m. the only evidence is the CI log. Every failure the package can produce must be distinguishable from the log alone: bad link, unparseable state, unreachable or unauthorized data source, browser crash, timeout while chunks load. Today's neuroglancer tooling prints raw progress lines to stdout and reports stalls only as reloads. This task defines the exception hierarchy, decides what each error message contains, and routes all output through the logging module at configurable levels so that quiet is possible in production and verbose is possible when debugging.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A small exception hierarchy exists with one base class and distinct classes for input, data source, browser, and timeout failures
- [ ] #2 Each error message names the failing input, such as the layer or source URL, and suggests the likely fix
- [ ] #3 Browser console errors and chunk load statistics are available at DEBUG level and are silent at the default level
- [ ] #4 Log level is settable from the Python API and from the CLI
- [ ] #5 Tests assert on the exception type and message for each failure mode that can be triggered without a browser
<!-- AC:END -->
