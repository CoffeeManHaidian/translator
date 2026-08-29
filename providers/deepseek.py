import json

from PySide6.QtCore import QByteArray, QObject, QUrl
from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkReply,
    QNetworkRequest,
)
from dataclasses import replace

from providers.base import TranslationProvider
from providers.config import DeepSeekConfig
from providers.sse import SSEDecoder
from translation.models import (
    TranslationError,
    TranslationErrorKind,
    TranslationRequest,
)


SYSTEM_PROMPT = """You are a professional translation engine.

Translate the user's entire text accurately and naturally as one coherent passage.
Use surrounding sentences to resolve pronouns, terminology, tone, and ambiguity.

Preserve:
- product names
- model numbers
- numbers
- units
- technical terminology
- paragraph structure

Do not explain the translation.
Only output the translated text."""

TARGET_LANGUAGE_NAMES = {
    "zh-CN": "Simplified Chinese",
    "en": "English",
}


class DeepSeekTranslationProvider(TranslationProvider):
    """通过 Qt 网络栈异步调用 DeepSeek Chat Completions API。"""

    _service_name = "DeepSeek"

    def __init__(
        self,
        config: DeepSeekConfig,
        network_manager: QNetworkAccessManager | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._config = config
        self._network_manager = (
            network_manager or QNetworkAccessManager(self)
        )
        self._replies: dict[str, QNetworkReply] = {}
        self._cancelled_request_ids: set[str] = set()
        self._stream_decoders: dict[str, SSEDecoder] = {}
        self._stream_error_bodies: dict[str, bytearray] = {}
        self._stream_terminal_ids: set[str] = set()
        self._stream_content_ids: set[str] = set()

    def translate(self, request: TranslationRequest) -> None:
        request_id = request.request_id

        if request_id in self._replies:
            self.cancel(request_id)

        self.started.emit(request_id)

        validation_error = self._validate_request(request)
        if validation_error is not None:
            self.failed.emit(request_id, validation_error)
            return

        network_request = self._create_network_request()
        payload = self._build_payload(request)
        encoded_payload = QByteArray(
            json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        )

        reply = self._network_manager.post(
            network_request,
            encoded_payload,
        )
        self._replies[request_id] = reply
        self._stream_decoders[request_id] = SSEDecoder()
        self._stream_error_bodies[request_id] = bytearray()
        reply.readyRead.connect(
            lambda request_id=request_id, reply=reply: (
                self._on_reply_ready_read(request_id, reply)
            )
        )
        reply.finished.connect(
            lambda request_id=request_id, reply=reply: (
                self._on_reply_finished(request_id, reply)
            )
        )

    def cancel(self, request_id: str) -> None:
        reply = self._replies.get(request_id)
        if reply is None or request_id in self._cancelled_request_ids:
            return

        self._cancelled_request_ids.add(request_id)
        reply.abort()
        self.cancelled.emit(request_id)

    def _validate_request(
        self,
        request: TranslationRequest,
    ) -> TranslationError | None:
        if not self._config.api_key:
            return TranslationError(
                TranslationErrorKind.AUTHENTICATION,
                f"未配置 {self._service_name} API Key",
            )

        if request.target_language not in TARGET_LANGUAGE_NAMES:
            return TranslationError(
                TranslationErrorKind.UNKNOWN,
                f"不支持的目标语言：{request.target_language}",
            )

        if len(request.text) > self._config.max_input_chars:
            return TranslationError(
                TranslationErrorKind.UNKNOWN,
                (
                    "输入内容过长，当前最多支持 "
                    f"{self._config.max_input_chars} 个字符"
                ),
            )

        return None

    def _create_network_request(self) -> QNetworkRequest:
        request = QNetworkRequest(
            QUrl(self._config.chat_completions_url)
        )
        request.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader,
            "application/json",
        )
        request.setRawHeader(
            b"Authorization",
            f"Bearer {self._config.api_key}".encode("utf-8"),
        )
        request.setRawHeader(
            b"User-Agent",
            b"TradeTranslator/0.1",
        )
        request.setRawHeader(b"Accept", b"text/event-stream")
        request.setTransferTimeout(self._config.timeout_ms)
        return request

    def _build_payload(
        self,
        request: TranslationRequest,
    ) -> dict[str, object]:
        target_language = TARGET_LANGUAGE_NAMES[
            request.target_language
        ]
        user_prompt = (
            f"Source language: {request.source_language}\n"
            f"Target language: {target_language}\n\n"
            f"{request.text}"
        )

        return {
            "model": self._config.model,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "thinking": {"type": "disabled"},
            "stream": True,
        }

    def _on_reply_ready_read(
        self,
        request_id: str,
        reply: QNetworkReply,
    ) -> None:
        self._consume_available_data(
            request_id,
            reply,
            abort_on_error=True,
        )

    def _consume_available_data(
        self,
        request_id: str,
        reply: QNetworkReply,
        abort_on_error: bool,
    ) -> bool:
        if self._replies.get(request_id) is not reply:
            return False

        if request_id in self._cancelled_request_ids:
            self._read_reply_data(reply)
            return True

        data = self._read_reply_data(reply)
        if not data:
            return True

        status_code = self._status_code(reply)
        if status_code is not None and not 200 <= status_code < 300:
            self._stream_error_bodies[request_id].extend(data)
            return True

        decoder = self._stream_decoders[request_id]
        try:
            for event_data in decoder.feed(data):
                self._consume_stream_event(request_id, event_data)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            self._fail_stream(
                request_id,
                reply,
                error,
                status_code,
                abort_on_error,
            )
            return False
        return True

    def _consume_stream_event(
        self,
        request_id: str,
        event_data: bytes,
    ) -> None:
        if event_data.strip() == b"[DONE]":
            self._stream_terminal_ids.add(request_id)
            return

        response = json.loads(event_data.decode("utf-8"))
        if not isinstance(response, dict):
            raise ValueError("流式响应不是 JSON 对象")
        choices = response.get("choices")
        if choices == []:
            # stream_options.include_usage 会产生 choices 为空的统计事件。
            return
        if not isinstance(choices, list) or not choices:
            raise ValueError("流式响应中缺少 choices")

        choice = choices[0]
        if not isinstance(choice, dict):
            raise ValueError("流式响应中的 choice 格式错误")
        delta = choice.get("delta")
        if not isinstance(delta, dict):
            raise ValueError("流式响应中缺少 delta")

        content = delta.get("content")
        if content is not None and not isinstance(content, str):
            raise ValueError("流式响应中的译文格式错误")
        if content:
            self._stream_content_ids.add(request_id)
            self.chunk_received.emit(request_id, content)

        if choice.get("finish_reason") is not None:
            self._stream_terminal_ids.add(request_id)

    def _on_reply_finished(
        self,
        request_id: str,
        reply: QNetworkReply,
    ) -> None:
        active_reply = self._replies.get(request_id)
        if active_reply is not reply:
            reply.deleteLater()
            return

        if request_id in self._cancelled_request_ids:
            self._replies.pop(request_id, None)
            self._cancelled_request_ids.discard(request_id)
            self._clear_stream_state(request_id)
            reply.deleteLater()
            return

        if not self._consume_available_data(
            request_id,
            reply,
            abort_on_error=False,
        ):
            reply.deleteLater()
            return

        status_code = self._status_code(reply)
        if status_code is None or 200 <= status_code < 300:
            decoder = self._stream_decoders[request_id]
            try:
                for event_data in decoder.finish():
                    self._consume_stream_event(request_id, event_data)
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                self._fail_stream(
                    request_id,
                    reply,
                    error,
                    status_code,
                    abort_reply=False,
                )
                reply.deleteLater()
                return

        self._replies.pop(request_id, None)
        try:
            response_body = bytes(
                self._stream_error_bodies.get(request_id, b"")
            )

            if status_code is not None and not 200 <= status_code < 300:
                self.failed.emit(
                    request_id,
                    self._error_from_http_response(
                        status_code,
                        response_body,
                    ),
                )
                return

            if (
                reply.error()
                != QNetworkReply.NetworkError.NoError
            ):
                error_kind = (
                    TranslationErrorKind.TIMEOUT
                    if reply.error()
                    == QNetworkReply.NetworkError.TimeoutError
                    else TranslationErrorKind.NETWORK
                )
                self.failed.emit(
                    request_id,
                    TranslationError(
                        error_kind,
                        reply.errorString() or "网络请求失败",
                        status_code,
                    ),
                )
                return

            if request_id not in self._stream_content_ids:
                self.failed.emit(
                    request_id,
                    TranslationError(
                        TranslationErrorKind.PARSING,
                        f"{self._service_name} 返回的译文为空",
                        status_code,
                    ),
                )
                return
            if request_id not in self._stream_terminal_ids:
                self.failed.emit(
                    request_id,
                    TranslationError(
                        TranslationErrorKind.PARSING,
                        f"{self._service_name} 流式响应意外结束",
                        status_code,
                    ),
                )
                return
            self.completed.emit(request_id)
        finally:
            self._clear_stream_state(request_id)
            reply.deleteLater()

    @staticmethod
    def _status_code(reply: QNetworkReply) -> int | None:
        status_value = reply.attribute(
            QNetworkRequest.Attribute.HttpStatusCodeAttribute
        )
        return int(status_value) if status_value is not None else None

    @staticmethod
    def _read_reply_data(reply: QNetworkReply) -> bytes:
        """避免在 SSE 连接已经关闭后再次读取 QIODevice。"""
        is_open = getattr(reply, "isOpen", None)
        if callable(is_open) and not is_open():
            return b""
        return bytes(reply.readAll())

    def _fail_stream(
        self,
        request_id: str,
        reply: QNetworkReply,
        error: Exception,
        status_code: int | None,
        abort_reply: bool,
    ) -> None:
        self._replies.pop(request_id, None)
        self._cancelled_request_ids.discard(request_id)
        self._clear_stream_state(request_id)
        self.failed.emit(
            request_id,
            TranslationError(
                TranslationErrorKind.PARSING,
                f"无法解析 {self._service_name} 流式响应：{error}",
                status_code,
            ),
        )
        if abort_reply:
            reply.abort()

    def _clear_stream_state(self, request_id: str) -> None:
        self._stream_decoders.pop(request_id, None)
        self._stream_error_bodies.pop(request_id, None)
        self._stream_terminal_ids.discard(request_id)
        self._stream_content_ids.discard(request_id)

    @staticmethod
    def _extract_translation(response_body: bytes) -> str:
        response = json.loads(response_body.decode("utf-8"))

        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise ValueError("响应中缺少译文内容") from error

        if not isinstance(content, str) or not content.strip():
            raise ValueError("响应中的译文为空")

        return content.strip()

    def _error_from_http_response(
        self,
        status_code: int,
        response_body: bytes,
    ) -> TranslationError:
        api_message = ""
        try:
            response = json.loads(response_body.decode("utf-8"))
            error_data = response.get("error", {})
            if isinstance(error_data, dict):
                api_message = str(error_data.get("message", "")).strip()
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass

        if status_code in (401, 403):
            kind = TranslationErrorKind.AUTHENTICATION
            default_message = f"{self._service_name} API Key 无效"
        elif status_code == 429:
            kind = TranslationErrorKind.RATE_LIMIT
            default_message = f"{self._service_name} 请求过于频繁，请稍后重试"
        elif status_code == 408:
            kind = TranslationErrorKind.TIMEOUT
            default_message = f"{self._service_name} 请求超时"
        elif status_code >= 500:
            kind = TranslationErrorKind.SERVER
            default_message = f"{self._service_name} 暂时不可用"
        elif status_code == 402:
            kind = TranslationErrorKind.UNKNOWN
            default_message = f"{self._service_name}账户余额不足"
        else:
            kind = TranslationErrorKind.UNKNOWN
            default_message = f"{self._service_name}请求参数错误"

        return TranslationError(
            kind,
            api_message or default_message,
            status_code,
        )

    def update_api_key(self, api_key: str) -> None:
        """更新后续翻译请求使用的 API Key。"""
        self._config = replace(
            self._config,
            api_key=api_key.strip(),
        )
