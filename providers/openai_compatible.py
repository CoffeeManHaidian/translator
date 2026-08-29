from PySide6.QtCore import QObject, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest

from providers.config import ProviderConfig
from providers.deepseek import TARGET_LANGUAGE_NAMES, DeepSeekTranslationProvider
from translation.models import (
    TranslationError,
    TranslationErrorKind,
    TranslationRequest,
)


class OpenAICompatibleTranslationProvider(DeepSeekTranslationProvider):
    """调用实现 OpenAI Chat Completions 协议的自定义服务。"""

    _service_name = "模型服务"

    def __init__(
        self,
        config: ProviderConfig,
        network_manager: QNetworkAccessManager | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(config, network_manager, parent)

    def _validate_request(
        self,
        request: TranslationRequest,
    ) -> TranslationError | None:
        if request.target_language not in TARGET_LANGUAGE_NAMES:
            return TranslationError(
                TranslationErrorKind.UNKNOWN,
                f"不支持的目标语言：{request.target_language}",
            )
        if len(request.text) > self._config.max_input_chars:
            return TranslationError(
                TranslationErrorKind.UNKNOWN,
                f"输入内容过长，当前最多支持 {self._config.max_input_chars} 个字符",
            )
        return None

    def _create_network_request(self) -> QNetworkRequest:
        request = QNetworkRequest(QUrl(self._config.chat_completions_url))
        request.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader,
            "application/json",
        )
        if self._config.api_key:
            request.setRawHeader(
                b"Authorization",
                f"Bearer {self._config.api_key}".encode("utf-8"),
            )
        request.setRawHeader(b"User-Agent", b"TradeTranslator/0.1")
        request.setTransferTimeout(self._config.timeout_ms)
        return request

    def _build_payload(
        self,
        request: TranslationRequest,
    ) -> dict[str, object]:
        payload = super()._build_payload(request)
        payload.pop("thinking", None)
        return payload
