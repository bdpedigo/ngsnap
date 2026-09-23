---
id: TASK-8
title: >-
  Render engine: browser session plus render(state, out_path, style, timeout)
  with load waiting and batch reuse
status: Done
assignee: []
created_date: '2026-09-22 19:32'
updated_date: '2026-09-23 00:31'
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
- [x] #1 A public render() function takes any accepted state input, an output path, a Style, and a timeout in seconds, and writes a PNG at the style's configured size
- [x] #2 A session context manager starts the browser once and can render many states; a test renders three states through one session and the second and third are faster than the first
- [x] #3 The render returns only after Neuroglancer reports all visible chunks loaded; a test with an unreachable data source raises a timeout error and writes no file
- [x] #4 No partial or blank image is ever left at the output path on failure
- [x] #5 Two renders of the same state and style in one CI run produce byte-identical PNGs, or the deviation is documented with a reason
- [x] #6 Renders a state with a 2D cross-section, a 3D mesh panel, and a multi-panel layout in an integration test that runs in the browser CI job
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

Render engine implemented in src/ngsnap/render.py; public API render() + RenderSession exported from ngsnap. Backend: pinned Chrome for Testing (154.0.8037.57) via neuroglancer.webdriver/Selenium behind a small _new_chrome seam; selenium ships as the optional 'render' extra (base install stays browser-free, imported lazily with an actionable error if missing). Flow follows the TASK-1 spike: neuroglancer.Viewer server + browser opens only the viewer URL + Viewer.screenshot(size) blocks until visible chunks load; screenshot runs in a worker thread with a join timeout (screenshot has no native timeout) so a slow/unreachable source raises RenderTimeoutError instead of a partial image, and _recover() reloads the page so the session survives. Output is written via _atomic_write (tmp + os.replace) so no partial/blank file is ever left on failure. Session reuse keeps one browser alive across renders for batch (P11). AC mapping: #1 render(source,out,style,timeout) writes PNG at style viewerSize (test_render_writes_png_at_configured_size, plus unit test_size_from_config); #2 RenderSession context manager, test_session_reuse_is_faster_after_first (2nd/3rd < 1st); #3 test_unreachable_source_times_out_and_writes_no_file + unit test_timeout_raises_and_writes_no_file; #4 test_atomic_write_writes_bytes_and_leaves_no_tmp + timeout-writes-no-file; #5 test_warm_renders_are_byte_identical (cold-render deviation from progressive mip loading documented in-test); #6 test_multipanel_2d_and_3d_mesh (2D cross-section + 3D mesh + 4panel) now runs in the TASK-9 'browser' CI job on ubuntu-latest. Verified locally on mac-arm64: pytest -m browser = 5 passed (~39s); just check green (44 passed, 5 browser deselected); ruff + mypy clean.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Render engine: render(state, out_path, style, timeout) and a reusable RenderSession that turn a state + style into a PNG headlessly via a pinned Chrome-for-Testing/Selenium session. Real load-waiting (Viewer.screenshot blocks on visible chunks) with a worker-thread timeout that fails loudly on slow/unreachable sources, atomic writes so no partial image is ever left, byte-identical warm renders (P6), and session reuse for batch (P11). selenium is an optional 'render' extra; base install stays browser-free for templating. 2D+3D multi-panel integration test runs in the browser CI job (TASK-9). All six ACs met; validated locally and wired into CI.
<!-- SECTION:FINAL_SUMMARY:END -->
