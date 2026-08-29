from platforms.macos.global_hotkey import (
    QuartzHotkeyListener,
    MacOSGlobalHotkey,
    hotkey_key_code,
    hotkey_modifier_flags,
)
from platforms.macos.quartz_api import (
    K_CG_EVENT_FLAG_MASK_COMMAND,
    K_CG_EVENT_FLAG_MASK_SHIFT,
    K_CG_EVENT_KEY_DOWN,
    K_CG_EVENT_TAP_DISABLED_BY_TIMEOUT,
    K_CG_KEYBOARD_EVENT_AUTOREPEAT,
    K_CG_KEYBOARD_EVENT_KEYCODE,
)
from platforms.models import DEFAULT_MACOS_HOTKEY, Hotkey


class FakeListener:
    def __init__(self, hotkey, callback, start_result=True) -> None:
        self.hotkey = hotkey
        self.callback = callback
        self.start_result = start_result
        self.start_count = 0
        self.stop_count = 0

    def start(self) -> bool:
        self.start_count += 1
        return self.start_result

    def stop(self) -> None:
        self.stop_count += 1


class RecordingListenerFactory:
    def __init__(self, start_results=None) -> None:
        self.start_results = list(start_results or [])
        self.listeners = []

    def __call__(self, hotkey, callback) -> FakeListener:
        start_result = (
            self.start_results.pop(0)
            if self.start_results
            else True
        )
        listener = FakeListener(hotkey, callback, start_result)
        self.listeners.append(listener)
        return listener


class FakeQuartzApi:
    def __init__(self) -> None:
        self.flags = 0
        self.key_code = 0
        self.is_repeat = 0
        self.enabled_taps = []

    def event_flags(self, _event) -> int:
        return self.flags

    def event_integer(self, _event, field) -> int:
        if field == K_CG_KEYBOARD_EVENT_KEYCODE:
            return self.key_code
        if field == K_CG_KEYBOARD_EVENT_AUTOREPEAT:
            return self.is_repeat
        raise AssertionError(f"未知事件字段：{field}")

    def enable_event_tap(self, event_tap) -> None:
        self.enabled_taps.append(event_tap)


def test_macos_key_code_and_modifiers_for_command_shift_t() -> None:
    assert hotkey_key_code(DEFAULT_MACOS_HOTKEY) == 17
    assert hotkey_modifier_flags(DEFAULT_MACOS_HOTKEY) == (
        K_CG_EVENT_FLAG_MASK_COMMAND
        | K_CG_EVENT_FLAG_MASK_SHIFT
    )


def test_macos_service_registers_and_emits_activated(qapp) -> None:
    factory = RecordingListenerFactory()
    service = MacOSGlobalHotkey(listener_factory=factory)
    activations = []
    service.activated.connect(lambda: activations.append(True))

    try:
        assert service.register_hotkey(DEFAULT_MACOS_HOTKEY)
        assert factory.listeners[0].hotkey == DEFAULT_MACOS_HOTKEY

        factory.listeners[0].callback()
        assert activations == [True]
    finally:
        service.close()


def test_macos_registration_failure_emits_permission_help(qapp) -> None:
    factory = RecordingListenerFactory(start_results=[False])
    service = MacOSGlobalHotkey(listener_factory=factory)
    errors = []
    service.registration_failed.connect(errors.append)

    try:
        assert not service.register_hotkey(DEFAULT_MACOS_HOTKEY)
        assert "输入监控" in errors[0]
    finally:
        service.close()


def test_changing_macos_hotkey_stops_previous_listener(qapp) -> None:
    factory = RecordingListenerFactory()
    service = MacOSGlobalHotkey(listener_factory=factory)

    try:
        assert service.register_hotkey(DEFAULT_MACOS_HOTKEY)
        assert service.register_hotkey(
            Hotkey(key="Y", meta=True, shift=True)
        )

        assert factory.listeners[0].stop_count == 1
        assert factory.listeners[1].hotkey.key == "Y"
    finally:
        service.close()


def test_quartz_listener_matches_key_and_ignores_repeat() -> None:
    api = FakeQuartzApi()
    activations = []
    listener = QuartzHotkeyListener(
        DEFAULT_MACOS_HOTKEY,
        lambda: activations.append(True),
        api=api,
    )
    api.key_code = 17
    api.flags = (
        K_CG_EVENT_FLAG_MASK_COMMAND
        | K_CG_EVENT_FLAG_MASK_SHIFT
    )

    listener._handle_event(None, K_CG_EVENT_KEY_DOWN, 1, None)
    api.is_repeat = 1
    listener._handle_event(None, K_CG_EVENT_KEY_DOWN, 1, None)

    assert activations == [True]


def test_disabled_quartz_tap_is_reenabled() -> None:
    api = FakeQuartzApi()
    listener = QuartzHotkeyListener(
        DEFAULT_MACOS_HOTKEY,
        lambda: None,
        api=api,
    )
    listener._event_tap = 42

    listener._handle_event(
        None,
        K_CG_EVENT_TAP_DISABLED_BY_TIMEOUT,
        1,
        None,
    )

    assert api.enabled_taps == [42]
