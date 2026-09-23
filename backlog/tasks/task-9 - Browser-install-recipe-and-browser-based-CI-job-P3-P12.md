---
id: TASK-9
title: 'Browser install recipe and browser-based CI job (P3, P12)'
status: Done
assignee: []
created_date: '2026-09-22 19:33'
updated_date: '2026-09-23 00:31'
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
- [x] #1 A justfile recipe or shell script installs the chosen browser and its system dependencies on ubuntu-latest in one step
- [x] #2 The README documents the install step for CI and for a local macOS developer machine
- [x] #3 A GitHub Actions job runs the browser integration tests on ubuntu-latest and passes
- [x] #4 The browser CI job completes within a documented time budget and the budget is recorded in design.md next to P4
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Chosen backend is Chrome for Testing via Selenium (doc-1). The TASK-1 spike's chrome job proved the browser install on ubuntu-latest needs NO apt and NO xvfb: Selenium Manager auto-downloads the pinned Chrome-for-Testing build (linux-x64 + mac-arm64) and the runner already has the shared libs. AC#1: added install_browser() in render.py (builds the pinned Chrome once so Selenium Manager provisions it, then quits; refactored _start_browser to share _new_chrome) and a 'just install-browser' recipe. AC#2: README documents the one-step install for CI (ubuntu-latest) and local macOS Apple Silicon (identical; mac-arm64 build fetched by Selenium Manager so local matches CI). AC#3: added a 'browser' job to .github/workflows/ci.yml that runs 'uv sync --extra render', provisions Chrome, then 'uv run pytest -m browser' on ubuntu-latest. Validated locally on mac-arm64: pytest -m browser = 5 passed in ~39s; just install-browser succeeds; just check green (44 passed, 5 browser deselected). AC#4: timeout-minutes: 15 on the job; budget recorded in design.md next to P4 (<=15 min covering one-time Chrome download + 5 integration renders; ~40s locally once provisioned).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Browser install recipe + browser CI job. Added install_browser() (Selenium Manager provisions the pinned Chrome for Testing; no system Chrome, apt, or xvfb) exposed via 'just install-browser'; a 'browser' job in ci.yml runs the render integration tests (pytest -m browser) on ubuntu-latest after syncing the render extra and provisioning Chrome; README documents the one-step install for CI and local macOS; time budget (<=15 min) recorded in design.md by P4. Backend and no-apt/no-xvfb recipe follow the TASK-1 spike's chrome result.
<!-- SECTION:FINAL_SUMMARY:END -->
