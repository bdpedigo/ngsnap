# Render spike (TASK-1)

Proves the core unproven assumption: a real Neuroglancer client can render WebGL
to a PNG on a GitHub Actions `ubuntu-latest` runner with no GPU and no display
(design requirement P3), and measures how long it takes.

## What's here

- `representative_state.json` — a public MICrONS minnie65 state (S3 EM image
  layer + `gs://` segmentation with a selected mesh, `layout: "3d"`). No
  credentials needed.
- `render_spike.py` — starts a `neuroglancer.Viewer`, points a browser driver at
  it, screenshots the state twice in one session, and writes PNGs plus a
  `metrics.json` (wall-clock per render, peak RSS, byte-for-byte equality of the
  two renders, failure mode if any).
- `drivers.py` — the three candidate drivers, each a thin swappable seam that
  only opens the viewer URL. The screenshot is taken through the Python server.
- `baselines/` — reference renders produced locally for the visual comparison in
  acceptance criterion #2.

## Drivers

| Driver | How WebGL runs | Install |
| --- | --- | --- |
| `chrome` | Chrome `--headless=new` + ANGLE/SwiftShader software WebGL2 | Selenium + a Chrome binary; Selenium Manager fetches chromedriver |
| `firefox-xvfb` | Firefox non-headless under a virtual display | Selenium + Firefox + `xvfb`; run under `xvfb-run -a` (Linux only) |
| `playwright` | Playwright-bundled Chromium + SwiftShader | `playwright install --with-deps chromium` |

## Run it

```bash
just spike-deps                      # install selenium, playwright, psutil
just spike-render chrome             # canonical 3D state
just spike-render-4panel chrome      # 2D cross-sections + 3D mesh (AC #2 view)
```

For the Firefox driver on Linux, wrap the process in a virtual display:

```bash
xvfb-run -a uv run python render_spike.py --driver firefox-xvfb
```

Playwright's newer builds do not ship a Chromium for `mac13-arm64`; use the
`chrome` driver locally on that machine, or run the `playwright` driver in CI.

Outputs land in `spike/out/` (and `spike/out-4panel/`), which are git-ignored.

## CI

`.github/workflows/render-spike.yml` runs all three drivers on `ubuntu-latest`,
renders both the canonical and 4panel variants, prints each `metrics.json` to the
job summary, and uploads the PNGs and metrics as artifacts. Trigger it via
`workflow_dispatch` or by pushing changes under `spike/`.

## Acceptance criteria mapping

- **#1** artifact on `ubuntu-latest` — the workflow uploads `render-<driver>`.
- **#2** 2D + 3D visible, matches a local render — compare the 4panel artifact
  against `baselines/local-4panel.png`.
- **#3/#4** timing and byte-for-byte determinism — `metrics.json`
  (`render1_seconds`, `render2_seconds`, `renders_identical`).
- **#5** install recipes / failure modes — the driver table above plus the
  `install_notes` and `error` fields in each `metrics.json`.
- **#6** backend decision — recorded in `backlog/docs/doc-1` and `design.md`
  after the CI run.
