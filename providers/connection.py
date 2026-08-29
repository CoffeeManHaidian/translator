import json

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkReply,
    QNetworkRequest,
)

from providers.config import ProviderConfig
from providers.registry import validate_provider_config


class ProviderConnectionTester(QObject):
    """异步读取模型列表，验证地址和凭据是否可用。"""

    started = Signal()
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        network_manager: QNetworkAccessManager | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._network_manager = network_manager or QNetworkAccessManager(self)
        self._reply: QNetworkReply | None = None

    def test(self, config: ProviderConfig) -> None:
        try:
            config = validate_provider_config(config)
        except ValueError as error:
            self.failed.emit(str(error))
            return

        if self._reply is not None:
            previous_reply = self._reply
            self._reply = None
            previous_reply.abort()

        request = QNetworkRequest(QUrl(config.models_url))
        request.setRawHeader(b"Accept", b"application/json")
        request.setRawHeader(b"User-Agent", b"TradeTranslator/0.1")
        if config.api_key:
            request.setRawHeader(
                b"Authorization",
                f"Bearer {config.api_key}".encode("utf-8"),
            )
        request.setTransferTimeout(min(config.timeout_ms, 10_000))

        self.started.emit()
        reply = self._network_manager.get(request)
        self._reply = reply
        reply.finished.connect(lambda reply=reply: self._on_finished(reply))

    def _on_finished(self, reply: QNetworkReply) -> None:
        if reply is not self._reply:
            reply.deleteLater()
            return
        self._reply = None

        try:
            status_value = reply.attribute(
                QNetworkRequest.Attribute.HttpStatusCodeAttribute
            )
            status_code = int(status_value) if status_value is not None else None
            body = bytes(reply.readAll())

            if status_code in (401, 403):
                self.failed.emit("API Key 无效或没有访问权限")
                return
            if status_code is not None and not 200 <= status_code < 300:
                self.failed.emit(self._http_error(status_code, body))
                return
            if reply.error() != QNetworkReply.NetworkError.NoError:
                self.failed.emit(reply.errorString() or "无法连接模型服务")
                return

            response = json.loads(body.decode("utf-8"))
            data = response.get("data")
            if not isinstance(data, list):
                raise ValueError("响应中缺少模型列表")
            models = sorted(
                item["id"].strip()
                for item in data
                if isinstance(item, dict)
                and isinstance(item.get("id"), str)
                and item["id"].strip()
            )
            self.succeeded.emit(models)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            self.failed.emit(f"无法解析模型列表：{error}")
        finally:
            reply.deleteLater()

    @staticmethod
    def _http_error(status_code: int, body: bytes) -> str:
        try:
            response = json.loads(body.decode("utf-8"))
            error = response.get("error", {})
            if isinstance(error, dict) and error.get("message"):
                return str(error["message"])
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass
        return f"连接测试失败（HTTP {status_code}）"
