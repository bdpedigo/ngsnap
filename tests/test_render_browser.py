"""Integration tests that launch a real headless browser. Skipped by default.

Run with the 'render' extra installed and the browser marker selected:
    uv run pytest -m browser
These cover the acceptance criteria that need a live render (P2, P3, P6, P11, P14).
"""

import struct
import time
from pathlib import Path

import pytest

from ngsnap import RenderSession, RenderTimeoutError, Spec, render

pytestmark = pytest.mark.browser

# Public MICrONS-adjacent data, no auth: FIB-25 EM image + ground-truth segmentation (has meshes).
_IMAGE = "precomputed://gs://neuroglancer-public-data/flyem_fib-25/image"
_SEG = "precomputed://gs://neuroglancer-public-data/flyem_fib-25/ground_truth"


def _sized_spec(width: int, height: int) -> Spec:
    base = Spec.default()
    return Spec(
        template=base.template,
        config={**base.config, "viewerSize": [width, height]},
        respects=base.respects,
    )


def _png_size(data: bytes) -> tuple[int, int]:
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def _image_state() -> dict:
    return {
        "layers": [{"type": "image", "source": _IMAGE, "name": "image"}],
        "layout": "xy",
    }


def test_render_writes_png_at_configured_size(tmp_path: Path) -> None:
    out = render(
        _image_state(), tmp_path / "fig.png", spec=_sized_spec(300, 225), timeout=60
    )
    assert _png_size(out.read_bytes()) == (300, 225)


def test_session_reuse_is_faster_after_first(tmp_path: Path) -> None:
    spec = _sized_spec(300, 225)
    state = _image_state()
    times: list[float] = []
    with RenderSession(timeout=60) as session:
        for i in range(3):
            start = time.time()
            session.render(state, tmp_path / f"s{i}.png", spec=spec)
            times.append(time.time() - start)
    assert times[1] < times[0]
    assert times[2] < times[0]


def test_warm_renders_are_byte_identical(tmp_path: Path) -> None:
    # P6: once the session is warm (chunks loaded) the same state renders identically.
    # The cold first render can differ because progressive loading may finish the screenshot
    # at a slightly coarser mip, so we compare two warm renders.
    spec = _sized_spec(300, 225)
    state = _image_state()
    with RenderSession(timeout=60) as session:
        session.render(state, tmp_path / "warmup.png", spec=spec)
        second = session.render(state, tmp_path / "a.png", spec=spec).read_bytes()
        third = session.render(state, tmp_path / "b.png", spec=spec).read_bytes()
    assert second == third


def test_multipanel_2d_and_3d_mesh(tmp_path: Path) -> None:
    # P14: a 2D cross-section, a 3D mesh panel, and a multi-panel layout in one image.
    state = {
        "layers": [
            {"type": "image", "source": _IMAGE, "name": "image"},
            {
                "type": "segmentation",
                "source": _SEG,
                "name": "seg",
                "segments": ["21894"],
            },
        ],
        "layout": "4panel",
        "showSlices": True,
    }
    out = render(state, tmp_path / "multi.png", spec=_sized_spec(400, 300), timeout=90)
    assert _png_size(out.read_bytes()) == (400, 300)


def test_unreachable_source_times_out_and_writes_no_file(tmp_path: Path) -> None:
    # P8: a slow/unreachable source fails loudly instead of emitting a partial image.
    state = {
        "layers": [
            {
                "type": "image",
                "source": "precomputed://gs://neuroglancer-public-data/no-such-xyz/image",
                "name": "image",
            }
        ],
        "layout": "xy",
    }
    out = tmp_path / "never.png"
    with pytest.raises(RenderTimeoutError):
        render(state, out, spec=_sized_spec(200, 150), timeout=8)
    assert not out.exists()
