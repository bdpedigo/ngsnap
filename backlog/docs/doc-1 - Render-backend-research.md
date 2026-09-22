---
id: doc-1
title: Render backend research
type: other
created_date: '2026-09-22 19:30'
updated_date: '2026-09-22 19:31'
---
Research notes from 2026-09-22 on how to render a Neuroglancer state to a PNG without a display. Sources: the installed `neuroglancer` 2.41 Python package, the neuroglancer GitHub repository, and its CI configuration.

## What the neuroglancer Python package already provides

- `neuroglancer.Viewer` starts a local Tornado server that hosts the Neuroglancer client. Any browser that opens `viewer.get_viewer_url()` becomes a render target.
- `Viewer.screenshot(size=(w, h))` sets `viewer_size` in the config state, asks the client for a screenshot, and blocks until the reply. The client only replies after all visible chunks load. The reply carries PNG bytes in `ScreenshotReply.image` and a numpy view in `image_pixels`.
- `Viewer.async_screenshot(callback, statistics_callback=...)` streams `ScreenshotStatistics` while chunks load. `neuroglancer.tool.screenshot` uses the time since the last statistics message as a stall detector and reloads the browser after `--refresh-browser-timeout` seconds (default 60).
- `neuroglancer.tool.screenshot` also provides: tiled rendering above about 4096x4096, segment sharding for very large meshes, `--hide-axis-lines`, `--hide-default-annotations`, `--layout`, `--cross-section-background-color`, `--scale-bar-scale`, `--projection-scale-multiplier`, `--resolution-scale-factor`, and memory and download limits. Its `apply_state_modifications` function is a small existing example of the templating idea in P15.
- `neuroglancer.webdriver.Webdriver` wraps Selenium. Chrome gets `--headless=new`, Firefox gets `--headless`. A `docker=True` option adds `--no-sandbox --disable-gpu --disable-dev-shm-usage`. Selenium is an optional dependency and is not installed by default.
- `neuroglancer.url_state` has `parse_url`, `parse_url_fragment`, `to_url`, `to_url_fragment`, and `to_json_dump`. It handles the URL-safe JSON variant that Neuroglancer links use (single quotes, underscores for commas).

## Two state objects, not one

Neuroglancer keeps rendering knobs in two places. A templating or style layer must cover both.

| Object | Python class | Example knobs |
| --- | --- | --- |
| Viewer state (in the link) | `neuroglancer.ViewerState` | `layout`, `showAxisLines`, `showDefaultAnnotations`, `crossSectionBackgroundColor`, `projectionBackgroundColor`, `crossSectionScale`, `projectionScale`, layer visibility, `showSlices` |
| Config state (client only, not in the link) | `neuroglancer.viewer_config_state.ConfigState` | `showUIControls`, `showPanelBorders`, `viewerSize`, `scaleBarOptions` (scale factor, font, bar height, offsets), `showLayerHoverValues`, `prefetch` |

## Headless WebGL on CI

- The neuroglancer Python README states: "due to bugs in Swiftshader, Chrome Headless does not work. Firefox Headless also currently does not support WebGL at all. On Linux, you can successfully run the tests headlessly on Firefox using `xvfb-run`."
- Their CI workflow runs browser tests only on `ubuntu-latest`, with Firefox from the Mozilla team PPA plus `xvfb`, through a `nox -s test_xvfb -- --browser firefox` session. On macOS and Windows runners they skip browser tests because "a working headless WebGL2 implementation is not available on Github actions".
- The README note can be stale. Chrome `--headless=new` with `--use-angle=swiftshader --enable-unsafe-swiftshader` gives software WebGL2 in recent Chrome builds. Software WebGL on heavy scenes is slow and memory-hungry, so the spike must measure time and peak memory.
- Firefox headless mode with WebGL is worth a recheck too, because it is the lightest install if it works.

## Candidate browser drivers for the spike

1. `neuroglancer.webdriver.Webdriver` (Selenium) with Chrome headless and Swiftshader flags. Least code. Needs a Chrome or Chromium binary and a matching driver on the runner. Selenium Manager can download the driver.
2. Same, with Firefox under `xvfb-run`. Mirrors neuroglancer's own CI, so it is known to work. Adds `xvfb` as a system dependency and is Linux only.
3. Playwright-driven Chromium pointed at the `neuroglancer.Viewer` URL. Playwright bundles browsers (`playwright install --with-deps chromium`), which gives the simplest install story for P12. Needs our own thin driver class, because the screenshot itself still returns through the Python server.

In every option the browser only opens a URL and stays alive. The screenshot, load waiting, and stall detection all live on the Python side. That makes the driver a small replaceable seam.

## Open items for the spike to answer

- Does Chrome headless with Swiftshader render a real 2D plus 3D state correctly today? Compare pixels against a non-headless render of the same state.
- Wall-clock time and peak memory per image for a representative Neuroddities-style state on `ubuntu-latest`.
- Are renders byte-identical across two runs on the same runner (P6)? Software rasterizers are usually deterministic, GPUs often are not.
- Which driver has the shortest install recipe for CI?
