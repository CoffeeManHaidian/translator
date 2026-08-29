class SSEDecoder:
    """将任意网络分片增量还原为 SSE data 事件。"""

    def __init__(self, max_event_bytes: int = 1_000_000) -> None:
        self._buffer = bytearray()
        self._data_lines: list[bytes] = []
        self._event_size = 0
        self._max_event_bytes = max_event_bytes

    def feed(self, chunk: bytes) -> list[bytes]:
        self._buffer.extend(chunk)
        events: list[bytes] = []

        while True:
            newline_index = self._buffer.find(b"\n")
            if newline_index < 0:
                break

            line = bytes(self._buffer[:newline_index])
            del self._buffer[: newline_index + 1]
            if line.endswith(b"\r"):
                line = line[:-1]
            self._consume_line(line, events)

        self._check_size(len(self._buffer))
        return events

    def finish(self) -> list[bytes]:
        """处理连接结束时没有换行符的最后一行/事件。"""
        events: list[bytes] = []
        if self._buffer:
            line = bytes(self._buffer)
            self._buffer.clear()
            if line.endswith(b"\r"):
                line = line[:-1]
            self._consume_line(line, events)
        self._dispatch(events)
        return events

    def _consume_line(self, line: bytes, events: list[bytes]) -> None:
        if not line:
            self._dispatch(events)
            return
        if line.startswith(b":"):
            return

        field, separator, value = line.partition(b":")
        if separator and value.startswith(b" "):
            value = value[1:]
        if field != b"data":
            return

        self._event_size += len(value)
        self._check_size()
        self._data_lines.append(value)

    def _dispatch(self, events: list[bytes]) -> None:
        if self._data_lines:
            events.append(b"\n".join(self._data_lines))
        self._data_lines.clear()
        self._event_size = 0

    def _check_size(self, buffered_bytes: int = 0) -> None:
        if self._event_size + buffered_bytes > self._max_event_bytes:
            raise ValueError("单个流式事件过大")
