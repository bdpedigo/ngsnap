import json

from ngsnap import Spec, cache_key, to_url

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
    "showAxisLines": True,
}


def test_key_is_short_hex_string() -> None:
    key = cache_key(STATE_DICT)
    assert isinstance(key, str)
    assert 0 < len(key) <= 64
    assert all(c in "0123456789abcdef" for c in key)


def test_key_is_stable_across_calls() -> None:
    assert cache_key(STATE_DICT) == cache_key(STATE_DICT)


def test_key_ignores_host_prefix() -> None:
    url_a = to_url(STATE_DICT, prefix="https://neuroglancer.example/")
    url_b = to_url(STATE_DICT, prefix="https://another-host.test/viewer/")
    assert cache_key(url_a) == cache_key(url_b)


def test_key_ignores_key_order() -> None:
    reordered = {
        "showAxisLines": True,
        "layout": "xy",
        "layers": STATE_DICT["layers"],
    }
    assert cache_key(STATE_DICT) == cache_key(reordered)


def test_key_ignores_url_quoting() -> None:
    fragment = "#!" + json.dumps(STATE_DICT)
    raw = "https://neuroglancer.example/" + fragment
    quoted = to_url(STATE_DICT, prefix="https://neuroglancer.example/")
    assert cache_key(raw) == cache_key(quoted)


def test_changing_non_overridden_element_changes_key() -> None:
    changed = {**STATE_DICT, "layout": "3d"}
    assert cache_key(changed) != cache_key(STATE_DICT)


def test_changing_overridden_element_does_not_change_key() -> None:
    # The default spec overrides showAxisLines, so toggling it in the input
    # produces the same rendered output and therefore the same key.
    spec = Spec.default()
    with_true = {**STATE_DICT, "showAxisLines": True}
    with_false = {**STATE_DICT, "showAxisLines": False}
    assert cache_key(with_true, spec) == cache_key(with_false, spec)


def test_changing_spec_template_changes_key() -> None:
    base = Spec(template={"showAxisLines": False})
    other = Spec(template={"showAxisLines": True})
    assert cache_key(STATE_DICT, base) != cache_key(STATE_DICT, other)


def test_changing_spec_config_changes_key() -> None:
    base = Spec(config={"viewerSize": [800, 600]})
    other = Spec(config={"viewerSize": [1600, 1200]})
    assert cache_key(STATE_DICT, base) != cache_key(STATE_DICT, other)


def test_default_spec_differs_from_empty_spec() -> None:
    assert cache_key(STATE_DICT) != cache_key(STATE_DICT, Spec())
