import pytest

from providers.config import ProviderConfig
from providers.deepseek import DeepSeekTranslationProvider
from providers.registry import create_provider, validate_provider_config


def test_custom_remote_http_endpoint_is_rejected() -> None:
    config = ProviderConfig(
        provider_id="openai-compatible",
        base_url="http://example.com/v1",
        model="example-model",
    )

    with pytest.raises(ValueError, match="必须使用 HTTPS"):
        validate_provider_config(config)


def test_deepseek_provider_can_be_created_before_key_is_configured() -> None:
    provider = create_provider(
        ProviderConfig(
            provider_id="deepseek",
            base_url="https://api.deepseek.com",
            model="deepseek-v4-flash",
        )
    )

    assert isinstance(provider, DeepSeekTranslationProvider)
