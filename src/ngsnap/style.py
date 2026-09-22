"""House style: a viewer-state template plus render-time config, applied via templating."""

import json
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ngsnap.errors import StyleError
from ngsnap.state import StateInput
from ngsnap.template import TemplatedState, apply_template


@dataclass(frozen=True)
class Style:
    """An opinionated look applied to a state through the templating interface.

    A style is task-4's two output objects up front: a viewer-state ``template``
    and render-time ``config`` overrides. ``respects`` names the state elements the
    style deliberately leaves to the author. Applying a style never mutates the input.
    """

    template: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    respects: tuple[str, ...] = ()

    @classmethod
    def default(cls) -> "Style":
        """The single opinionated default style (P5)."""
        return cls(
            template={
                "showScaleBar": True,
                "showAxisLines": False,
                "showDefaultAnnotations": False,
                "crossSectionBackgroundColor": "#000000",
                "projectionBackgroundColor": "#000000",
            },
            config={
                "showUIControls": False,
                "showPanelBorders": False,
                "viewerSize": [1600, 1200],
                "scaleBarOptions": {"scaleFactor": 1},
            },
            respects=(
                "layers[].visible",
                "layers[].segments",
                "position",
                "crossSectionScale",
                "projectionScale",
            ),
        )

    @classmethod
    def from_file(cls, path: str | Path) -> "Style":
        """Load a style from a TOML file with ``template``, ``config``, and ``respects``."""
        file_path = Path(path)
        try:
            text = file_path.read_text(encoding="utf-8")
        except OSError as error:
            raise StyleError(
                f"Cannot read style file {str(file_path)!r}: {error}"
            ) from error
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            raise StyleError(
                f"Invalid TOML in style file {str(file_path)!r}: {error}"
            ) from error
        return cls._from_mapping(data)

    @classmethod
    def _from_mapping(cls, data: Mapping[str, Any]) -> "Style":
        template = data.get("template", {})
        config = data.get("config", {})
        respects = data.get("respects", [])
        if not isinstance(template, Mapping):
            raise StyleError("Style 'template' must be a table")
        if not isinstance(config, Mapping):
            raise StyleError("Style 'config' must be a table")
        if not isinstance(respects, list):
            raise StyleError("Style 'respects' must be an array")
        return cls(
            template=dict(template),
            config=dict(config),
            respects=tuple(respects),
        )

    @property
    def overrides(self) -> tuple[str, ...]:
        """The state elements this style sets, derived from the template and config keys."""
        return tuple(sorted({*self.template, *self.config}))

    def apply(self, source: StateInput) -> TemplatedState:
        """Apply the style to a state via task-4's templating interface (P15)."""
        return apply_template(source, self.template, config=self.config)

    def to_json(self) -> str:
        """Canonical JSON of the whole style, stable for use in a cache key (P7)."""
        return json.dumps(
            {
                "template": self.template,
                "config": self.config,
                "respects": sorted(self.respects),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
