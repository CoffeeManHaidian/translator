import keyring
import pytest
from keyring.errors import KeyringError, PasswordDeleteError

from settings.store import (
    API_KEY_ACCOUNT,
    CredentialStoreError,
    SERVICE_NAME,
    SettingsStore,
)
from providers.config import ProviderConfig
from platforms.models import DEFAULT_MACOS_HOTKEY, Hotkey


class FakeSettings:
    def __init__(self) -> None:
        self.values = {}

    def setValue(self, key, value) -> None:
        self.values[key] = value

    def value(self, key, default=None):
        return self.values.get(key, default)

    def sync(self) -> None:
        pass


def test_save_api_key_uses_system_keyring(monkeypatch) -> None:
    calls: list[tuple[str, str, str]] = []
    monkeypatch.setattr(
        keyring,
        "set_password",
        lambda service, account, value: calls.append(
            (service, account, value)
        ),
    )

    SettingsStore().save_api_key("  secret-key  ")

    assert calls == [
        (SERVICE_NAME, API_KEY_ACCOUNT, "secret-key")
    ]


def test_save_api_key_rejects_empty_value(monkeypatch) -> None:
    monkeypatch.setattr(
        keyring,
        "set_password",
        lambda *_args: pytest.fail("不应写入空 API Key"),
    )

    with pytest.raises(ValueError, match="API Key 不能为空"):
        SettingsStore().save_api_key("   ")


def test_save_api_key_reports_unavailable_keyring(monkeypatch) -> None:
    def raise_keyring_error(*_args):
        raise KeyringError("keyring unavailable")

    monkeypatch.setattr(
        keyring,
        "set_password",
        raise_keyring_error,
    )

    with pytest.raises(
        CredentialStoreError,
        match="无法保存 API Key",
    ):
        SettingsStore().save_api_key("secret-key")


def test_load_api_key_prefers_system_keyring(monkeypatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "environment-key")
    monkeypatch.setattr(
        keyring,
        "get_password",
        lambda *_args: "  stored-key  ",
    )

    assert SettingsStore().load_api_key() == "stored-key"


def test_load_api_key_falls_back_to_environment(monkeypatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "  environment-key  ")
    monkeypatch.setattr(
        keyring,
        "get_password",
        lambda *_args: None,
    )

    assert SettingsStore().load_api_key() == "environment-key"


def test_load_api_key_handles_unavailable_keyring(monkeypatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "environment-key")

    def raise_keyring_error(*_args):
        raise KeyringError("keyring unavailable")

    monkeypatch.setattr(keyring, "get_password", raise_keyring_error)

    assert SettingsStore().load_api_key() == "environment-key"


def test_delete_api_key_ignores_missing_credential(monkeypatch) -> None:
    def raise_missing_password(*_args):
        raise PasswordDeleteError("credential not found")

    monkeypatch.setattr(
        keyring,
        "delete_password",
        raise_missing_password,
    )

    SettingsStore().delete_api_key()


def test_provider_settings_and_keys_are_stored_separately(monkeypatch) -> None:
    credentials = {}
    monkeypatch.setattr(
        keyring,
        "set_password",
        lambda service, account, value: credentials.__setitem__(
            (service, account), value
        ),
    )
    monkeypatch.setattr(
        keyring,
        "get_password",
        lambda service, account: credentials.get((service, account)),
    )
    settings = FakeSettings()
    store = SettingsStore(settings=settings)

    store.save_provider_config(
        ProviderConfig(
            provider_id="openai-compatible",
            base_url="https://gateway.example.com/v1/",
            model="custom-model",
            api_key="custom-key",
        )
    )

    loaded = store.load_active_config()
    assert loaded.provider_id == "openai-compatible"
    assert loaded.base_url == "https://gateway.example.com/v1"
    assert loaded.model == "custom-model"
    assert loaded.api_key == "custom-key"
    assert store.load_api_key("deepseek") == ""


def test_hotkey_is_saved_and_loaded_from_qsettings() -> None:
    store = SettingsStore(settings=FakeSettings())
    hotkey = Hotkey(key="Y", ctrl=True, alt=True)

    store.save_hotkey(hotkey)

    assert store.load_hotkey() == hotkey


def test_empty_settings_use_macos_default_hotkey(monkeypatch) -> None:
    monkeypatch.setattr("platforms.models.sys.platform", "darwin")

    store = SettingsStore(settings=FakeSettings())

    assert store.load_hotkey() == DEFAULT_MACOS_HOTKEY


def test_default_target_language_is_saved_and_loaded() -> None:
    store = SettingsStore(settings=FakeSettings())

    store.save_default_target_language("en")

    assert store.load_default_target_language() == "en"


def test_invalid_default_target_language_falls_back_to_chinese() -> None:
    settings = FakeSettings()
    settings.setValue("translation/default_target_language", "fr")

    assert (
        SettingsStore(settings=settings).load_default_target_language()
        == "zh-CN"
    )


def test_unsupported_default_target_language_is_rejected() -> None:
    store = SettingsStore(settings=FakeSettings())

    with pytest.raises(ValueError, match="不支持的目标语言"):
        store.save_default_target_language("fr")
