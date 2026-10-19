import pytest
from django.core.exceptions import ImproperlyConfigured

from config.settings import _env_bool, _env_non_negative_int


@pytest.mark.parametrize("value", ["1", "true", "YES", "on"])
def test_env_bool_accepts_true_spellings(monkeypatch, value):
    monkeypatch.setenv("TEST_SECURITY_FLAG", value)
    assert _env_bool("TEST_SECURITY_FLAG") is True


@pytest.mark.parametrize("value", ["0", "false", "NO", "off"])
def test_env_bool_accepts_false_spellings(monkeypatch, value):
    monkeypatch.setenv("TEST_SECURITY_FLAG", value)
    assert _env_bool("TEST_SECURITY_FLAG", True) is False


def test_env_bool_rejects_ambiguous_values(monkeypatch):
    monkeypatch.setenv("TEST_SECURITY_FLAG", "sometimes")
    with pytest.raises(ImproperlyConfigured, match="must be a boolean"):
        _env_bool("TEST_SECURITY_FLAG")


@pytest.mark.parametrize("value", ["0", "12"])
def test_non_negative_int_accepts_valid_values(monkeypatch, value):
    monkeypatch.setenv("TEST_SECURITY_SECONDS", value)
    assert _env_non_negative_int("TEST_SECURITY_SECONDS", 7) == int(value)


@pytest.mark.parametrize("value", ["-1", "forever"])
def test_non_negative_int_rejects_invalid_values(monkeypatch, value):
    monkeypatch.setenv("TEST_SECURITY_SECONDS", value)
    with pytest.raises(ImproperlyConfigured, match="non-negative integer"):
        _env_non_negative_int("TEST_SECURITY_SECONDS", 0)
