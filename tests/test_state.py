import io
import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from neuroglancer.viewer_state import ViewerState

from ngsnap import StateInputError, parse_state, to_url

STATE_DICT = {
    "layers": [
        {"type": "image", "source": "precomputed://gs://example/img", "name": "img"}
    ],
    "layout": "xy",
}


def _canonical() -> dict:
    return ViewerState(STATE_DICT).to_json()


def test_parse_from_viewer_state_returns_state() -> None:
    state = ViewerState(STATE_DICT)
    assert parse_state(state) is state


def test_parse_from_dict() -> None:
    assert parse_state(STATE_DICT).to_json() == _canonical()


def test_parse_from_json_string() -> None:
    assert parse_state(json.dumps(STATE_DICT)).to_json() == _canonical()


def test_parse_from_file(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text(json.dumps(STATE_DICT), encoding="utf-8")
    assert parse_state(path).to_json() == _canonical()
    # Same result when passed as a string path.
    assert parse_state(str(path)).to_json() == _canonical()


def test_parse_from_url() -> None:
    url = to_url(STATE_DICT)
    assert parse_state(url).to_json() == _canonical()


def test_three_host_prefixes_parse_equal() -> None:
    fragment = to_url(STATE_DICT).split("#", 1)[1]
    hosts = [
        "https://neuroglancer-demo.appspot.com/",
        "https://spelunker.cave-explorer.org/",
        "https://neuroglancer.example.org/ng/",
    ]
    states = [parse_state(host + "#" + fragment) for host in hosts]
    for state in states:
        assert state == states[0]
        assert state == ViewerState(STATE_DICT)


def test_round_trip_with_custom_prefix() -> None:
    prefix = "https://custom.example.org/ng"
    url = to_url(STATE_DICT, prefix=prefix)
    assert url.startswith(prefix + "#!")
    assert parse_state(url) == parse_state(to_url(parse_state(url), prefix=prefix))


@contextmanager
def _fake_response(payload: bytes) -> Iterator[io.BytesIO]:
    yield io.BytesIO(payload)


def test_fetch_public_remote_state(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    def fake_urlopen(url, timeout):  # noqa: ANN001, ANN202
        calls["url"] = url
        calls["timeout"] = timeout
        return _fake_response(json.dumps(STATE_DICT).encode("utf-8"))

    monkeypatch.setattr("ngsnap.state.urllib.request.urlopen", fake_urlopen)
    url = "https://neuroglancer-demo.appspot.com/#!https://state.example.org/v1/42"
    assert parse_state(url).to_json() == _canonical()
    assert calls["url"] == "https://state.example.org/v1/42"


def test_fetch_remote_network_error_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    import urllib.error

    def fake_urlopen(url, timeout):  # noqa: ANN001, ANN202
        raise urllib.error.URLError("boom")

    monkeypatch.setattr("ngsnap.state.urllib.request.urlopen", fake_urlopen)
    url = "https://host/#!https://state.example.org/v1/42"
    with pytest.raises(StateInputError, match="Failed to fetch remote state"):
        parse_state(url)


def test_fetch_remote_non_json_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(url, timeout):  # noqa: ANN001, ANN202
        return _fake_response(b"<html>not json</html>")

    monkeypatch.setattr("ngsnap.state.urllib.request.urlopen", fake_urlopen)
    url = "https://host/#!https://state.example.org/v1/42"
    with pytest.raises(StateInputError, match="not valid JSON"):
        parse_state(url)


def test_auth_backed_remote_state_rejected() -> None:
    url = "https://spelunker.cave-explorer.org/#!middleauth+https://global.daf-apis.com/nglstate/api/v1/42"
    with pytest.raises(StateInputError, match="authentication-backed"):
        parse_state(url)


def test_empty_string_raises() -> None:
    with pytest.raises(StateInputError, match="empty"):
        parse_state("   ")


def test_invalid_json_string_raises() -> None:
    with pytest.raises(StateInputError, match="Invalid JSON"):
        parse_state('{"layers": [}')


def test_non_object_json_raises() -> None:
    with pytest.raises(StateInputError, match="must be an object"):
        parse_state("[1, 2, 3]")


def test_missing_file_raises() -> None:
    with pytest.raises(StateInputError, match="Cannot read state file"):
        parse_state("does-not-exist.json")


def test_url_without_fragment_raises() -> None:
    with pytest.raises(StateInputError, match="no state fragment"):
        parse_state("https://neuroglancer-demo.appspot.com/")


def test_unsupported_type_raises() -> None:
    with pytest.raises(StateInputError, match="Unsupported state input type"):
        parse_state(42)  # type: ignore[arg-type]
