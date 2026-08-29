from platforms.macos.quartz_api import (
    K_CG_EVENT_FLAG_MASK_COMMAND,
    MacOSQuartzApi,
)


MACOS_KEY_CODE_C = 8
MACOS_KEY_CODE_COMMAND = 55


class MacOSCopyKeySender:
    """通过 Quartz 向当前前台应用发送一次 Command+C。"""

    def __init__(self, api: MacOSQuartzApi | None = None) -> None:
        self._api = api or MacOSQuartzApi()

    def send_copy_shortcut(self) -> bool:
        if not self._api.request_post_event_access():
            return False

        event_specs = (
            (
                MACOS_KEY_CODE_COMMAND,
                True,
                K_CG_EVENT_FLAG_MASK_COMMAND,
            ),
            (MACOS_KEY_CODE_C, True, K_CG_EVENT_FLAG_MASK_COMMAND),
            (MACOS_KEY_CODE_C, False, K_CG_EVENT_FLAG_MASK_COMMAND),
            (MACOS_KEY_CODE_COMMAND, False, 0),
        )
        events = [
            self._api.create_keyboard_event(key_code, is_key_down)
            for key_code, is_key_down, _flags in event_specs
        ]
        if not all(events):
            for event in events:
                self._api.release(event)
            return False

        try:
            for event, (_key_code, _is_key_down, flags) in zip(
                events,
                event_specs,
            ):
                # 覆盖触发全局快捷键时仍按下的 Shift 等修饰键。
                self._api.set_event_flags(event, flags)
                self._api.post_event(event)
        finally:
            for event in events:
                self._api.release(event)
        return True
