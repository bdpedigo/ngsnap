---
id: TASK-1
title: 'Spike: render a Neuroglancer state to PNG headlessly on GitHub Actions'
status: In Progress
assignee:
  - '@ben'
created_date: '2026-09-22 19:31'
updated_date: '2026-09-22 20:29'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Decode the provided MICrONS link into spike/representative_state.json (image + segmentation w/ mesh + 3d layout).
2. Build spike harness under spike/: driver abstraction (chrome-headless+swiftshader via neuroglancer.webdriver, firefox under xvfb, playwright chromium) + render_spike.py that starts neuroglancer.Viewer, opens URL in the driver, screenshots twice, records wall-clock (render1, render2), peak memory, and byte-for-byte diff of the two renders, writing PNGs + metrics.json.
3. Add a 'spike' dependency group in pyproject (selenium, playwright, psutil, pillow, numpy).
4. Add .github/workflows/render-spike.yml: ubuntu-latest matrix over the 3 drivers, install recipes per driver, run spike, upload PNG + metrics artifacts. Record failures per driver.
5. Add justfile recipes + spike/README.md documenting install recipes and local non-headless baseline render for AC#2 comparison.
6. After user pushes and CI runs: record wall-clock/determinism/install findings, write backend decision into doc-1, and update design.md Open Questions + P4 target.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Built spike harness under spike/: drivers.py (chrome+swiftshader via neuroglancer.webdriver, firefox-xvfb, playwright-chromium), render_spike.py (viewer + 2 screenshots/session, records render1/render2 seconds, peak RSS via psutil, byte-for-byte determinism, failure mode), representative_state.json decoded from the MICrONS minnie65 link, and baselines/ reference PNGs. Added 'spike' dep group (selenium, playwright, psutil), justfile recipes (spike-deps, spike-render, spike-render-4panel), and .github/workflows/render-spike.yml (ubuntu-latest matrix over 3 drivers, renders canonical 3d + 4panel variant, prints metrics to job summary, uploads PNG+metrics artifacts).

Local validation on macOS (chrome driver): render1 ~1.5-4.6s, render2 ~0.02-0.05s (batch reuse), two renders byte-identical, peak RSS ~1.1-1.5GB. 3d state renders the neuron mesh correctly; 4panel override shows 2D EM cross-sections + 3D mesh (AC#2 view). Note: playwright has no chromium build for local mac13-arm64; chrome driver used locally, playwright runs in CI.

REMAINING (needs CI run by user): push to trigger render-spike workflow, then record per-driver wall-clock/determinism/install results + failure modes (AC#3-5), confirm ubuntu-latest artifact + visual match vs baselines (AC#1-2), and write the backend decision into doc-1 + update design.md Open Questions with a concrete P4 runtime target (AC#6).
<!-- SECTION:NOTES:END -->
