import os

import pygame

from .base import KeyboardReaderBase


class PygameKeyboardReader(KeyboardReaderBase):
    """
    pygame を使って GUI 環境でキー押下状態を読むクラス．
    UTM など evdev が使えない環境向けの開発用バックエンド．
    """

    def __init__(self, logger, window_width: int = 320, window_height: int = 120) -> None:
        self._logger = logger
        self._pressed: set[str] = set()

        if "DISPLAY" not in os.environ and "WAYLAND_DISPLAY" not in os.environ:
            raise RuntimeError("pygame backend requires GUI environment.")

        pygame.init()
        pygame.display.set_caption("keyboard_node")
        self._screen = pygame.display.set_mode((window_width, window_height))
        self._clock = pygame.time.Clock()

        self._logger.info("Using pygame keyboard backend.")

    def snapshot(self) -> list[str]:
        self._pump_events()
        return sorted(self._pressed)

    def shutdown(self) -> None:
        pygame.quit()

    def _pump_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continue

        key_states = pygame.key.get_pressed()
        pressed: set[str] = set()

        # 英数字
        for c in "abcdefghijklmnopqrstuvwxyz0123456789":
            key_code = getattr(pygame, f"K_{c}")
            if key_states[key_code]:
                pressed.add(c)

        # 特殊キー
        special_map = {
            "shift": [pygame.K_LSHIFT, pygame.K_RSHIFT],
            "ctrl": [pygame.K_LCTRL, pygame.K_RCTRL],
            "alt": [pygame.K_LALT, pygame.K_RALT],
            "space": [pygame.K_SPACE],
            "escape": [pygame.K_ESCAPE],
            "enter": [pygame.K_RETURN],
            "backspace": [pygame.K_BACKSPACE],
            "tab": [pygame.K_TAB],
            "up": [pygame.K_UP],
            "down": [pygame.K_DOWN],
            "left": [pygame.K_LEFT],
            "right": [pygame.K_RIGHT],
            "-": [pygame.K_MINUS],
            "=": [pygame.K_EQUALS],
            ",": [pygame.K_COMMA],
            ".": [pygame.K_PERIOD],
            "/": [pygame.K_SLASH],
            ";": [pygame.K_SEMICOLON],
            "'": [pygame.K_QUOTE],
            "[": [pygame.K_LEFTBRACKET],
            "]": [pygame.K_RIGHTBRACKET],
            "\\": [pygame.K_BACKSLASH],
            "`": [pygame.K_BACKQUOTE],
        }

        for name, codes in special_map.items():
            if any(key_states[code] for code in codes):
                pressed.add(name)

        self._pressed = pressed

        # GUI を固めないため
        self._screen.fill((30, 30, 30))
        pygame.display.flip()
        self._clock.tick(120)