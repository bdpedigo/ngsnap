"""Render the default-style example used in the README.

Uses public, no-auth MICrONS-adjacent data (FIB-25 EM image + ground-truth
segmentation with meshes) so the example reproduces anywhere. Needs the render
extra: `uv sync --extra render`.
"""

from pathlib import Path

from ngsnap import RenderSession, Spec

_IMAGE = "precomputed://gs://neuroglancer-public-data/flyem_fib-25/image"
_SEG = "precomputed://gs://neuroglancer-public-data/flyem_fib-25/ground_truth"

_STATE = {
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

_OUT = Path(__file__).resolve().parent.parent / "assets" / "default-style-example.png"


def main() -> None:
    spec = Spec.default()
    with RenderSession(timeout=90) as session:
        # Warm the session first so the committed image is the stable warm render (P6).
        session.render(_STATE, _OUT, spec=spec)
        session.render(_STATE, _OUT, spec=spec)
    print(f"wrote {_OUT}")


if __name__ == "__main__":
    main()
