import json

from PySide6.QtCore import QByteArray, QObject, Signal
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest

from providers.config import ProviderConfig
from providers.connection import ProviderConnectionTester


class FakeReply(QObject):
    finished = Signal()

    def __init__(self, body: bytes, status_code: int = 200) -> None:
        super().__init__()
        self.body = body
        self.status_code = status_code
        self.deleted = False

    def attribute(self, attribute):
        if attribute == QNetworkRequest.Attribute.HttpStatusCodeAttribute:
            return self.status_code
        return None

    def readAll(self) -> QByteArray:
        return QByteArray(self.body)

    def error(self):
        return QNetworkReply.NetworkError.NoError

    def errorString(self) -> str:
        return ""

    def abort(self) -> None:
        pass

    def deleteLater(self) -> None:
        self.deleted = True


class FakeNetworkManager:
    def __init__(self, reply: FakeReply) -> None:
        self.reply = reply
        self.request = None

    def get(self, request):
        self.request = request
        return self.reply


def test_connection_tester_reads_models_with_bearer_auth() -> None:
    reply = FakeReply(
        json.dumps(
            {"data": [{"id": "model-b"}, {"id": "model-a"}]}
        ).encode("utf-8")
    )
    network_manager = FakeNetworkManager(reply)
    tester = ProviderConnectionTester(network_manager=network_manager)
    models = []
    tester.succeeded.connect(models.append)

    tester.test(
        ProviderConfig(
            provider_id="openai-compatible",
            base_url="https://models.example.com/v1",
            model="model-a",
            api_key="secret",
        )
    )
    reply.finished.emit()

    assert network_manager.request.url().toString() == (
        "https://models.example.com/v1/models"
    )
    assert network_manager.request.rawHeader("Authorization") == b"Bearer secret"
    assert models == [["model-a", "model-b"]]
    assert reply.deleted
