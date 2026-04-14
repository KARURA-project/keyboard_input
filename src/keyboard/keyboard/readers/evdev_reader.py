import threading
from typing import Optional

from evdev import InputDevice, categorize, ecodes
from evdev.events import KeyEvent

from .base import KeyboardReaderBase


class EvdevKeyboardReader(KeyboardReaderBase):
    """
    evdev を使って Linux input event からキー押下状態を読むクラス．
    """

    def __init__(self, device_path: str, logger) -> None:
        self._logger = logger
        self._lock = threading.Lock()
        self._pressed: set[str] = set()
        self._running = True

        self._device = self._open_device(device_path)
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def snapshot(self) -> list[str]:
        with self._lock:
            return sorted(self._pressed)

    def shutdown(self) -> None:
        self._running = False
        try:
            self._device.close()
        except Exception:
            pass
        self._thread.join(timeout=1.0)

    def _open_device(self, device_path: str) -> InputDevice:
        dev = InputDevice(device_path)
        self._logger.info(
            f"Using evdev keyboard device: path={dev.path}, name={dev.name}"
        )
        return dev

    def _read_loop(self) -> None:
        try:
            for event in self._device.read_loop():
                if not self._running:
                    break

                if event.type != ecodes.EV_KEY:
                    continue

                key_event = categorize(event)
                if not isinstance(key_event, KeyEvent):
                    continue

                key_names = self._normalize_keycodes(key_event.keycode)
                if not key_names:
                    continue

                with self._lock:
                    if key_event.keystate == KeyEvent.key_down:
                        for key in key_names:
                            self._pressed.add(key)
                    elif key_event.keystate == KeyEvent.key_up:
                        for key in key_names:
                            self._pressed.discard(key)
                    elif key_event.keystate == KeyEvent.key_hold:
                        pass

        except OSError as e:
            if self._running:
                self._logger.error(f"Evdev read loop stopped: {e}")
        except Exception as e:
            self._logger.error(f"Unexpected evdev read loop error: {e}")

    @staticmethod
    def _normalize_keycodes(keycode) -> list[str]:
        raw_codes: list[str]
        if isinstance(keycode, list):
            raw_codes = [str(k) for k in keycode]
        else:
            raw_codes = [str(keycode)]

        normalized: list[str] = []
        for code in raw_codes:
            key = EvdevKeyboardReader._normalize_single_keycode(code)
            if key is not None:
                normalized.append(key)

        seen = set()
        unique: list[str] = []
        for k in normalized:
            if k not in seen:
                seen.add(k)
                unique.append(k)

        return unique

    @staticmethod
    def _normalize_single_keycode(code: str) -> Optional[str]:
        code = code.strip().upper()
        if not code.startswith("KEY_"):
            return None

        name = code.removeprefix("KEY_")

        special_map = {
            "LEFTSHIFT": "shift",
            "RIGHTSHIFT": "shift",
            "LEFTCTRL": "ctrl",
            "RIGHTCTRL": "ctrl",
            "LEFTALT": "alt",
            "RIGHTALT": "alt",
            "SPACE": "space",
            "ESC": "escape",
            "ENTER": "enter",
            "BACKSPACE": "backspace",
            "TAB": "tab",
            "UP": "up",
            "DOWN": "down",
            "LEFT": "left",
            "RIGHT": "right",
            "MINUS": "-",
            "EQUAL": "=",
            "COMMA": ",",
            "DOT": ".",
            "SLASH": "/",
            "SEMICOLON": ";",
            "APOSTROPHE": "'",
            "LEFTBRACE": "[",
            "RIGHTBRACE": "]",
            "BACKSLASH": "\\",
            "GRAVE": "`",
        }

        if name in special_map:
            return special_map[name]

        if len(name) == 1:
            return name.lower()

        if name.startswith("F") and name[1:].isdigit():
            return name.lower()

        return name.lower()