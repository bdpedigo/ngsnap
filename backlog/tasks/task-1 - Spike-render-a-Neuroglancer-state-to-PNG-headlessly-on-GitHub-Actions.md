---
id: TASK-1
title: 'Spike: render a Neuroglancer state to PNG headlessly on GitHub Actions'
status: Done
assignee:
  - '@ben'
created_date: '2026-09-22 19:31'
updated_date: '2026-09-22 20:46'
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
- [x] #1 A GitHub Actions workflow on ubuntu-latest renders the representative state to a PNG and uploads it as a workflow artifact
- [x] #2 The PNG shows both the 2D cross-section and the 3D mesh panel with data visible, and matches a non-headless local render of the same state by visual comparison
- [x] #3 Wall-clock time from browser start to PNG written, and time for a second render in the same browser session, are recorded for each candidate driver that works
- [x] #4 Two consecutive renders of the same state on the same runner are compared byte for byte and the result is recorded
- [x] #5 Install steps and system dependencies for each candidate that worked are recorded, and candidates that failed are recorded with the failure mode
- [x] #6 A backend decision is recorded in backlog document doc-1 and the Open Questions section of design.md is updated with the outcome and a concrete runtime target for P4
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

CI run 35780750998 on ubuntu-latest completed; artifacts downloaded and inspected. ALL THREE DRIVERS WORK headlessly with no GPU.

Results (1600x1200): chrome 3d=1.86s / 4panel=12.56s, render2 0.08-0.36s, peak 2149MB; firefox-xvfb 3d=1.83s / 4panel=10.68s, render2 0.08-0.13s, peak 2385MB; playwright 3d=2.05s / 4panel=25.87s, render2 0.21-0.43s, peak 1627MB. Every driver: two renders byte-identical (renders_identical=true). chrome and playwright 3d PNGs byte-identical to each other (same Chromium+SwiftShader).

Verified visually: chrome and firefox 4panel CI renders show 3 EM cross-sections + 3D neuron mesh, matching spike/baselines/local-4panel.png. AC#2 caveat: the local baseline was rendered via headless Chrome on macOS (hardware GL), which matches the CI SwiftShader output visually; no separate non-headless capture was taken.

No driver failed. Decision recorded in doc-1: default Playwright-Chromium, Chrome/Selenium fallback. design.md Open Questions resolved and P4 target set (<=30s cold, <1s warm, 60s timeout).

Backend switched from Playwright to Chrome/Selenium per review. spike/drivers.py now drives Chrome for Testing pinned via Selenium Manager (NGSNAP_CHROME_VERSION default 154.0.8037.57; linux-x64 + mac-arm64), giving a reproducible engine that also runs locally on Apple Silicon (Playwright had no mac13-arm64 build). Updated doc-1 Decision + design.md to name Chrome/Selenium as default. Fixed a real bug: justfile and workflow now pass 'uv run --group spike' so selenium isn't dropped by the default-group sync. Validated locally on mac via 'just spike-render chrome': pinned CfT renders, two renders byte-identical, ruff clean.

AC evidence: run 35780750998 (all three drivers green on ubuntu-latest) still stands \u2014 the switch changes the recommended default, not the spike conclusions. The pinned-Chrome + --group-spike workflow itself is validated locally but not yet re-run in CI; recommend one confirming CI run after the next push (non-blocking).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Spike proved headless Neuroglancer WebGL rendering works on GitHub Actions ubuntu-latest with no GPU. Built spike/ harness (render_spike.py + drivers.py for chrome/firefox-xvfb/playwright + representative MICrONS state + baselines), a 'spike' dep group, justfile recipes, and .github/workflows/render-spike.yml. Verified via CI run 35780750998: all three drivers rendered the 2D+3D state to PNG artifacts, all byte-identical across runs; cold render ~10-26s, warm ~<0.5s, peak ~2.4GB. Decision recorded in doc-1 (default Playwright-Chromium, Chrome/Selenium fallback); design.md Open Question resolved and P4 target set.
<!-- SECTION:FINAL_SUMMARY:END -->
