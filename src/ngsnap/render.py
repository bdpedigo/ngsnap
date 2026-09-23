"""Headless render of a Neuroglancer state to PNG via a pinned Chrome-for-Testing session."""

from __future__ import annotations

import contextlib
import os
import threading
import uuid
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Any, Self

import neuroglancer
from neuroglancer.viewer_config_state import ConfigState

from ngsnap.errors import RenderError, RenderTimeoutError
from ngsnap.state import StateInput
from ngsnap.style import Style

if TYPE_CHECKING:
    from selenium.webdriver import Chrome

# Pinned Chrome-for-Testing build so renders are reproducible across machines (P6).
CHROME_VERSION = "154.0.8037.57"

# Software WebGL2, headless, no GPU — the flags the TASK-1 spike proved on ubuntu-latest.
_CHROME_ARGS: tuple[str, ...] = (
    "--headless=new",
    "--use-gl=angle",
    "--use-angle=swiftshader",
    "--enable-unsafe-swiftshader",
    "--ignore-gpu-blocklist",
    "--no-sandbox",
    "--disable-dev-shm-usage",
)

DEFAULT_TIMEOUT = 60.0
DEFAULT_SIZE = (1600, 1200)

_SELENIUM_HINT = (
    "The render engine needs the 'render' extra. Install it with "
    "'pip install ngsnap[render]' (or 'uv sync --extra render')."
)


class RenderSession:
    """A live browser + viewer that renders many states, amortizing browser startup (P11).

    Use as a context manager. The browser opens once on entry and stays alive across
    ``render`` calls; the first render pays cold-load cost and later renders that reuse
    the session are far cheaper.
    """

    def __init__(
        self, *, timeout: float = DEFAULT_TIMEOUT, chrome_version: str = CHROME_VERSION
    ) -> None:
        self._timeout = timeout
        self._chrome_version = chrome_version
        self._viewer: neuroglancer.Viewer | None = None
        self._driver: Chrome | None = None
        self._url: str | None = None

    def __enter__(self) -> Self:
        neuroglancer.set_server_bind_address("127.0.0.1")
        self._viewer = neuroglancer.Viewer()
        self._url = self._viewer.get_viewer_url()
        self._driver = _start_browser(self._url, self._chrome_version)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def render(
        self,
        source: StateInput,
        out_path: str | Path,
        *,
        style: Style | None = None,
        timeout: float | None = None,
    ) -> Path:
        """Render ``source`` under ``style`` and write a PNG at the style's configured size.

        Waits for Neuroglancer to report all visible chunks loaded, then writes the PNG
        atomically. Raises :class:`RenderTimeoutError` (and writes nothing) if the load
        does not finish within ``timeout`` seconds.
        """
        if self._viewer is None:
            raise RenderError(
                "RenderSession is not started; use it as a context manager"
            )
        style = style or Style.default()
        templated = style.apply(source)
        size = _size_from_config(templated.config)
        self._viewer.set_state(templated.viewer_state)
        _apply_config(self._viewer, templated.config)
        image = self._screenshot(size, self._timeout if timeout is None else timeout)
        return _atomic_write(Path(out_path), image)

    def _screenshot(self, size: tuple[int, int], timeout: float) -> bytes:
        assert self._viewer is not None
        viewer = self._viewer
        result: dict[str, Any] = {}

        def run() -> None:
            try:
                reply = viewer.screenshot(size=size)
                result["image"] = reply.screenshot.image
            except Exception as error:
                result["error"] = error

        worker = threading.Thread(target=run, daemon=True)
        worker.start()
        worker.join(timeout)
        if worker.is_alive():
            self._recover()
            raise RenderTimeoutError(
                f"Render did not finish loading within {timeout:g}s; the data source may be "
                "slow or unreachable. No image was written."
            )
        if "error" in result:
            raise RenderError(
                f"Neuroglancer failed to render the state: {result['error']}"
            )
        return result["image"]

    def _recover(self) -> None:
        # A hung screenshot leaves the client stuck; reload the page so the session survives.
        if self._driver is not None and self._url is not None:
            with contextlib.suppress(Exception):
                self._driver.get(self._url)

    def close(self) -> None:
        if self._driver is not None:
            self._driver.quit()
            self._driver = None


def render(
    source: StateInput,
    out_path: str | Path,
    *,
    style: Style | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Path:
    """Render a single state to a PNG in a one-shot browser session.

    For several images, open one :class:`RenderSession` and call ``render`` on it to
    avoid paying browser startup per image (P11).
    """
    with RenderSession(timeout=timeout) as session:
        return session.render(source, out_path, style=style)


def _start_browser(url: str, chrome_version: str) -> Chrome:
    driver = _new_chrome(chrome_version)
    driver.get(url)
    return driver


def _new_chrome(chrome_version: str) -> Chrome:
    try:
        from selenium.webdriver import Chrome, ChromeOptions
    except ImportError as error:
        raise RenderError(_SELENIUM_HINT) from error
    options = ChromeOptions()
    options.browser_version = chrome_version
    for arg in _CHROME_ARGS:
        options.add_argument(arg)
    try:
        return Chrome(options=options)
    except Exception as error:
        raise RenderError(f"Could not start Chrome for rendering: {error}") from error


def install_browser(chrome_version: str = CHROME_VERSION) -> None:
    """Provision the pinned Chrome-for-Testing build via Selenium Manager (P12).

    Building the driver once makes Selenium Manager download the pinned browser and
    matching driver, so the first real render does not pay for it and CI failures are
    about rendering, not a missing browser. No system Chrome is required.
    """
    _new_chrome(chrome_version).quit()


def _size_from_config(config: dict[str, Any]) -> tuple[int, int]:
    size = config.get("viewerSize")
    if isinstance(size, (list, tuple)) and len(size) == 2:
        return int(size[0]), int(size[1])
    return DEFAULT_SIZE


def _apply_config(viewer: neuroglancer.Viewer, config: dict[str, Any]) -> None:
    if not config:
        return
    source = ConfigState(config)
    with viewer.config_state.txn() as state:
        for key in source.to_json():
            setattr(state, key, getattr(source, key))


def _atomic_write(out_path: Path, image: bytes) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_name(
        f"{out_path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
    )
    tmp_path.write_bytes(image)
    tmp_path.replace(out_path)
    return out_path
