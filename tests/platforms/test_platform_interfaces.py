import pytest

from platforms.global_hotkey import GlobalHotkey
from platforms.models import (
    DEFAULT_MACOS_HOTKEY,
    DEFAULT_WINDOWS_HOTKEY,
    Hotkey,
    default_hotkey_for_platform,
    hotkey_from_text,
    hotkey_to_text,
)
from platforms.text_capture import TextCapture


class FakeGlobalHotkey(GlobalHotkey):
    """验证上层只依赖统一接口，不需要真实系统 API。"""

    def __init__(self) -> None:
        super().__init__()
        self.registered_hotkey: Hotkey | None = None

    def register_hotkey(self, hotkey: Hotkey) -> bool:
        self.registered_hotkey = hotkey
        return True

    def unregister_hotkey(self) -> None:
        self.registered_hotkey = None

    def trigger(self) -> None:
        self.activated.emit()


class FakeTextCapture(TextCapture):
    def __init__(self, selected_text: str) -> None:
        super().__init__()
        self._selected_text = selected_text

    def capture_selected_text(self) -> None:
        self.capture_started.emit()
        self.text_captured.emit(self._selected_text)


def test_default_windows_hotkey_is_ctrl_shift_t() -> None:
    assert DEFAULT_WINDOWS_HOTKEY == Hotkey(
        key="T",
        ctrl=True,
        shift=True,
    )


def test_default_macos_hotkey_is_command_shift_t() -> None:
    assert DEFAULT_MACOS_HOTKEY == Hotkey(
        key="T",
        shift=True,
        meta=True,
    )


def test_platform_default_hotkey_uses_command_on_macos() -> None:
    assert default_hotkey_for_platform("darwin") == DEFAULT_MACOS_HOTKEY
    assert default_hotkey_for_platform("win32") == DEFAULT_WINDOWS_HOTKEY


def test_global_hotkey_contract_registers_triggers_and_unregisters() -> None:
    global_hotkey = FakeGlobalHotkey()
    activations: list[bool] = []
    global_hotkey.activated.connect(lambda: activations.append(True))

    assert global_hotkey.register_hotkey(DEFAULT_WINDOWS_HOTKEY)
    assert global_hotkey.registered_hotkey == DEFAULT_WINDOWS_HOTKEY

    global_hotkey.trigger()
    assert activations == [True]

    global_hotkey.unregister_hotkey()
    assert global_hotkey.registered_hotkey is None


def test_text_capture_contract_returns_result_through_signals() -> None:
    text_capture = FakeTextCapture("Selected text")
    events: list[str] = []
    text_capture.capture_started.connect(lambda: events.append("started"))
    text_capture.text_captured.connect(events.append)

    text_capture.capture_selected_text()

    assert events == ["started", "Selected text"]


def test_base_interfaces_require_platform_implementations() -> None:
    with pytest.raises(NotImplementedError):
        GlobalHotkey().register_hotkey(DEFAULT_WINDOWS_HOTKEY)
    with pytest.raises(NotImplementedError):
        GlobalHotkey().unregister_hotkey()
    with pytest.raises(NotImplementedError):
        TextCapture().capture_selected_text()


def test_hotkey_text_round_trip() -> None:
    hotkey = Hotkey(key="y", ctrl=True, alt=True, shift=True)

    assert hotkey_from_text(hotkey_to_text(hotkey)) == Hotkey(
        key="Y",
        ctrl=True,
        alt=True,
        shift=True,
    )
