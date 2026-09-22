---
id: TASK-8
title: >-
  Render engine: browser session plus render(state, out_path, style, timeout)
  with load waiting and batch reuse
status: To Do
assignee: []
created_date: '2026-09-22 19:32'
updated_date: '2026-09-22 20:48'
labels: []
milestone: m-1
dependencies:
  - TASK-1
  - TASK-3
  - TASK-5
references:
  - backlog/docs/doc-1 - Render-backend-research.md
priority: high
type: feature
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
This is the core deliverable: turn a state plus a style into a PNG (P2, P14). It wires the backend chosen in the spike (task-1) to the templating and style layers. The design follows what the spike showed: a `neuroglancer.Viewer` server, a browser that only opens the viewer URL, and `Viewer.screenshot()` which waits for all visible chunks before it returns the image. Load waiting must be real, not a sleep, so that a slow data source produces a timeout error rather than a half-loaded figure (P8). `neuroglancer.tool.screenshot.capture_screenshots` shows how to use the statistics callback as a stall detector.

Browser startup is the dominant fixed cost, so the engine must let a caller open one session and render many states through it (P11). A batch mode that amortizes startup is the nice-to-have from design.md, but the session object is required because the CLI batch command and the blog build both need it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A public render() function takes any accepted state input, an output path, a Style, and a timeout in seconds, and writes a PNG at the style's configured size
- [ ] #2 A session context manager starts the browser once and can render many states; a test renders three states through one session and the second and third are faster than the first
- [ ] #3 The render returns only after Neuroglancer reports all visible chunks loaded; a test with an unreachable data source raises a timeout error and writes no file
- [ ] #4 No partial or blank image is ever left at the output path on failure
- [ ] #5 Two renders of the same state and style in one CI run produce byte-identical PNGs, or the deviation is documented with a reason
- [ ] #6 Renders a state with a 2D cross-section, a 3D mesh panel, and a multi-panel layout in an integration test that runs in the browser CI job
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
DEPENDENCY DECISION (from TASK-1 follow-up): the render backend is Chrome via neuroglancer.webdriver (Selenium), pinned to a Chrome-for-Testing build for reproducibility + local (mac-arm64) parity. selenium must NOT ship only in the dev 'spike' dependency-group (PEP 735 groups are not delivered to PyPI consumers). When this engine imports selenium, declare it as an optional extra instead:

[project.optional-dependencies]
render = ["selenium>=4.20"]   # pip install ngsnap[render]

Keep the base install browser-free so templating (P15: apply_template/to_url) works with no browser, and import selenium lazily inside the engine, raising an actionable error (P8) if the 'render' extra is missing. The 'spike' group can then be retired or left pinning the same build for local experiments.

REUSABLE SPIKE DETAILS (harness removed after TASK-1; these are the bits worth keeping):
- Chrome options that gave software WebGL2 headless with no GPU: --headless=new, --use-gl=angle, --use-angle=swiftshader, --enable-unsafe-swiftshader, --ignore-gpu-blocklist, plus --no-sandbox and --disable-dev-shm-usage on CI. Set options.browser_version to a pinned Chrome-for-Testing version (spike used 154.0.8037.57) so Selenium Manager downloads that exact build (linux-x64 + mac-arm64).
- Flow: neuroglancer.set_server_bind_address('127.0.0.1'); v = neuroglancer.Viewer(); v.set_state(state); open browser at v.get_viewer_url(); then PNG bytes = v.screenshot(size=(w,h)).screenshot.image (note the .screenshot.image accessor \u2014 screenshot() returns an ActionState whose .screenshot is the ScreenshotReply). screenshot() blocks until all visible chunks load.
- Session reuse: keep one browser/viewer alive across states for batch (P11); 2nd render was ~100-300x faster.
- Timeout: screenshot() has no timeout arg; run it in a worker thread with a join timeout to fail loudly (P8). Representative public test state: MICrONS minnie65 (S3 EM image + gs:// segmentation mesh), layout '3d'; use '4panel' + showSlices=true to get 2D+3D in one image.
<!-- SECTION:NOTES:END -->
