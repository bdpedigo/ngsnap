"""Swap named elements of a Neuroglancer state via a partial-dict template."""

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Final

from neuroglancer.viewer_config_state import ConfigState
from neuroglancer.viewer_state import ViewerState

from ngsnap.errors import StateTemplateError
from ngsnap.state import DEFAULT_PREFIX, StateInput, parse_state, to_url


class _Remove:
    __slots__ = ()

    def __repr__(self) -> str:
        return "REMOVE"


REMOVE: Final = _Remove()
"""Template sentinel: delete the key (or named layer) it is assigned to."""

type Template = Mapping[str, Any]


@dataclass(frozen=True)
class TemplatedState:
    """A viewer state plus separate client config-state overrides.

    The two are kept apart because only the viewer state can be encoded into a
    Neuroglancer URL; config-state knobs live in the client and are applied by
    the render path.
    """

    viewer_state: ViewerState
    config: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Canonical JSON string of the viewer state, stable across identical inputs."""
        return json.dumps(
            self.viewer_state.to_json(), sort_keys=True, separators=(",", ":")
        )

    def to_url(self, prefix: str = DEFAULT_PREFIX) -> str:
        """Neuroglancer URL for the viewer state with a configurable host prefix."""
        return to_url(self.viewer_state, prefix=prefix)


def apply_template(
    source: StateInput,
    template: Template | None = None,
    *,
    config: Template | None = None,
) -> TemplatedState:
    """Return a new state with only the named elements replaced.

    ``template`` is deep-merged over the viewer state: mappings recurse, other
    values overwrite, and ``REMOVE`` deletes a key. A ``layers`` mapping keyed by
    layer name patches (or adds, or with ``REMOVE`` deletes) individual layers.
    ``config`` carries client config-state overrides and is returned separately.
    The input state is never mutated.
    """
    base = parse_state(source).to_json()
    merged = _deep_merge(base, template) if template else base
    try:
        viewer_state = ViewerState(merged)
    except Exception as error:
        raise StateTemplateError(
            f"Template produced an invalid viewer state: {error}"
        ) from error
    return TemplatedState(viewer_state=viewer_state, config=_build_config(config))


def _build_config(config: Template | None) -> dict[str, Any]:
    if not config:
        return {}
    overrides = _clone(config)
    try:
        return ConfigState(overrides).to_json()
    except Exception as error:
        raise StateTemplateError(
            f"Template produced an invalid config state: {error}"
        ) from error


def _deep_merge(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in overlay.items():
        if value is REMOVE:
            result.pop(key, None)
        elif key == "layers" and isinstance(value, Mapping):
            result["layers"] = _merge_layers(result.get("layers", []), value)
        elif isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = _clone(value)
    return result


def _merge_layers(
    base_layers: object, overlay: Mapping[str, Any]
) -> list[dict[str, Any]]:
    if not isinstance(base_layers, list):
        raise StateTemplateError(
            f"Cannot address layers by name: 'layers' is {type(base_layers).__name__},"
            " not a list"
        )
    layers: list[dict[str, Any] | None] = [dict(layer) for layer in base_layers]
    index = {
        layer["name"]: i for i, layer in enumerate(layers) if layer and "name" in layer
    }
    for name, patch in overlay.items():
        position = index.get(name)
        if patch is REMOVE:
            if position is not None:
                layers[position] = None
            continue
        if not isinstance(patch, Mapping):
            raise StateTemplateError(
                f"Layer override for {name!r} must be a mapping or REMOVE, got "
                f"{type(patch).__name__}"
            )
        if position is None:
            new_layer = _deep_merge({}, patch)
            new_layer.setdefault("name", name)
            index[name] = len(layers)
            layers.append(new_layer)
        else:
            current = layers[position]
            assert current is not None
            layers[position] = _deep_merge(current, patch)
    return [layer for layer in layers if layer is not None]


def _clone(value: object) -> object:
    if isinstance(value, Mapping):
        return {k: _clone(v) for k, v in value.items() if v is not REMOVE}
    if isinstance(value, list):
        return [_clone(item) for item in value]
    return value
