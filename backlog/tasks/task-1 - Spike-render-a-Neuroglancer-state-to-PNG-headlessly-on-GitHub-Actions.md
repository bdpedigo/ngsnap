---
id: TASK-1
title: 'Spike: render a Neuroglancer state to PNG headlessly on GitHub Actions'
status: To Do
assignee: []
created_date: '2026-09-22 19:31'
labels: []
milestone: m-0
dependencies: []
references:
  - backlog/docs/doc-1 - Render-backend-research.md
  - design.md
  - 'https://github.com/google/neuroglancer/blob/master/python/README.md'
priority: high
type: spike
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The whole package rests on one unproven assumption: that a real Neuroglancer client can render WebGL to an image on a GitHub Actions ubuntu-latest runner with no GPU and no display (P3). Neuroglancer's own README says Chrome headless breaks on Swiftshader bugs and Firefox headless has no WebGL, and their CI falls back to Firefox under xvfb. That note may be stale. Until this is settled, the render backend, install story (P12), and the runtime budget (P4) are all guesses.

The screenshot itself does not depend on the browser driver: `neuroglancer.Viewer.screenshot()` returns PNG bytes through the Python server after all chunks load. The spike only has to prove that some browser can open the viewer URL and produce a correct WebGL render on the runner, and measure how long it takes.

Candidates to compare: (1) `neuroglancer.webdriver.Webdriver` with Chrome `--headless=new` plus Swiftshader flags, (2) the same with Firefox under `xvfb-run`, (3) Playwright-bundled Chromium opening the viewer URL. Use a representative public state that has at least one image layer, one segmentation layer with meshes, and a 3D panel. Use a public data source so the spike needs no credentials.

Background and the list of questions to answer are in backlog document doc-1 (Render backend research).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A GitHub Actions workflow on ubuntu-latest renders the representative state to a PNG and uploads it as a workflow artifact
- [ ] #2 The PNG shows both the 2D cross-section and the 3D mesh panel with data visible, and matches a non-headless local render of the same state by visual comparison
- [ ] #3 Wall-clock time from browser start to PNG written, and time for a second render in the same browser session, are recorded for each candidate driver that works
- [ ] #4 Two consecutive renders of the same state on the same runner are compared byte for byte and the result is recorded
- [ ] #5 Install steps and system dependencies for each candidate that worked are recorded, and candidates that failed are recorded with the failure mode
- [ ] #6 A backend decision is recorded in backlog document doc-1 and the Open Questions section of design.md is updated with the outcome and a concrete runtime target for P4
<!-- AC:END -->
