import json
from pathlib import Path

from neuroglancer.viewer_state import ViewerState

from ngsnap import REMOVE, apply_template, parse_state, to_url
from ngsnap.state import DEFAULT_PREFIX

STATE_DICT = {
    "layers": [
        {"type": "image", "source": "precomputed://gs://example/img", "name": "img"},
        {
            "type": "segmentation",
            "source": "precomputed://gs://example/seg",
            "name": "seg",
            "segments": ["1", "2"],
        },
    ],
    "layout": "xy",
    "showAxisLines": True,
}


def test_input_state_not_mutated() -> None:
    state = ViewerState(STATE_DICT)
    before = state.to_json()
    apply_template(state, {"layout": "3d"})
    assert state.to_json() == before


def test_set_and_override_top_level() -> None:
    result = apply_template(
        STATE_DICT, {"layout": "3d", "showDefaultAnnotations": True}
    )
    viewer = result.viewer_state.to_json()
    assert viewer["layout"] == "3d"
    assert viewer["showDefaultAnnotations"] is True


def test_remove_top_level_element() -> None:
    result = apply_template(STATE_DICT, {"showAxisLines": REMOVE})
    assert "showAxisLines" not in result.viewer_state.to_json()


def test_per_layer_override_by_name() -> None:
    result = apply_template(STATE_DICT, {"layers": {"seg": {"segments": ["9"]}}})
    layers = {layer["name"]: layer for layer in result.viewer_state.to_json()["layers"]}
    assert layers["seg"]["segments"] == ["9"]
    assert layers["img"]["source"] == "precomputed://gs://example/img"


def test_per_layer_add_and_remove() -> None:
    result = apply_template(
        STATE_DICT,
        {
            "layers": {
                "img": REMOVE,
                "anno": {"type": "annotation", "source": "local://annotations"},
            }
        },
    )
    names = [layer["name"] for layer in result.viewer_state.to_json()["layers"]]
    assert "img" not in names
    assert "anno" in names
    assert "seg" in names


def test_config_returned_separately() -> None:
    result = apply_template(
        STATE_DICT,
        {"layout": "3d"},
        config={
            "showUIControls": False,
            "showPanelBorders": False,
            "viewerSize": [800, 600],
            "scaleBarOptions": {"scaleFactor": 2},
        },
    )
    assert result.config == {
        "showUIControls": False,
        "showPanelBorders": False,
        "viewerSize": [800, 600],
        "scaleBarOptions": {"scaleFactor": 2},
    }
    assert "showUIControls" not in result.viewer_state.to_json()


def test_unnamed_elements_unchanged() -> None:
    before = ViewerState(STATE_DICT).to_json()
    after = apply_template(STATE_DICT, {"layout": "3d"}).viewer_state.to_json()
    before_without_layout = {k: v for k, v in before.items() if k != "layout"}
    after_without_layout = {k: v for k, v in after.items() if k != "layout"}
    assert before_without_layout == after_without_layout


def test_deterministic_canonical_json() -> None:
    template = {"layout": "3d", "layers": {"seg": {"segments": ["9"]}}}
    first = apply_template(STATE_DICT, template).to_json()
    second = apply_template(STATE_DICT, template).to_json()
    assert first == second
    assert json.loads(first)["layout"] == "3d"


def test_emit_as_viewer_state_json_and_url() -> None:
    result = apply_template(STATE_DICT, {"layout": "3d"})
    assert isinstance(result.viewer_state, ViewerState)
    canonical = result.to_json()
    assert json.loads(canonical) == result.viewer_state.to_json()
    url = result.to_url()
    assert parse_state(url).to_json() == result.viewer_state.to_json()


def test_url_round_trips_with_prefix() -> None:
    result = apply_template(STATE_DICT, {"layout": "3d"})
    prefix = "https://custom.example.org/ng"
    url = result.to_url(prefix=prefix)
    assert url.startswith(prefix + "#!")
    assert parse_state(url) == parse_state(to_url(result.viewer_state, prefix=prefix))


def test_input_url_prefix_is_preserved_and_can_be_overridden() -> None:
    source_prefix = "https://spelunker.cave-explorer.org/ng/"
    source = to_url(STATE_DICT, prefix=source_prefix)
    result = apply_template(source, {"layout": "3d"})

    assert result.to_url().startswith(source_prefix + "#!")

    override = "https://custom.example.org/viewer"
    assert result.to_url(prefix=override).startswith(override + "#!")


def test_inputs_without_url_prefix_use_default(
    tmp_path: Path,
) -> None:
    path = tmp_path / "state.json"
    path.write_text(json.dumps(STATE_DICT), encoding="utf-8")
    sources = [STATE_DICT, json.dumps(STATE_DICT), path, ViewerState(STATE_DICT)]

    for source in sources:
        assert apply_template(source).to_url().startswith(DEFAULT_PREFIX + "#!")


def test_no_template_returns_normalized_state() -> None:
    result = apply_template(STATE_DICT)
    assert result.viewer_state.to_json() == ViewerState(STATE_DICT).to_json()
    assert result.config == {}
