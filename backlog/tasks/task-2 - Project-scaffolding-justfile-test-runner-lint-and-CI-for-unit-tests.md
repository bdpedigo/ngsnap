---
id: TASK-2
title: 'Project scaffolding: justfile, test runner, lint, and CI for unit tests'
status: To Do
assignee: []
created_date: '2026-09-22 19:31'
labels: []
milestone: m-1
dependencies: []
references:
  - AGENTS.md
  - pyproject.toml
priority: medium
type: chore
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The repo is an empty uv project with a hello-world entry point. Before feature work lands, contributors and agents need one obvious way to run tests, lint, and format, and CI needs to run the pure-Python test suite on every push. AGENTS.md says that command recipes belong in a justfile, not in code comments. The browser-based CI job is out of scope here and follows from the render spike.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A justfile has recipes for install, test, lint, format, and typecheck, and each recipe runs cleanly from a fresh clone
- [ ] #2 pytest is configured as a dev dependency and an empty test suite passes
- [ ] #3 ruff check and ruff format run with the rules already in pyproject.toml and pass on the existing source
- [ ] #4 A GitHub Actions workflow runs the test and lint recipes on push and pull request for Python 3.13
- [ ] #5 The package entry point is renamed so that it no longer prints hello world, or is removed until the CLI task lands
<!-- AC:END -->
