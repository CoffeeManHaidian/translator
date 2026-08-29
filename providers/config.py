import os
from dataclasses import dataclass


DEEPSEEK_PROVIDER_ID = "deepseek"
OPENAI_COMPATIBLE_PROVIDER_ID = "openai-compatible"


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    """运行一个翻译服务所需的完整配置。"""

    provider_id: str
    base_url: str
    model: str
    api_key: str = ""
    api_protocol: str = "chat_completions"
    timeout_ms: int = 60_000
    max_input_chars: int = 20_000

    @property
    def chat_completions_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/chat/completions"

    @property
    def models_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/models"


@dataclass(frozen=True, slots=True)
class DeepSeekConfig:
    """兼容现有调用的 DeepSeek 专用配置。"""

    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-v4-flash"
    timeout_ms: int = 60_000
    max_input_chars: int = 20_000

    @property
    def chat_completions_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/chat/completions"

    @classmethod
    def from_environment(cls) -> "DeepSeekConfig":
        return cls(api_key=os.getenv("DEEPSEEK_API_KEY", "").strip())

    def to_provider_config(self) -> ProviderConfig:
        return ProviderConfig(
            provider_id=DEEPSEEK_PROVIDER_ID,
            base_url=self.base_url,
            model=self.model,
            api_key=self.api_key,
            timeout_ms=self.timeout_ms,
            max_input_chars=self.max_input_chars,
        )
