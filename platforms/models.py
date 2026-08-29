from dataclasses import dataclass
import sys


@dataclass(frozen=True, slots=True)
class Hotkey:
    key: str
    ctrl: bool = False
    shift: bool = False
    alt: bool = False
    meta: bool = False


DEFAULT_WINDOWS_HOTKEY = Hotkey(
    key="T",
    ctrl=True,
    shift=True,
)

DEFAULT_MACOS_HOTKEY = Hotkey(
    key="T",
    shift=True,
    meta=True,
)


def default_hotkey_for_platform(
    platform_name: str | None = None,
) -> Hotkey:
    platform_name = platform_name or sys.platform
    if platform_name == "darwin":
        return DEFAULT_MACOS_HOTKEY
    return DEFAULT_WINDOWS_HOTKEY


def validate_hotkey(hotkey: Hotkey) -> Hotkey:
    key = hotkey.key.strip().upper()
    if len(key) != 1 or not key.isascii() or not key.isalnum():
        raise ValueError("快捷键目前只支持单个英文字母或数字")
    if not (hotkey.ctrl or hotkey.alt or hotkey.meta):
        raise ValueError("快捷键必须包含 Ctrl、Alt 或 Command/Win")
    return Hotkey(
        key=key,
        ctrl=hotkey.ctrl,
        shift=hotkey.shift,
        alt=hotkey.alt,
        meta=hotkey.meta,
    )


def hotkey_to_text(hotkey: Hotkey) -> str:
    hotkey = validate_hotkey(hotkey)
    parts = []
    if hotkey.ctrl:
        parts.append("Ctrl")
    if hotkey.alt:
        parts.append("Alt")
    if hotkey.shift:
        parts.append("Shift")
    if hotkey.meta:
        parts.append("Meta")
    parts.append(hotkey.key)
    return "+".join(parts)


def hotkey_from_text(value: str) -> Hotkey:
    parts = [part.strip() for part in value.split("+") if part.strip()]
    modifiers = {
        "ctrl": False,
        "shift": False,
        "alt": False,
        "meta": False,
    }
    keys: list[str] = []
    aliases = {
        "ctrl": "ctrl",
        "control": "ctrl",
        "shift": "shift",
        "alt": "alt",
        "meta": "meta",
        "win": "meta",
        "command": "meta",
        "cmd": "meta",
    }
    for part in parts:
        modifier = aliases.get(part.casefold())
        if modifier is None:
            keys.append(part)
        else:
            modifiers[modifier] = True
    if len(keys) != 1:
        raise ValueError("请选择一个完整的快捷键组合")
    return validate_hotkey(Hotkey(key=keys[0], **modifiers))
