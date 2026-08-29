from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class TranslationRequest:
    """翻译请求数据类"""
    request_id: str
    text: str
    source_language: str
    target_language: str


class TranslationErrorKind(Enum):
    """翻译错误类型"""
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    NETWORK = "network"
    TIMEOUT = "timeout"
    SERVER = "server"
    PARSING = "parsing"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class TranslationError:
    """可供业务层和 UI 使用的统一翻译错误。"""

    kind: TranslationErrorKind
    message: str
    status_code: int | None = None

    def __str__(self) -> str:
        return self.message
