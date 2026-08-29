from providers.sse import SSEDecoder


def test_sse_decoder_handles_split_utf8_and_crlf_events() -> None:
    decoder = SSEDecoder()
    encoded = "data: 你好\r\n\r\ndata: 世界\n\n".encode("utf-8")
    split_at = encoded.index("好".encode("utf-8")) + 1

    assert decoder.feed(encoded[:split_at]) == []
    assert decoder.feed(encoded[split_at:]) == [
        "你好".encode("utf-8"),
        "世界".encode("utf-8"),
    ]


def test_sse_decoder_joins_multiple_data_lines_and_ignores_comments() -> None:
    decoder = SSEDecoder()

    events = decoder.feed(
        b": keep-alive\n"
        b"event: message\n"
        b"data: first\n"
        b"data: second\n\n"
    )

    assert events == [b"first\nsecond"]


def test_sse_decoder_flushes_final_event_without_blank_line() -> None:
    decoder = SSEDecoder()

    assert decoder.feed(b"data: [DONE]") == []
    assert decoder.finish() == [b"[DONE]"]
