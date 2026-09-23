"""Deployment-scoped classification of Neuroglancer state properties into named groups.

A setting group names a subset of a viewer state's properties for the Neuroglancer
deployment the team uses. Extraction lifts one group out of a source state into a
template (the same partial-dict shape :mod:`ngsnap.template` deep-merges), so a
group can be saved as a spec and re-applied to other states.

Top-level keys map to top-level template keys; per-layer keys are collected per
layer and keyed by layer name, matching the ``layers`` mapping the templating
interface understands. A layer's ``name`` is the addressing key, not a group
member. Any property not listed in a group is unclassified: it is never included
in an extract (dropped), never silently folded into another group.
"""

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from ngsnap.errors import SpecError


@dataclass(frozen=True)
class SettingGroup:
    """A named subset of state properties: top-level keys and per-layer keys."""

    name: str
    top_level: frozenset[str]
    layer: frozenset[str]


CAMERA = SettingGroup(
    name="camera",
    top_level=frozenset(
        {
            "position",
            "crossSectionScale",
            "crossSectionDepth",
            "crossSectionOrientation",
            "projectionScale",
            "projectionDepth",
            "projectionOrientation",
        }
    ),
    layer=frozenset(),
)

APPEARANCE = SettingGroup(
    name="appearance",
    top_level=frozenset(
        {
            "showSlices",
            "hideCrossSectionBackground3D",
            "showAxisLines",
            "wireFrame",
            "showScaleBar",
            "showDefaultAnnotations",
            "crossSectionBackgroundColor",
            "projectionBackgroundColor",
            "layout",
            "partialViewport",
            "relativeDisplayScales",
            "displayDimensions",
        }
    ),
    layer=frozenset(
        {
            "shader",
            "shaderControls",
            "opacity",
            "blend",
            "colorSeed",
            "segmentColors",
            "segmentDefaultColor",
            "objectAlpha",
            "selectedAlpha",
            "notSelectedAlpha",
            "saturation",
            "meshRenderScale",
            "crossSectionRenderScale",
            "meshSilhouetteRendering",
            "hideSegmentZero",
            "baseSegmentColoring",
            "hoverHighlight",
            "ignoreNullVisibleSet",
            "annotationColor",
            "volumeRendering",
            "volumeRenderingGain",
            "volumeRenderingDepthSamples",
            "linkedSegmentationColorGroup",
        }
    ),
)

SOURCES = SettingGroup(
    name="sources",
    top_level=frozenset({"dimensions"}),
    layer=frozenset(
        {
            "type",
            "source",
            "localDimensions",
            "localPosition",
            "linkedSegmentationGroup",
        }
    ),
)

SELECTION = SettingGroup(
    name="selection",
    top_level=frozenset({"selectedLayer"}),
    layer=frozenset({"visible", "archived", "segments", "pick"}),
)

GROUPS: dict[str, SettingGroup] = {
    group.name: group for group in (APPEARANCE, SOURCES, SELECTION, CAMERA)
}
"""The named setting groups for the current deployment, keyed by name."""


def extract_group(state: Mapping[str, Any], group: str) -> dict[str, Any]:
    """Lift one setting group out of a state into a template dict.

    Returns a partial dict in the shape :func:`ngsnap.template.apply_template`
    deep-merges over a state: top-level group keys become top-level keys, and
    per-layer group keys are collected per layer under ``layers`` keyed by name.
    Unclassified properties are dropped. Raises :class:`SpecError` for an unknown
    group name.
    """
    try:
        setting_group = GROUPS[group]
    except KeyError:
        known = ", ".join(sorted(GROUPS))
        raise SpecError(
            f"Unknown setting group {group!r}; known groups: {known}"
        ) from None

    template: dict[str, Any] = {
        key: deepcopy(state[key]) for key in setting_group.top_level if key in state
    }

    layers = state.get("layers")
    if setting_group.layer and isinstance(layers, list):
        layer_overrides: dict[str, dict[str, Any]] = {}
        for layer in layers:
            if not isinstance(layer, Mapping) or "name" not in layer:
                continue
            picked = {
                key: deepcopy(layer[key]) for key in setting_group.layer if key in layer
            }
            if picked:
                layer_overrides[layer["name"]] = picked
        if layer_overrides:
            template["layers"] = layer_overrides

    return template
