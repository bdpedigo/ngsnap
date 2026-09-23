import json
from pathlib import Path

from ngsnap import GROUPS, Spec, SpecError, apply, extract_group

MULTI_LAYER_STATE = {
    "dimensions": {"x": [4e-9, "m"], "y": [4e-9, "m"], "z": [40e-9, "m"]},
    "position": [1000, 2000, 30],
    "crossSectionScale": 2.5,
    "projectionScale": 4096,
    "projectionOrientation": [0.1, 0.2, 0.3, 0.9],
    "showScaleBar": True,
    "showAxisLines": False,
    "crossSectionBackgroundColor": "#000000",
    "layout": "xy-3d",
    "selectedLayer": {"layer": "seg", "visible": True},
    "layers": [
        {
            "type": "image",
            "source": "precomputed://gs://example/img",
            "name": "img",
            "shader": "#uicontrol float x\nvoid main(){}",
            "opacity": 0.75,
            "blend": "default",
        },
        {
            "type": "segmentation",
            "source": "precomputed://gs://example/seg",
            "name": "seg",
            "visible": False,
            "segments": ["123", "456"],
            "colorSeed": 42,
            "objectAlpha": 0.9,
            "selectedAlpha": 0.5,
        },
    ],
}


def test_known_groups_cover_required_names() -> None:
    assert {"appearance", "sources", "selection", "camera"} <= set(GROUPS)


def test_extract_appearance_includes_appearance_properties() -> None:
    template = extract_group(MULTI_LAYER_STATE, "appearance")
    assert template["showScaleBar"] is True
    assert template["showAxisLines"] is False
    assert template["crossSectionBackgroundColor"] == "#000000"
    assert template["layout"] == "xy-3d"
    assert template["layers"]["img"]["shader"].startswith("#uicontrol")
    assert template["layers"]["img"]["opacity"] == 0.75
    assert template["layers"]["seg"]["colorSeed"] == 42
    assert template["layers"]["seg"]["objectAlpha"] == 0.9


def test_extract_appearance_excludes_sources_selection_camera() -> None:
    template = extract_group(MULTI_LAYER_STATE, "appearance")
    assert "position" not in template
    assert "crossSectionScale" not in template
    assert "projectionScale" not in template
    assert "dimensions" not in template
    assert "selectedLayer" not in template
    for layer in template["layers"].values():
        assert "source" not in layer
        assert "segments" not in layer
        assert "visible" not in layer
        assert "type" not in layer


def test_extract_sources_selection_camera_partition() -> None:
    sources = extract_group(MULTI_LAYER_STATE, "sources")
    assert sources["layers"]["img"]["source"] == "precomputed://gs://example/img"
    assert sources["layers"]["seg"]["type"] == "segmentation"
    assert "dimensions" in sources

    selection = extract_group(MULTI_LAYER_STATE, "selection")
    assert selection["layers"]["seg"]["segments"] == ["123", "456"]
    assert selection["layers"]["seg"]["visible"] is False
    assert selection["selectedLayer"] == {"layer": "seg", "visible": True}

    camera = extract_group(MULTI_LAYER_STATE, "camera")
    assert camera["position"] == [1000, 2000, 30]
    assert camera["crossSectionScale"] == 2.5


def test_extract_does_not_mutate_input() -> None:
    before = json.loads(json.dumps(MULTI_LAYER_STATE))
    extract_group(MULTI_LAYER_STATE, "appearance")
    assert before == MULTI_LAYER_STATE


def test_unclassified_property_is_dropped() -> None:
    state = {**MULTI_LAYER_STATE, "title": "my find", "gpuMemoryLimit": 2_000_000_000}
    for group in GROUPS:
        template = extract_group(state, group)
        assert "title" not in template
        assert "gpuMemoryLimit" not in template


def test_from_state_unknown_group_raises() -> None:
    try:
        Spec.from_state(MULTI_LAYER_STATE, "nonsense")
    except SpecError:
        return
    raise AssertionError("expected SpecError")


def test_from_state_appearance_round_trip_is_idempotent() -> None:
    spec = Spec.from_state(MULTI_LAYER_STATE, "appearance")
    applied = spec.apply(MULTI_LAYER_STATE).viewer_state.to_json()
    layers = {layer["name"]: layer for layer in applied["layers"]}

    assert applied["showScaleBar"] is True
    assert applied["crossSectionBackgroundColor"] == "#000000"
    assert layers["img"]["opacity"] == 0.75
    assert layers["seg"]["colorSeed"] == 42

    reapplied = spec.apply(applied).viewer_state.to_json()
    assert reapplied == applied


def test_from_state_appearance_leaves_sources_and_selection_intact() -> None:
    applied = Spec.from_state(MULTI_LAYER_STATE, "appearance").apply(MULTI_LAYER_STATE)
    result = applied.viewer_state.to_json()
    layers = {layer["name"]: layer for layer in result["layers"]}
    assert layers["seg"]["source"] == "precomputed://gs://example/seg"
    assert layers["seg"]["segments"] == ["123", "456"]
    assert result["position"] == [1000, 2000, 30]


def test_extract_to_toml_reloads_via_from_file(tmp_path: Path) -> None:
    spec = Spec.from_state(MULTI_LAYER_STATE, "appearance")
    spec_path = tmp_path / "appearance.toml"
    spec.to_file(spec_path)
    reloaded = Spec.from_file(spec_path)
    assert reloaded.to_json() == spec.to_json()

    result = apply(MULTI_LAYER_STATE, spec_path)
    assert isinstance(result, dict)
    assert result["showScaleBar"] is True
    layers = {layer["name"]: layer for layer in result["layers"]}
    assert layers["img"]["opacity"] == 0.75
