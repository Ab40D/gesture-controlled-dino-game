"""Keyboard control of the Chrome Dino game through PyAutoGUI.

The controller never talks to Chrome directly: it simply emits a real SPACE
key press, and whichever window currently has focus (the Dino game) receives
it.  A configurable startup delay guarantees that no key is sent before the
user has had time to focus the game window.
"""

from __future__ import annotations

import time

import pyautogui

import config


class DinoController:
    """Sends single, never-held SPACE presses to the focused window."""

    def __init__(self, startup_delay: float = config.STARTUP_DELAY) -> None:
        pyautogui.FAILSAFE = True  # slam the mouse into a screen corner to abort
        pyautogui.PAUSE = 0.0      # no artificial pause -> jumps stay snappy

        self._startup_delay = startup_delay
        self._start_time = time.monotonic()
        self.jump_count = 0

        # Cheap sanity check: on Linux this raises when no usable display or
        # keyboard is available, so we fail early with a clear message instead
        # of blowing up at the first jump.
        try:
            pyautogui.size()
        except Exception as exc:
            raise RuntimeError(
                "PyAutoGUI cannot access your display/keyboard. On Linux run "
                "inside an X11 session (PyAutoGUI does not work on Wayland) "
                "and install python-xlib."
            ) from exc

    # -------------------------------------------------------------- properties
    @property
    def startup_remaining(self) -> float:
        """Seconds left before the controller is allowed to press keys."""
        elapsed = time.monotonic() - self._start_time
        return max(0.0, self._startup_delay - elapsed)

    @property
    def ready(self) -> bool:
        """True once the startup delay has fully elapsed."""
        return self.startup_remaining <= 0.0

    # ------------------------------------------------------------------- API
    def jump(self) -> bool:
        """Press SPACE exactly once. Returns True if the key was sent.

        press() is a keyDown immediately followed by a keyUp - the key is
        never held down, so the Dino performs one normal jump per event.
        """
        if not self.ready:
            return False
        # FailSafeException is intentionally NOT caught here: it is the user's
        # emergency stop and is handled gracefully in main().
        pyautogui.press("space")
        self.jump_count += 1
        return True
