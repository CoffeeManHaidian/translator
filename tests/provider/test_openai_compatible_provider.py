import json

from PySide6.QtCore import QByteArray, QObject, Signal
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest

from providers.config import ProviderConfig
from providers.openai_compatible import OpenAICompatibleTranslationProvider
from translation.models import TranslationRequest


class FakeReply(QObject):
    readyRead = Signal()
    finished = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.deleted = False
        self.body = bytearray(
            (
                'data: {"choices":[{"delta":{"content":"译文"},'
                '"finish_reason":"stop"}]}\n\ndata: [DONE]\n\n'
            ).encode("utf-8")
        )

    def attribute(self, attribute):
        if attribute == QNetworkRequest.Attribute.HttpStatusCodeAttribute:
            return 200
        return None

    def readAll(self) -> QByteArray:
        body = bytes(self.body)
        self.body.clear()
        return QByteArray(body)

    def error(self):
        return QNetworkReply.NetworkError.NoError

    def errorString(self) -> str:
        return ""

    def abort(self) -> None:
        self.finished.emit()

    def deleteLater(self) -> None:
        self.deleted = True


class FakeNetworkManager:
    def __init__(self, reply: FakeReply) -> None:
        self.reply = reply
        self.request = None
        self.payload = b""

    def post(self, request, payload):
        self.request = request
        self.payload = bytes(payload)
        return self.reply


def test_openai_compatible_payload_omits_deepseek_extension() -> None:
    reply = FakeReply()
    network_manager = FakeNetworkManager(reply)
    provider = OpenAICompatibleTranslationProvider(
        ProviderConfig(
            provider_id="openai-compatible",
            base_url="http://localhost:11434/v1",
            model="local-model",
        ),
        network_manager=network_manager,
    )

    provider.translate(
        TranslationRequest(
            request_id="request-1",
            text="Hello",
            source_language="auto",
            target_language="zh-CN",
        )
    )

    payload = json.loads(network_manager.payload.decode("utf-8"))
    assert payload["model"] == "local-model"
    assert payload["stream"] is True
    assert "thinking" not in payload
    assert network_manager.request.rawHeader("Authorization") == b""

    reply.finished.emit()
    assert reply.deleted
