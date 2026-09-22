"""Thin, replaceable browser drivers for the render spike.

Each driver only launches a browser and points it at the ``neuroglancer.Viewer``
URL. The screenshot itself is taken through the Python server (see
``render_spike.py``), so the driver stays a small swappable seam.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from neuroglancer import Viewer

# Force software WebGL2 through ANGLE + SwiftShader. `--enable-unsafe-swiftshader`
# is required on Chrome 120+ to allow the SwiftShader fallback at all.
CHROME_SWIFTSHADER_ARGS: tuple[str, ...] = (
    "--use-gl=angle",
    "--use-angle=swiftshader",
    "--enable-unsafe-swiftshader",
    "--ignore-gpu-blocklist",
)

SUPPORTED_DRIVERS: tuple[str, ...] = ("chrome", "firefox-xvfb", "playwright")


@dataclass
class Driver:
    """A launched browser pointed at the viewer, plus how to install it."""

    name: str
    close: Callable[[], None]
    install_notes: str
    launch_args: Sequence[str] = field(default_factory=tuple)


def open_driver(name: str, viewer: Viewer, window_size: tuple[int, int]) -> Driver:
    if name == "chrome":
        return _open_chrome(viewer, window_size)
    if name == "firefox-xvfb":
        return _open_firefox_xvfb(viewer, window_size)
    if name == "playwright":
        return _open_playwright(viewer, window_size)
    raise ValueError(f"unknown driver {name!r}, expected one of {SUPPORTED_DRIVERS}")


def _open_chrome(viewer: Viewer, window_size: tuple[int, int]) -> Driver:
    from neuroglancer.webdriver import Webdriver

    driver = Webdriver(
        viewer=viewer,
        browser="chrome",
        headless=True,
        docker=True,
        window_size=window_size,
        extra_command_line_args=CHROME_SWIFTSHADER_ARGS,
    )
    return Driver(
        name="chrome",
        close=driver.driver.quit,
        install_notes=(
            "Selenium + a Chrome/Chromium binary on PATH. Selenium Manager "
            "downloads the matching chromedriver automatically. SwiftShader "
            "flags force software WebGL2 (no GPU)."
        ),
        launch_args=CHROME_SWIFTSHADER_ARGS,
    )


def _open_firefox_xvfb(viewer: Viewer, window_size: tuple[int, int]) -> Driver:
    from neuroglancer.webdriver import Webdriver

    # Firefox headless has no WebGL; run non-headless under a virtual display
    # (the process must be wrapped in `xvfb-run`). Mirrors neuroglancer's own CI.
    driver = Webdriver(
        viewer=viewer,
        browser="firefox",
        headless=False,
        window_size=window_size,
    )
    return Driver(
        name="firefox-xvfb",
        close=driver.driver.quit,
        install_notes=(
            "Selenium + Firefox + geckodriver, plus the `xvfb` system package. "
            "Run the whole command under `xvfb-run -a`. Linux only."
        ),
    )


def _open_playwright(viewer: Viewer, window_size: tuple[int, int]) -> Driver:
    from playwright.sync_api import sync_playwright

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=True,
        args=list(CHROME_SWIFTSHADER_ARGS),
    )
    context = browser.new_context(
        viewport={"width": window_size[0], "height": window_size[1]}
    )
    page = context.new_page()
    page.goto(viewer.get_viewer_url())

    def close() -> None:
        browser.close()
        playwright.stop()

    return Driver(
        name="playwright",
        close=close,
        install_notes=(
            "`pip install playwright` then `playwright install --with-deps "
            "chromium`, which bundles a browser and its system deps. Simplest "
            "CI install story."
        ),
        launch_args=CHROME_SWIFTSHADER_ARGS,
    )
