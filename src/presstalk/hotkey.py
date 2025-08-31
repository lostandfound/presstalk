class HotkeyHandler:
    """Simple hotkey state machine supporting 'hold' and 'toggle' modes.

    This does not register OS-level hooks; it just exposes handle_key_down/up
    for tests and for integration with actual hook backends.
    """

    def __init__(self, orchestrator, *, mode: str = 'hold') -> None:
        self.orch = orchestrator
        self.mode = mode  # 'hold' or 'toggle'
        self._down = False
        self._active = False  # for toggle mode

    def handle_key_down(self):
        if self.mode == 'hold':
            if not self._down:
                self._down = True
                self.orch.press()
        else:  # toggle
            if not self._down:
                self._down = True
                if not self._active:
                    self.orch.press()
                    self._active = True
                else:
                    self.orch.release()
                    self._active = False

    def handle_key_up(self):
        if self.mode == 'hold':
            if self._down:
                self._down = False
                self.orch.release()
        else:
            # toggle ignores key up; only resets _down
            self._down = False

