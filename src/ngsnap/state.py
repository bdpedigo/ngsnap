"""Parse and normalize Neuroglancer state input into a canonical ViewerState."""

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from neuroglancer import url_state
from neuroglancer.viewer_state import ViewerState

from ngsnap.errors import StateInputError

type StateInput = str | Path | Mapping[str, Any] | ViewerState

DEFAULT_PREFIX = url_state.default_neuroglancer_url

_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
_FETCH_TIMEOUT = 30


def parse_state(source: StateInput) -> ViewerState:
    """Normalize a Neuroglancer state into a ViewerState.

    Accepts a Neuroglancer URL, a JSON string, a path to a JSON file, a mapping,
    or an existing ViewerState. Raises StateInputError for anything malformed.
    """
    if isinstance(source, ViewerState):
        return source
    if isinstance(source, Mapping):
        return _from_json_data(dict(source))
    if isinstance(source, Path):
        return _load_from_file(source)
    if isinstance(source, str):
        text = source.strip()
        if not text:
            raise StateInputError("State input string is empty")
        if _SCHEME_RE.match(text) or text.startswith("#!"):
            return _load_from_url(text)
        if text.startswith(("{", "[")):
            return _from_json_string(text)
        return _load_from_file(Path(source))
    raise StateInputError(f"Unsupported state input type: {type(source).__name__}")


def to_url(source: StateInput, prefix: str = DEFAULT_PREFIX) -> str:
    """Encode a normalized state as a Neuroglancer URL with a configurable host prefix."""
    state = parse_state(source)
    return url_state.to_url(state, prefix=prefix)


def _from_json_data(data: Mapping[str, Any]) -> ViewerState:
    try:
        return ViewerState(dict(data))
    except Exception as error:
        raise StateInputError(f"Invalid Neuroglancer state object: {error}") from error


def _from_json_string(text: str) -> ViewerState:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise StateInputError(f"Invalid JSON state string: {error}") from error
    if not isinstance(data, Mapping):
        raise StateInputError(
            f"JSON state must be an object, got {type(data).__name__}"
        )
    return _from_json_data(data)


def _load_from_file(path: Path) -> ViewerState:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise StateInputError(
            f"Cannot read state file {str(path)!r}: {error}"
        ) from error
    return _from_json_string(text)


def _load_from_url(url: str) -> ViewerState:
    fragment = urllib.parse.urlparse(url).fragment
    if not fragment:
        raise StateInputError(f"URL has no state fragment (expected '#!...'): {url!r}")
    reference = urllib.parse.unquote(fragment).removeprefix("!").strip()
    if reference.startswith("{"):
        try:
            return url_state.parse_url_fragment(fragment)
        except Exception as error:
            raise StateInputError(
                f"Invalid Neuroglancer state fragment in URL: {error}"
            ) from error
    return _load_remote_state(reference)


def _load_remote_state(reference: str) -> ViewerState:
    lower = reference.lower()
    if lower.startswith(("http://", "https://")):
        return _fetch_json_state(reference)
    # NOTE: auth-backed states (middleauth+, gs://, etc.) are rejected for now; a
    # future feature will fetch them via caveclient + a token from the environment.
    raise StateInputError(
        "State link points to an authentication-backed remote state "
        f"({reference!r}); fetching auth-backed states is not yet supported. "
        "Provide the inline JSON state instead."
    )


def _fetch_json_state(url: str) -> ViewerState:
    try:
        with urllib.request.urlopen(url, timeout=_FETCH_TIMEOUT) as response:
            payload = response.read()
    except (urllib.error.URLError, OSError) as error:
        raise StateInputError(
            f"Failed to fetch remote state from {url!r}: {error}"
        ) from error
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as error:
        raise StateInputError(
            f"Remote state at {url!r} is not valid JSON: {error}"
        ) from error
    if not isinstance(data, Mapping):
        raise StateInputError(
            f"Remote state at {url!r} must be a JSON object, got {type(data).__name__}"
        )
    return _from_json_data(data)
