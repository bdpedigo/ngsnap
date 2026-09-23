---
id: TASK-11
title: 'CLI: ngsnap render, apply, check, extract, and cache-key commands (P9)'
status: To Do
assignee: []
created_date: '2026-09-22 19:33'
updated_date: '2026-09-23 18:26'
labels: []
milestone: m-2
dependencies:
  - TASK-13
  - TASK-16
  - TASK-6
  - TASK-14
  - TASK-15
references:
  - design.md
priority: medium
type: feature
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Some consumers are not Python programs. A static-site generator or a shell script needs to render figures, restyle links, check conformance, and compute cache keys from the command line (P9). The CLI is a thin layer over the Python API, holding no logic of its own. Per the settled single-IO API, each command takes a single input (a link, a JSON file, or `-` for JSON on stdin). Commands: `render` writes a PNG to `-o`; `apply` prints the restyled link or JSON to stdout (from a `--spec` file or inline `--set` overrides); `check` reports conformance and exits non-zero when a link diverges; `extract` prints a spec TOML lifted from a named setting group of a link; `cache-key` prints the stable key. Every command except `render` writes to stdout so the tool composes in shell pipelines. Multiple-input batch is out of scope for now.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ngsnap render <url-or-file> -o out.png [--spec file] writes a PNG and exits non-zero with the error message on failure
- [ ] #2 ngsnap apply <url-or-file> [--spec file] [--set key=value] [--url | --json] prints the restyled link or JSON to stdout
- [ ] #3 ngsnap check <url-or-file> [--spec file] [--strict] reports conformance and exits non-zero when the link does not match
- [ ] #4 ngsnap extract <url-or-file> [--group appearance] prints a spec TOML that Spec.from_file can load
- [ ] #5 ngsnap cache-key <url-or-file> [--spec file] prints the cache key and nothing else on stdout
- [ ] #6 Every command reads - as JSON on stdin, has --help text, and the README shows one example per command
<!-- AC:END -->
