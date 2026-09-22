---
id: TASK-11
title: 'CLI: ngsnap render, key, template, and batch commands (P9)'
status: To Do
assignee: []
created_date: '2026-09-22 19:33'
labels: []
milestone: m-2
dependencies:
  - TASK-8
  - TASK-6
  - TASK-4
references:
  - design.md
priority: medium
type: feature
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Some consumers are not Python programs. A static-site generator or a shell script needs to render figures and compute cache keys from the command line (P9). The CLI is a thin layer over the Python API, so it should hold no logic of its own. Commands sketched in design.md: render one state to a PNG, print the cache key, apply a template and print the new URL or JSON without rendering, and render a batch from a manifest file through one browser session.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ngsnap render <url-or-file> -o out.png [--style file] writes a PNG and exits non-zero with the error message on failure
- [ ] #2 ngsnap key <url-or-file> [--style file] prints the cache key and nothing else on stdout
- [ ] #3 ngsnap template <url-or-file> with override flags prints the new state as a URL or as JSON, selectable by flag
- [ ] #4 ngsnap batch <manifest> renders every entry through one browser session and reports per-entry success or failure without stopping at the first error
- [ ] #5 Every command has --help text and the README shows one example per command
<!-- AC:END -->
