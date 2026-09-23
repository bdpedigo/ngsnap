"""Spec: a viewer-state template plus render-time config, applied via templating."""

import json
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomli_w

from ngsnap.errors import SpecError
from ngsnap.groups import extract_group
from ngsnap.state import StateInput, looks_like_url, parse_state
from ngsnap.template import TemplatedState, apply_template


@dataclass(frozen=True)
class Spec:
    """An opinionated set of state properties applied through the templating interface.

    A spec is two objects up front: a viewer-state ``template`` and render-time
    ``config`` overrides. ``respects`` names the state elements the spec deliberately
    leaves to the author. Applying a spec never mutates the input.
    """

    template: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    respects: tuple[str, ...] = ()

    @classmethod
    def default(cls) -> "Spec":
        """The single opinionated default spec (P5)."""
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
    def from_file(cls, path: str | Path) -> "Spec":
        """Load a spec from a TOML file with ``template``, ``config``, and ``respects``."""
        file_path = Path(path)
        try:
            text = file_path.read_text(encoding="utf-8")
        except OSError as error:
            raise SpecError(
                f"Cannot read spec file {str(file_path)!r}: {error}"
            ) from error
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            raise SpecError(
                f"Invalid TOML in spec file {str(file_path)!r}: {error}"
            ) from error
        return cls._from_mapping(data)

    @classmethod
    def _from_mapping(cls, data: Mapping[str, Any]) -> "Spec":
        template = data.get("template", {})
        config = data.get("config", {})
        respects = data.get("respects", [])
        if not isinstance(template, Mapping):
            raise SpecError("Spec 'template' must be a table")
        if not isinstance(config, Mapping):
            raise SpecError("Spec 'config' must be a table")
        if not isinstance(respects, list):
            raise SpecError("Spec 'respects' must be an array")
        return cls(
            template=dict(template),
            config=dict(config),
            respects=tuple(respects),
        )

    @classmethod
    def from_state(cls, source: StateInput, group: str) -> "Spec":
        """Extract one setting group from a state into a reusable spec.

        Parses ``source`` (link, JSON, file, or dict) and lifts the named group
        (see :mod:`ngsnap.groups`) into the spec's ``template``. Unclassified
        properties are dropped. The result applies through the same templating
        path as any spec, so ``spec.apply(source)`` reproduces the extracted
        properties. Raises :class:`SpecError` for an unknown group name.
        """
        state = parse_state(source).to_json()
        return cls(template=extract_group(state, group))

    @property
    def overrides(self) -> tuple[str, ...]:
        """The state elements this spec sets, derived from the template and config keys."""
        return tuple(sorted({*self.template, *self.config}))

    def apply(self, source: StateInput) -> TemplatedState:
        """Apply the spec to a state, returning the lower-level templated result (P15)."""
        return apply_template(source, self.template, config=self.config)

    def to_json(self) -> str:
        """Canonical JSON of the whole spec, stable for use in a cache key (P7)."""
        return json.dumps(
            {
                "template": self.template,
                "config": self.config,
                "respects": sorted(self.respects),
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    def to_toml(self) -> str:
        """Serialize the spec as TOML with ``template``, ``config``, and ``respects``.

        The output is a spec file :meth:`from_file` reloads. Empty sections are
        omitted so an extracted single-group spec stays minimal.
        """
        document: dict[str, Any] = {}
        if self.respects:
            document["respects"] = sorted(self.respects)
        if self.template:
            document["template"] = self.template
        if self.config:
            document["config"] = self.config
        return tomli_w.dumps(document)

    def to_file(self, path: str | Path) -> None:
        """Write the spec as a TOML file that :meth:`from_file` can reload."""
        Path(path).write_text(self.to_toml(), encoding="utf-8")


type SpecInput = Spec | Mapping[str, Any] | str | Path


def _coerce_spec(spec: SpecInput | None) -> Spec:
    """Normalize a spec argument: a Spec, a plain mapping, or a TOML file path."""
    if spec is None:
        return Spec.default()
    if isinstance(spec, Spec):
        return spec
    if isinstance(spec, Mapping):
        return Spec(template=dict(spec))
    if isinstance(spec, (str, Path)):
        return Spec.from_file(spec)
    raise SpecError(f"Unsupported spec type: {type(spec).__name__}")


def apply(source: StateInput, spec: SpecInput | None = None) -> str | dict[str, Any]:
    """Restyle ``source`` with ``spec``, returning the same shape as the input.

    A URL string returns a restyled URL string (its host prefix preserved), a JSON
    string returns a canonical JSON string, and a mapping, ``ViewerState``, or file
    input returns a restyled JSON object. ``spec`` may be a :class:`Spec`, a plain
    mapping (an anonymous template), or a path to a TOML spec file. Render-time
    ``config`` is not part of a state and is dropped from the output.
    """
    templated = _coerce_spec(spec).apply(source)
    if isinstance(source, str):
        text = source.strip()
        if looks_like_url(text):
            return templated.to_url()
        if text[:1] in "{[":
            return templated.to_json()
    return templated.viewer_state.to_json()
