import os

import keyring
from keyring.errors import KeyringError, PasswordDeleteError
from PySide6.QtCore import QSettings

from providers.config import DEEPSEEK_PROVIDER_ID, ProviderConfig
from providers.registry import default_provider_config, get_provider_definition
from platforms.models import (
    Hotkey,
    default_hotkey_for_platform,
    hotkey_from_text,
    hotkey_to_text,
)


SERVICE_NAME = "com.trade-translator.credentials"
API_KEY_ACCOUNT = "deepseek-api-key"
SELECTED_PROVIDER_KEY = "providers/selected"
GLOBAL_HOTKEY_KEY = "shortcuts/global_hotkey"


class CredentialStoreError(RuntimeError):
    """系统凭据存储不可用或写入失败。"""


class SettingsStore:
    def __init__(self, settings: QSettings | None = None) -> None:
        self._settings = settings or QSettings()

    @staticmethod
    def _api_key_account(provider_id: str) -> str:
        if provider_id == DEEPSEEK_PROVIDER_ID:
            return API_KEY_ACCOUNT
        return f"{provider_id}-api-key"

    def save_api_key(
        self,
        api_key: str,
        provider_id: str = DEEPSEEK_PROVIDER_ID,
    ) -> None:
        api_key = api_key.strip()
        definition = get_provider_definition(provider_id)

        if not api_key:
            if definition.requires_api_key:
                raise ValueError("API Key 不能为空")
            self.delete_api_key(provider_id)
            return

        try:
            keyring.set_password(
                SERVICE_NAME,
                self._api_key_account(provider_id),
                api_key,
            )
        except KeyringError as error:
            raise CredentialStoreError(
                "无法保存 API Key，请检查系统凭据服务"
            ) from error

    def load_api_key(
        self,
        provider_id: str = DEEPSEEK_PROVIDER_ID,
    ) -> str:
        try:
            stored_key = keyring.get_password(
                SERVICE_NAME,
                self._api_key_account(provider_id),
            )
        except KeyringError:
            stored_key = None

        if stored_key:
            return stored_key.strip()
        if provider_id == DEEPSEEK_PROVIDER_ID:
            return os.getenv("DEEPSEEK_API_KEY", "").strip()
        return ""

    def delete_api_key(
        self,
        provider_id: str = DEEPSEEK_PROVIDER_ID,
    ) -> None:
        try:
            keyring.delete_password(
                SERVICE_NAME,
                self._api_key_account(provider_id),
            )
        except (PasswordDeleteError, KeyringError):
            pass

    def save_provider_config(self, config: ProviderConfig) -> None:
        definition = get_provider_definition(config.provider_id)
        base_url = config.base_url.strip().rstrip("/")
        model = config.model.strip()

        if not base_url:
            raise ValueError("模型地址不能为空")
        if not model:
            raise ValueError("模型名称不能为空")
        if definition.requires_api_key and not config.api_key.strip():
            raise ValueError("API Key 不能为空")

        self.save_api_key(config.api_key, config.provider_id)
        prefix = f"providers/{config.provider_id}"
        self._settings.setValue(f"{prefix}/base_url", base_url)
        self._settings.setValue(f"{prefix}/model", model)
        self._settings.setValue(SELECTED_PROVIDER_KEY, config.provider_id)
        self._settings.sync()

    def load_provider_config(self, provider_id: str) -> ProviderConfig:
        default = default_provider_config(provider_id)
        prefix = f"providers/{provider_id}"
        return ProviderConfig(
            provider_id=provider_id,
            base_url=str(
                self._settings.value(
                    f"{prefix}/base_url",
                    default.base_url,
                )
            ).strip(),
            model=str(
                self._settings.value(
                    f"{prefix}/model",
                    default.model,
                )
            ).strip(),
            api_key=self.load_api_key(provider_id),
        )

    def load_active_config(self) -> ProviderConfig:
        provider_id = str(
            self._settings.value(
                SELECTED_PROVIDER_KEY,
                DEEPSEEK_PROVIDER_ID,
            )
        )
        try:
            return self.load_provider_config(provider_id)
        except ValueError:
            return self.load_provider_config(DEEPSEEK_PROVIDER_ID)

    def save_hotkey(self, hotkey: Hotkey) -> None:
        self._settings.setValue(
            GLOBAL_HOTKEY_KEY,
            hotkey_to_text(hotkey),
        )
        self._settings.sync()

    def load_hotkey(self) -> Hotkey:
        default_hotkey = default_hotkey_for_platform()
        stored_value = str(
            self._settings.value(
                GLOBAL_HOTKEY_KEY,
                hotkey_to_text(default_hotkey),
            )
        )
        try:
            return hotkey_from_text(stored_value)
        except ValueError:
            return default_hotkey
