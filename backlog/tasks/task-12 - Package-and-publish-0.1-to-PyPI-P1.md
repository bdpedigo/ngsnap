---
id: TASK-12
title: Package and publish 0.1 to PyPI (P1)
status: To Do
assignee: []
created_date: '2026-09-22 19:33'
labels: []
milestone: m-2
dependencies:
  - TASK-8
priority: low
type: chore
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The blog and other consumers must install this as an ordinary dependency (P1). The repo already uses uv_build. This task finishes the metadata, decides whether the browser driver is a core or an optional dependency, adds a release workflow, and publishes the first version. Also the point to settle the package name, which design.md still lists as open.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 pyproject.toml has a real description, license, classifiers, and URLs, and the package name decision is recorded in design.md
- [ ] #2 The browser driver dependency is either core or an extra, and the README states which and why
- [ ] #3 A tagged release triggers a GitHub Actions workflow that builds and publishes to PyPI with trusted publishing
- [ ] #4 pip install of the published package in a fresh environment followed by the documented browser install step renders the README example
<!-- AC:END -->
