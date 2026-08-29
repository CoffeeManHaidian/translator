import json

from PySide6.QtCore import QByteArray, QObject, Signal
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest

from providers.config import DeepSeekConfig
from providers.deepseek import DeepSeekTranslationProvider
from translation.models import TranslationErrorKind, TranslationRequest


class FakeNetworkReply(QObject):
    readyRead = Signal()
    finished = Signal()

    def __init__(
        self,
        body: bytes,
        status_code: int = 200,
        network_error: QNetworkReply.NetworkError = (
            QNetworkReply.NetworkError.NoError
        ),
        error_string: str = "",
    ) -> None:
        super().__init__()
        self._body = bytearray(body)
        self._status_code = status_code
        self._network_error = network_error
        self._error_string = error_string
        self.was_aborted = False
        self.was_deleted = False
        self.is_open = True
        self.read_count = 0

    def attribute(self, attribute):
        if (
            attribute
            == QNetworkRequest.Attribute.HttpStatusCodeAttribute
        ):
            return self._status_code
        return None

    def readAll(self) -> QByteArray:
        if not self.is_open:
            raise AssertionError("设备关闭后不应继续读取")
        self.read_count += 1
        body = bytes(self._body)
        self._body.clear()
        return QByteArray(body)

    def push(self, body: bytes) -> None:
        self._body.extend(body)
        self.readyRead.emit()

    def error(self) -> QNetworkReply.NetworkError:
        return self._network_error

    def errorString(self) -> str:
        return self._error_string

    def abort(self) -> None:
        self.was_aborted = True
        self.is_open = False
        self.finished.emit()

    def isOpen(self) -> bool:
        return self.is_open

    def deleteLater(self) -> None:
        self.was_deleted = True


class FakeNetworkAccessManager:
    def __init__(self, reply: FakeNetworkReply) -> None:
        self.reply = reply
        self.request = None
        self.payload = b""

    def post(self, request, payload):
        self.request = request
        self.payload = bytes(payload)
        return self.reply


def make_request(request_id: str = "request-1") -> TranslationRequest:
    return TranslationRequest(
        request_id=request_id,
        text="Hello world",
        source_language="auto",
        target_language="zh-CN",
    )


def stream_event(content: str, finish_reason=None) -> bytes:
    body = {
        "choices": [
            {
                "delta": {"content": content},
                "finish_reason": finish_reason,
            }
        ]
    }
    return b"data: " + json.dumps(body, ensure_ascii=False).encode("utf-8") + b"\n\n"


def test_deepseek_provider_builds_and_emits_streaming_request() -> None:
    reply = FakeNetworkReply(b"")
    network_manager = FakeNetworkAccessManager(reply)
    provider = DeepSeekTranslationProvider(
        DeepSeekConfig(api_key="test-key"),
        network_manager=network_manager,
    )

    chunks: list[str] = []
    completed_ids: list[str] = []
    provider.chunk_received.connect(
        lambda _request_id, chunk: chunks.append(chunk)
    )
    provider.completed.connect(completed_ids.append)

    provider.translate(make_request())

    payload = json.loads(network_manager.payload.decode("utf-8"))
    assert payload["model"] == "deepseek-v4-flash"
    assert payload["stream"] is True
    assert payload["thinking"] == {"type": "disabled"}
    assert payload["messages"][-1]["content"].endswith(
        "Hello world"
    )
    assert network_manager.request.rawHeader(
        "Authorization"
    ) == b"Bearer test-key"

    first_event = stream_event("你好")
    split_at = first_event.index("好".encode("utf-8")) + 1
    reply.push(first_event[:split_at])
    assert chunks == []

    reply.push(
        first_event[split_at:]
        + stream_event("，世界", finish_reason="stop")
        + b"data: [DONE]\n\n"
    )

    assert chunks == ["你好", "，世界"]
    assert completed_ids == []

    reply.finished.emit()

    assert completed_ids == ["request-1"]
    assert reply.was_deleted


def test_deepseek_provider_reports_missing_api_key() -> None:
    reply = FakeNetworkReply(b"")
    network_manager = FakeNetworkAccessManager(reply)
    provider = DeepSeekTranslationProvider(
        DeepSeekConfig(api_key=""),
        network_manager=network_manager,
    )

    errors = []
    provider.failed.connect(
        lambda _request_id, error: errors.append(error)
    )

    provider.translate(make_request())

    assert len(errors) == 1
    assert errors[0].kind is TranslationErrorKind.AUTHENTICATION
    assert network_manager.request is None


def test_deepseek_provider_maps_authentication_error() -> None:
    reply = FakeNetworkReply(
        json.dumps(
            {"error": {"message": "Authentication fails"}}
        ).encode("utf-8"),
        status_code=401,
    )
    provider = DeepSeekTranslationProvider(
        DeepSeekConfig(api_key="invalid-key"),
        network_manager=FakeNetworkAccessManager(reply),
    )

    errors = []
    provider.failed.connect(
        lambda _request_id, error: errors.append(error)
    )

    provider.translate(make_request())
    reply.finished.emit()

    assert len(errors) == 1
    assert errors[0].kind is TranslationErrorKind.AUTHENTICATION
    assert errors[0].status_code == 401


def test_deepseek_provider_can_cancel_request() -> None:
    reply = FakeNetworkReply(stream_event("不应显示"))
    provider = DeepSeekTranslationProvider(
        DeepSeekConfig(api_key="test-key"),
        network_manager=FakeNetworkAccessManager(reply),
    )

    cancelled_ids: list[str] = []
    chunks: list[str] = []
    completed_ids: list[str] = []
    provider.cancelled.connect(cancelled_ids.append)
    provider.chunk_received.connect(
        lambda _request_id, chunk: chunks.append(chunk)
    )
    provider.completed.connect(completed_ids.append)

    provider.translate(make_request())
    provider.cancel("request-1")

    assert reply.was_aborted
    assert cancelled_ids == ["request-1"]
    assert chunks == []
    assert completed_ids == []
    assert reply.was_deleted


def test_deepseek_provider_uses_updated_api_key() -> None:
    reply = FakeNetworkReply(b"")
    network_manager = FakeNetworkAccessManager(reply)
    provider = DeepSeekTranslationProvider(
        DeepSeekConfig(api_key="old-key"),
        network_manager=network_manager,
    )

    provider.update_api_key("  new-key  ")
    provider.translate(make_request())

    assert network_manager.request.rawHeader(
        "Authorization"
    ) == b"Bearer new-key"


def test_deepseek_provider_reports_malformed_stream() -> None:
    reply = FakeNetworkReply(b"")
    provider = DeepSeekTranslationProvider(
        DeepSeekConfig(api_key="test-key"),
        network_manager=FakeNetworkAccessManager(reply),
    )
    errors = []
    provider.failed.connect(
        lambda _request_id, error: errors.append(error)
    )

    provider.translate(make_request())
    reply.push(b"data: {not-json}\n\n")

    assert len(errors) == 1
    assert errors[0].kind is TranslationErrorKind.PARSING
    assert reply.was_aborted


def test_deepseek_provider_rejects_truncated_stream() -> None:
    reply = FakeNetworkReply(stream_event("部分译文"))
    provider = DeepSeekTranslationProvider(
        DeepSeekConfig(api_key="test-key"),
        network_manager=FakeNetworkAccessManager(reply),
    )
    errors = []
    provider.failed.connect(
        lambda _request_id, error: errors.append(error)
    )

    provider.translate(make_request())
    reply.finished.emit()

    assert len(errors) == 1
    assert errors[0].kind is TranslationErrorKind.PARSING
    assert "意外结束" in errors[0].message


def test_finished_closed_reply_is_not_read_again() -> None:
    reply = FakeNetworkReply(b"")
    provider = DeepSeekTranslationProvider(
        DeepSeekConfig(api_key="test-key"),
        network_manager=FakeNetworkAccessManager(reply),
    )

    provider.translate(make_request())
    reply.push(
        stream_event("译文", finish_reason="stop")
        + b"data: [DONE]\n\n"
    )
    reads_before_finished = reply.read_count
    reply.is_open = False
    reply.finished.emit()

    assert reply.read_count == reads_before_finished
