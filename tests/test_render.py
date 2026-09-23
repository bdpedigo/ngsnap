import threading
from pathlib import Path

import pytest

from ngsnap import RenderError, RenderSession, RenderTimeoutError, Spec
from ngsnap.render import DEFAULT_SIZE, _atomic_write, _size_from_config

STATE_DICT = {
    "layers": [
        {"type": "image", "source": "precomputed://gs://example/img", "name": "img"}
    ],
    "layout": "xy",
}

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


class _BlockingViewer:
    """Stands in for a neuroglancer Viewer whose screenshot never returns."""

    def __init__(self) -> None:
        self.released = threading.Event()

    def set_state(self, state: object) -> None:
        pass

    def screenshot(self, size: object = None) -> object:
        self.released.wait()
        raise AssertionError("should not be reached in the timeout test")


def test_size_from_config_uses_configured_size() -> None:
    assert _size_from_config({"viewerSize": [800, 600]}) == (800, 600)


def test_size_from_config_defaults_when_absent() -> None:
    assert _size_from_config({}) == DEFAULT_SIZE


def test_atomic_write_writes_bytes_and_leaves_no_tmp(tmp_path: Path) -> None:
    out = tmp_path / "sub" / "fig.png"
    result = _atomic_write(out, PNG_BYTES)
    assert result == out
    assert out.read_bytes() == PNG_BYTES
    assert list(tmp_path.glob("**/*.tmp")) == []


def test_render_before_start_raises() -> None:
    session = RenderSession()
    with pytest.raises(RenderError):
        session.render(STATE_DICT, "unused.png")


def test_timeout_raises_and_writes_no_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import importlib

    render_mod = importlib.import_module("ngsnap.render")
    monkeypatch.setattr(render_mod, "_apply_config", lambda viewer, config: None)
    session = RenderSession(timeout=0.2)
    blocking = _BlockingViewer()
    session._viewer = blocking  # type: ignore[assignment]
    out = tmp_path / "fig.png"
    try:
        with pytest.raises(RenderTimeoutError):
            session.render(STATE_DICT, out, spec=Spec.default())
    finally:
        blocking.released.set()
    assert not out.exists()
