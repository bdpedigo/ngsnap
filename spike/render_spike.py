"""Render spike: prove a Neuroglancer state renders to PNG headlessly.

Starts a ``neuroglancer.Viewer``, points a browser driver at it, screenshots the
representative state twice in the same session, and records wall-clock time, peak
memory, and whether the two renders are byte-identical. Writes both PNGs and a
``metrics.json`` so a GitHub Actions job can upload them as artifacts.

Usage:
    uv run python spike/render_spike.py --driver chrome
    xvfb-run -a uv run python spike/render_spike.py --driver firefox-xvfb
"""

from __future__ import annotations

import argparse
import contextlib
import json
import platform
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Self

import neuroglancer
from drivers import SUPPORTED_DRIVERS, open_driver

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_STATE = REPO_ROOT / "representative_state.json"


@dataclass
class Metrics:
    driver: str
    success: bool = False
    error: str | None = None
    render1_seconds: float | None = None
    render2_seconds: float | None = None
    peak_rss_mb: float | None = None
    image_bytes: int | None = None
    renders_identical: bool | None = None
    width: int = 0
    height: int = 0
    layout: str | None = None
    png1: str | None = None
    png2: str | None = None
    state_path: str = ""
    started_at: str = ""
    platform: dict[str, str] = field(default_factory=dict)
    install_notes: str | None = None


class PeakMemorySampler:
    """Samples RSS of this process and its children, tracking the peak."""

    def __init__(self, interval: float = 0.2) -> None:
        self._interval = interval
        self._peak_bytes = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        try:
            import psutil
        except ImportError:
            return
        proc = psutil.Process()
        while not self._stop.is_set():
            total = proc.memory_info().rss
            for child in proc.children(recursive=True):
                try:
                    total += child.memory_info().rss
                except psutil.Error:
                    continue
            self._peak_bytes = max(self._peak_bytes, total)
            self._stop.wait(self._interval)

    def __enter__(self) -> Self:
        self._thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._stop.set()
        self._thread.join(timeout=2)

    @property
    def peak_mb(self) -> float:
        return round(self._peak_bytes / (1024 * 1024), 1)


def screenshot_png(
    viewer: neuroglancer.Viewer, size: tuple[int, int], timeout: float
) -> bytes:
    """Take a screenshot, failing loudly if chunks never finish loading."""
    result: dict[str, Any] = {}

    def worker() -> None:
        try:
            result["png"] = viewer.screenshot(size=size).screenshot.image
        except Exception as exc:
            result["error"] = exc

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(timeout=timeout)
    if thread.is_alive():
        raise TimeoutError(
            f"screenshot did not complete within {timeout}s "
            "(data source unreachable or scene too heavy to load headlessly)"
        )
    if "error" in result:
        raise result["error"]
    return result["png"]


def load_state(state_path: Path, layout: str | None) -> neuroglancer.ViewerState:
    raw = json.loads(state_path.read_text())
    if layout is not None:
        raw["layout"] = layout
        raw["showSlices"] = True
    return neuroglancer.ViewerState(raw)


def run(args: argparse.Namespace) -> Metrics:
    size = (args.width, args.height)
    metrics = Metrics(
        driver=args.driver,
        width=args.width,
        height=args.height,
        layout=args.layout,
        state_path=str(args.state),
        started_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        platform={
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    neuroglancer.set_server_bind_address("127.0.0.1")
    viewer = neuroglancer.Viewer()
    viewer.set_state(load_state(args.state, args.layout))

    driver = None
    try:
        with PeakMemorySampler() as sampler:
            driver = open_driver(args.driver, viewer, size)
            metrics.install_notes = driver.install_notes

            start = time.perf_counter()
            png1 = screenshot_png(viewer, size, args.timeout)
            metrics.render1_seconds = round(time.perf_counter() - start, 2)

            start = time.perf_counter()
            png2 = screenshot_png(viewer, size, args.timeout)
            metrics.render2_seconds = round(time.perf_counter() - start, 2)

        png1_path = out_dir / f"{args.driver}-render1.png"
        png2_path = out_dir / f"{args.driver}-render2.png"
        png1_path.write_bytes(png1)
        png2_path.write_bytes(png2)

        metrics.png1 = str(png1_path)
        metrics.png2 = str(png2_path)
        metrics.image_bytes = len(png1)
        metrics.renders_identical = png1 == png2
        metrics.peak_rss_mb = sampler.peak_mb
        metrics.success = True
    except Exception as exc:
        metrics.error = f"{type(exc).__name__}: {exc}"
    finally:
        if driver is not None:
            with contextlib.suppress(Exception):
                driver.close()

    return metrics


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", required=True, choices=SUPPORTED_DRIVERS)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "out"))
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=1200)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument(
        "--layout",
        default=None,
        help="Override the state's layout (e.g. 4panel) to show 2D + 3D panels.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    metrics = run(args)

    metrics_path = Path(args.out_dir) / f"{args.driver}-metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(asdict(metrics), indent=2) + "\n")

    print(json.dumps(asdict(metrics), indent=2), file=sys.stderr)
    return 0 if metrics.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
