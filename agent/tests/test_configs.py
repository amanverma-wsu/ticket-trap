"""Unit tests for the three defense configurations. Pure data, no network."""
import pytest

from agent.configs import CONFIGS, UNTRUSTED_NOTE, get_config


def test_exactly_three_configs():
    assert set(CONFIGS) == {"baseline", "prompt_only", "app_enforced"}


def test_baseline_has_no_untrusted_note_and_no_enforcement():
    c = get_config("baseline")
    assert UNTRUSTED_NOTE not in c.system_prompt
    assert c.enforce_permissions is False


def test_prompt_only_has_note_but_no_enforcement():
    c = get_config("prompt_only")
    assert UNTRUSTED_NOTE in c.system_prompt
    assert c.enforce_permissions is False


def test_app_enforced_has_note_and_enforcement():
    c = get_config("app_enforced")
    assert UNTRUSTED_NOTE in c.system_prompt
    assert c.enforce_permissions is True


def test_only_app_enforced_enforces():
    enforcing = [name for name, c in CONFIGS.items() if c.enforce_permissions]
    assert enforcing == ["app_enforced"]


def test_each_config_name_matches_key():
    for name, c in CONFIGS.items():
        assert c.name == name


def test_get_config_rejects_unknown():
    with pytest.raises(KeyError):
        get_config("nope")
