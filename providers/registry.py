from dataclasses import dataclass
from urllib.parse import urlparse

from providers.base import TranslationProvider
from providers.config import (
    DEEPSEEK_PROVIDER_ID,
    OPENAI_COMPATIBLE_PROVIDER_ID,
    DeepSeekConfig,
    ProviderConfig,
)


@dataclass(frozen=True, slots=True)
class ProviderDefinition:
    provider_id: str
    display_name: str
    default_base_url: str
    default_model: str
    requires_api_key: bool


PROVIDERS = {
    DEEPSEEK_PROVIDER_ID: ProviderDefinition(
        provider_id=DEEPSEEK_PROVIDER_ID,
        display_name="DeepSeek",
        default_base_url="https://api.deepseek.com",
        default_model="deepseek-v4-flash",
        requires_api_key=True,
    ),
    OPENAI_COMPATIBLE_PROVIDER_ID: ProviderDefinition(
        provider_id=OPENAI_COMPATIBLE_PROVIDER_ID,
        display_name="自定义 OpenAI-Compatible",
        default_base_url="http://localhost:11434/v1",
        default_model="",
        requires_api_key=False,
    ),
}


def provider_definitions() -> tuple[ProviderDefinition, ...]:
    return tuple(PROVIDERS.values())


def get_provider_definition(provider_id: str) -> ProviderDefinition:
    try:
        return PROVIDERS[provider_id]
    except KeyError as error:
        raise ValueError(f"不支持的服务商：{provider_id}") from error


def default_provider_config(provider_id: str) -> ProviderConfig:
    definition = get_provider_definition(provider_id)
    return ProviderConfig(
        provider_id=provider_id,
        base_url=definition.default_base_url,
        model=definition.default_model,
    )


def validate_provider_config(config: ProviderConfig) -> ProviderConfig:
    definition = get_provider_definition(config.provider_id)
    base_url = config.base_url.strip().rstrip("/")
    model = config.model.strip()
    api_key = config.api_key.strip()

    if not base_url:
        raise ValueError("API 地址不能为空")

    parsed = urlparse(base_url)
    host = (parsed.hostname or "").lower()
    local_hosts = {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("API 地址必须是有效的 HTTP 或 HTTPS 地址")
    if parsed.scheme == "http" and host not in local_hosts:
        raise ValueError("非本地 API 地址必须使用 HTTPS")
    if not model:
        raise ValueError("模型名称不能为空")
    if definition.requires_api_key and not api_key:
        raise ValueError("API Key 不能为空")

    return ProviderConfig(
        provider_id=config.provider_id,
        base_url=base_url,
        model=model,
        api_key=api_key,
        api_protocol=config.api_protocol,
        timeout_ms=config.timeout_ms,
        max_input_chars=config.max_input_chars,
    )


def create_provider(config: ProviderConfig) -> TranslationProvider:
    try:
        config = validate_provider_config(config)
    except ValueError as error:
        # 首次启动时允许 DeepSeek 暂无密钥，用户仍可进入设置页。
        if not (
            config.provider_id == DEEPSEEK_PROVIDER_ID
            and not config.api_key.strip()
            and str(error) == "API Key 不能为空"
        ):
            raise

    if config.provider_id == DEEPSEEK_PROVIDER_ID:
        from providers.deepseek import DeepSeekTranslationProvider

        return DeepSeekTranslationProvider(
            DeepSeekConfig(
                api_key=config.api_key,
                base_url=config.base_url,
                model=config.model,
                timeout_ms=config.timeout_ms,
                max_input_chars=config.max_input_chars,
            )
        )

    if config.provider_id == OPENAI_COMPATIBLE_PROVIDER_ID:
        from providers.openai_compatible import (
            OpenAICompatibleTranslationProvider,
        )

        return OpenAICompatibleTranslationProvider(config)

    raise ValueError(f"不支持的服务商：{config.provider_id}")
