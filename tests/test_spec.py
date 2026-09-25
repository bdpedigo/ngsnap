import json
from pathlib import Path

from neuroglancer.viewer_state import ViewerState

from ngsnap import Spec, SpecError, apply, parse_state, to_url
from ngsnap.state import DEFAULT_PREFIX
from ngsnap.template import TemplatedState

STATE_DICT = {
    "layers": [
        {"type": "image", "source": "precomputed://gs://example/img", "name": "img"},
        {
            "type": "segmentation",
            "source": "precomputed://gs://example/seg",
            "name": "seg",
            "visible": False,
        },
    ],
    "layout": "xy",
}

DEFAULT_TOML = Path(__file__).parent.parent / "src/ngsnap/styles/default.toml"


def test_default_hides_ui_and_sets_size_background_scalebar() -> None:
    result = Spec.default().apply(STATE_DICT)
    config = result.config
    assert config["showUIControls"] is False
    assert config["showPanelBorders"] is False
    assert config["viewerSize"] == [1600, 1200]
    assert config["scaleBarOptions"]["scaleFactor"] == 1
    viewer = result.viewer_state.to_json()
    assert viewer["showScaleBar"] is True
    assert viewer["crossSectionBackgroundColor"] == "#000000"
    assert viewer["projectionBackgroundColor"] == "#000000"


def test_default_closes_side_panels() -> None:
    state = {
        **STATE_DICT,
        "selectedLayer": {"layer": "seg", "visible": True, "size": 259},
        "selection": {"size": 259},
        "settingsPanel": {"visible": True},
    }
    viewer = Spec.default().apply(state).viewer_state.to_json()
    assert viewer["selectedLayer"]["visible"] is False
    assert viewer["selection"]["visible"] is False
    assert viewer["settingsPanel"]["visible"] is False


def test_apply_returns_templated_state() -> None:
    result = Spec.default().apply(STATE_DICT)
    assert isinstance(result, TemplatedState)
    assert isinstance(result.viewer_state, ViewerState)
    assert result.config != {}


def test_apply_does_not_mutate_input() -> None:
    state = ViewerState(STATE_DICT)
    before = state.to_json()
    Spec.default().apply(state)
    assert state.to_json() == before


def test_respected_layer_visibility_survives() -> None:
    spec = Spec.default()
    assert "layers[].visible" in spec.respects
    result = spec.apply(STATE_DICT)
    layers = {layer["name"]: layer for layer in result.viewer_state.to_json()["layers"]}
    assert layers["seg"]["visible"] is False


def test_overrides_are_declared() -> None:
    overrides = Spec.default().overrides
    assert "showScaleBar" in overrides
    assert "viewerSize" in overrides


def test_render_time_setting_changes_canonical_serialization() -> None:
    base = Spec.default()
    bigger = Spec(
        template=base.template,
        config={**base.config, "viewerSize": [3200, 2400]},
        respects=base.respects,
    )
    assert base.to_json() != bigger.to_json()


def test_from_file_matches_default() -> None:
    loaded = Spec.from_file(DEFAULT_TOML)
    assert loaded.to_json() == Spec.default().to_json()


def test_from_file_missing_raises_spec_error() -> None:
    try:
        Spec.from_file("does/not/exist.toml")
    except SpecError:
        return
    raise AssertionError("expected SpecError")


def test_from_file_rejects_non_table_template(tmp_path: Path) -> None:
    bad = tmp_path / "bad.toml"
    bad.write_text('template = "not a table"\n', encoding="utf-8")
    try:
        Spec.from_file(bad)
    except SpecError:
        return
    raise AssertionError("expected SpecError")


def test_to_json_is_deterministic() -> None:
    first = Spec.default().to_json()
    second = Spec.default().to_json()
    assert first == second
    assert json.loads(first)["config"]["viewerSize"] == [1600, 1200]


def test_apply_url_returns_url() -> None:
    url = to_url(STATE_DICT, prefix=DEFAULT_PREFIX)
    result = apply(url, Spec.default())
    assert isinstance(result, str)
    assert result.startswith(DEFAULT_PREFIX + "#!")
    restyled = parse_state(result).to_json()
    assert restyled["showScaleBar"] is True


def test_apply_json_string_returns_json_string() -> None:
    result = apply(json.dumps(STATE_DICT), Spec.default())
    assert isinstance(result, str)
    assert json.loads(result)["showScaleBar"] is True


def test_apply_mapping_returns_dict() -> None:
    result = apply(STATE_DICT, Spec.default())
    assert isinstance(result, dict)
    assert result["showScaleBar"] is True
    assert result["crossSectionBackgroundColor"] == "#000000"


def test_apply_accepts_anonymous_dict_spec() -> None:
    result = apply(STATE_DICT, {"showAxisLines": True})
    assert isinstance(result, dict)
    assert result["showAxisLines"] is True


def test_apply_accepts_toml_path_spec() -> None:
    result = apply(STATE_DICT, DEFAULT_TOML)
    assert isinstance(result, dict)
    assert result["showScaleBar"] is True


def test_apply_drops_render_only_config() -> None:
    result = apply(STATE_DICT, Spec.default())
    assert isinstance(result, dict)
    assert "showUIControls" not in result
    assert "viewerSize" not in result
