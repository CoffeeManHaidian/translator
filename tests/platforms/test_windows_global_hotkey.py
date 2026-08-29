import ctypes
from ctypes import wintypes

import pytest
from PySide6.QtCore import QByteArray
from PySide6.QtWidgets import QWidget

from platforms.models import DEFAULT_WINDOWS_HOTKEY, Hotkey
from platforms.windows.global_hotkey import (
    HOTKEY_ID,
    MOD_CONTROL,
    MOD_NOREPEAT,
    MOD_SHIFT,
    WM_HOTKEY,
    WindowsGlobalHotkey,
    WindowsHotkeyEventFilter,
)


class FakeUser32:
    def __init__(
        self,
        register_result: bool = True,
        register_results: list[bool] | None = None,
    ) -> None:
        self.register_result = register_result
        self.register_results = list(register_results or [])
        self.register_calls = []
        self.unregister_calls = []

    def RegisterHotKey(
        self,
        window_handle,
        hotkey_id,
        modifiers,
        virtual_key,
    ) -> bool:
        self.register_calls.append(
            (
                window_handle,
                hotkey_id,
                modifiers,
                virtual_key,
            )
        )
        if self.register_results:
            return self.register_results.pop(0)
        return self.register_result

    def UnregisterHotKey(self, window_handle, hotkey_id) -> bool:
        self.unregister_calls.append((window_handle, hotkey_id))
        return True


@pytest.fixture
def hotkey_service(qapp):
    user32 = FakeUser32()
    service = WindowsGlobalHotkey(user32=user32)
    yield service, user32
    service.close()


def test_registers_ctrl_shift_t_with_win32(hotkey_service) -> None:
    service, user32 = hotkey_service

    assert service.register_hotkey(DEFAULT_WINDOWS_HOTKEY)
    assert user32.register_calls == [
        (
            None,
            HOTKEY_ID,
            MOD_NOREPEAT | MOD_CONTROL | MOD_SHIFT,
            ord("T"),
        )
    ]


def test_unregisters_only_after_successful_registration(
    hotkey_service,
) -> None:
    service, user32 = hotkey_service

    service.unregister_hotkey()
    assert user32.unregister_calls == []

    service.register_hotkey(DEFAULT_WINDOWS_HOTKEY)
    service.unregister_hotkey()
    service.unregister_hotkey()

    assert user32.unregister_calls == [(None, HOTKEY_ID)]


def test_registration_failure_emits_readable_error(qapp) -> None:
    user32 = FakeUser32(register_result=False)
    service = WindowsGlobalHotkey(user32=user32)
    errors: list[str] = []
    service.registration_failed.connect(errors.append)

    try:
        assert not service.register_hotkey(DEFAULT_WINDOWS_HOTKEY)
        assert len(errors) == 1
        assert "可能已被占用" in errors[0]
    finally:
        service.close()


def test_invalid_key_is_rejected_before_calling_win32(
    hotkey_service,
) -> None:
    service, user32 = hotkey_service
    errors: list[str] = []
    service.registration_failed.connect(errors.append)

    assert not service.register_hotkey(
        Hotkey(key="F1", ctrl=True)
    )

    assert user32.register_calls == []
    assert errors == ["快捷键目前只支持单个英文字母或数字"]


def test_registering_new_hotkey_unregisters_previous_one(
    hotkey_service,
) -> None:
    service, user32 = hotkey_service

    service.register_hotkey(DEFAULT_WINDOWS_HOTKEY)
    service.register_hotkey(Hotkey(key="Y", ctrl=True))

    assert user32.unregister_calls == [(None, HOTKEY_ID)]
    assert user32.register_calls[-1][-1] == ord("Y")


@pytest.mark.parametrize(
    "event_type",
    [b"windows_dispatcher_MSG", b"windows_generic_MSG"],
)
def test_native_wm_hotkey_message_emits_activated(event_type) -> None:
    activations: list[bool] = []
    event_filter = WindowsHotkeyEventFilter(
        lambda: activations.append(True)
    )
    message = wintypes.MSG()
    message.message = WM_HOTKEY
    message.wParam = HOTKEY_ID

    filtered = event_filter.nativeEventFilter(
        QByteArray(event_type),
        ctypes.addressof(message),
    )

    assert filtered is False
    assert activations == [True]


def test_native_filter_ignores_unrelated_messages() -> None:
    activations: list[bool] = []
    event_filter = WindowsHotkeyEventFilter(
        lambda: activations.append(True)
    )
    message = wintypes.MSG()
    message.message = WM_HOTKEY
    message.wParam = HOTKEY_ID + 1

    event_filter.nativeEventFilter(
        QByteArray(b"windows_dispatcher_MSG"),
        ctypes.addressof(message),
    )
    event_filter.nativeEventFilter(
        QByteArray(b"windows_generic_MSG"),
        ctypes.addressof(message),
    )

    assert activations == []


def test_registers_hotkey_against_parent_window(qapp) -> None:
    window = QWidget()
    user32 = FakeUser32()
    service = WindowsGlobalHotkey(
        user32=user32,
        parent=window,
    )

    try:
        assert service.register_hotkey(DEFAULT_WINDOWS_HOTKEY)
        assert user32.register_calls[0][0] == int(window.winId())
    finally:
        service.close()
        window.close()


def test_failed_change_restores_previous_hotkey(qapp) -> None:
    user32 = FakeUser32(register_results=[True, False, True])
    service = WindowsGlobalHotkey(user32=user32)
    errors: list[str] = []
    service.registration_failed.connect(errors.append)

    try:
        assert service.register_hotkey(DEFAULT_WINDOWS_HOTKEY)
        assert not service.register_hotkey(
            Hotkey(key="Y", ctrl=True)
        )

        assert [call[-1] for call in user32.register_calls] == [
            ord("T"),
            ord("Y"),
            ord("T"),
        ]
        assert len(errors) == 1
    finally:
        service.close()
