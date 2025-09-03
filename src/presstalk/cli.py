import argparse
import time
import os

from . import __version__
from .config import Config
from .ring_buffer import RingBuffer
from .controller import Controller
from .capture import PCMCapture
from .orchestrator import Orchestrator
from .beep import beep as system_beep
from .paste import insert_text
from .hotkey import HotkeyHandler
from .engine.dummy_engine import DummyAsrEngine
from .logger import get_logger, QUIET, INFO, DEBUG
from .logo import print_logo
from .beep import beep as system_beep


def _build_run_orchestrator(cfg: Config) -> Orchestrator:
    # Ring for prebuffer
    pre_bytes = int(cfg.bytes_per_second * (cfg.prebuffer_ms / 1000.0))
    ring = RingBuffer(max(1, pre_bytes or 1))

    # Engine backend with progress display
    try:
        from .engine.fwhisper_backend import FasterWhisperBackend
        from .engine.fwhisper_engine import FasterWhisperEngine
    except Exception as e:
        raise RuntimeError(f"engine modules unavailable: {e}")

    backend = FasterWhisperBackend(model=cfg.model, show_progress=True)
    engine = FasterWhisperEngine(
        sample_rate=cfg.sample_rate,
        language=cfg.language,
        model=cfg.model,
        backend=backend,
    )

    # Capture source (sounddevice)
    try:
        from .capture_sd import SoundDeviceSource
    except Exception as e:
        raise RuntimeError(f"capture module unavailable: {e}")

    source = SoundDeviceSource(
        sample_rate=cfg.sample_rate,
        channels=cfg.channels,
        frames_per_block=max(160, int(cfg.sample_rate * cfg.channels * 0.02)),
    )
    capture = PCMCapture(
        sample_rate=cfg.sample_rate, channels=cfg.channels, chunk_ms=20, source=source
    )

    controller = Controller(
        engine,
        ring,
        prebuffer_ms=cfg.prebuffer_ms,
        min_capture_ms=cfg.min_capture_ms,
        bytes_per_second=cfg.bytes_per_second,
        language=cfg.language,
    )

    def _paste(text: str) -> bool:
        return insert_text(
            text, guard_enabled=cfg.paste_guard, blocklist=cfg.paste_blocklist
        )

    orch = Orchestrator(
        controller=controller,
        ring=ring,
        capture=capture,
        paste_fn=_paste,
        audio_feedback=getattr(cfg, "audio_feedback", True),
        beep_fn=system_beep,
    )
    return orch


class _StatusOrch:
    """Orchestrator wrapper that prints simple status and protects finalize phase."""

    def __init__(self, orch: Orchestrator) -> None:
        self._o = orch
        self.is_finalizing = False

    def __getattr__(self, name):  # delegate to underlying orchestrator
        return getattr(self._o, name)

    def press(self):
        # avoid re-press spam
        try:
            if getattr(self._o.controller, "is_recording", lambda: False)():
                return
        except Exception:
            pass
        from .logger import get_logger

        get_logger().info("[PT] Recording...")
        return self._o.press()

    def release(self):
        # ignore if not recording or already finalizing
        try:
            rec = getattr(self._o.controller, "is_recording", lambda: False)()
        except Exception:
            rec = True
        if self.is_finalizing or not rec:
            return ""
        self.is_finalizing = True
        from .logger import get_logger

        get_logger().info("[PT] Finalizing...")
        try:
            import time as _t

            _t0 = _t.time()
            text = self._o.release()
            eng_time = _t.time() - _t0
            st = self._o.stats()
            try:
                approx_sec = st["bytes"] / max(1, st["bytes_per_second"]) if st else 0
            except Exception:
                approx_sec = 0
            get_logger().info(
                f"[PT] Stats: bytes={st.get('bytes', 0)} duration={st.get('duration_s', 0):.2f}s (~{approx_sec:.2f}s audio)"
            )
            get_logger().info(f"[PT] Engine: {eng_time:.2f}s")
            if text:
                get_logger().info("[PT] Final: " + text)
            else:
                get_logger().info("[PT] No transcription produced.")
            return text
        finally:
            self.is_finalizing = False


class _DummySource:
    def __init__(self, chunks, delay_s=0.0):
        self._chunks = list(chunks)
        self._delay = delay_s

    def start(self):
        pass

    def read(self, nbytes: int):
        if self._delay:
            time.sleep(self._delay)
        if not self._chunks:
            return None
        return self._chunks.pop(0)

    def stop(self):
        pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="presstalk", description="Local push-to-talk (WIP)"
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    sub = parser.add_subparsers(dest="cmd")

    sim = sub.add_parser(
        "simulate", help="Run a simulated press using dummy capture/engine"
    )
    sim.add_argument("--config", help="Path to YAML config (presstalk.yaml)")
    sim.add_argument(
        "--chunks",
        nargs="*",
        default=["aa", "bb", "cc"],
        help="List of ASCII chunks to feed (default: aa bb cc)",
    )
    sim.add_argument(
        "--delay-ms", type=int, default=50, help="Delay between chunks (ms)"
    )

    runp = sub.add_parser("run", help="Run local PTT (global hotkey by default)")
    runp.add_argument("--config", help="Path to YAML config (presstalk.yaml)")
    runp.add_argument(
        "--mode", choices=["hold", "toggle"], default=None, help="PTT mode"
    )
    runp.add_argument(
        "--console",
        action="store_true",
        help="Use console input instead of global hotkey",
    )
    runp.add_argument(
        "--hotkey", default=None, help="Hotkey combo (e.g., shift+space, ctrl+shift+x)"
    )
    runp.add_argument(
        "--log-level",
        choices=["QUIET", "INFO", "DEBUG"],
        default="INFO",
        help="Logging level",
    )
    runp.add_argument("--language", default=None, help="Override language (e.g., ja)")
    runp.add_argument("--model", default=None, help="Override model (e.g., small)")
    runp.add_argument(
        "--prebuffer-ms",
        type=int,
        default=None,
        help="Prebuffer milliseconds (0..300 recommended)",
    )
    runp.add_argument(
        "--min-capture-ms",
        type=int,
        default=None,
        help="Minimum capture ms (e.g., 1800)",
    )
    # config subcommand
    cfgp = sub.add_parser("config", help="Interactive configuration editor")
    cfgp.add_argument("--config", help="Path to YAML config (presstalk.yaml)")
    cfgp.add_argument("--show", action="store_true", help="Show current config and exit")
    return parser


def _find_repo_config(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    try:
        pkg_dir = os.path.dirname(__file__)  # src/presstalk
        repo_root = os.path.abspath(os.path.join(pkg_dir, "..", ".."))
        candidate = os.path.join(repo_root, "presstalk.yaml")
        if os.path.isfile(candidate):
            return candidate
    except Exception:
        pass
    return None


def _run_simulate(args) -> int:
    cfg_path = _find_repo_config(getattr(args, "config", None))
    cfg = Config(config_path=cfg_path)
    if getattr(cfg, "show_logo", True):
        print_logo(use_color=True, style=getattr(cfg, "logo_style", "simple"))
    bps = cfg.bytes_per_second
    pre_bytes = int(bps * (cfg.prebuffer_ms / 1000.0))
    ring = RingBuffer(max(1, pre_bytes or 1))
    eng = DummyAsrEngine()
    ctl = Controller(
        eng,
        ring,
        prebuffer_ms=cfg.prebuffer_ms,
        min_capture_ms=cfg.min_capture_ms,
        bytes_per_second=bps,
        language=cfg.language,
    )
    src = _DummySource(
        [c.encode("utf-8") for c in getattr(args, "chunks", ["aa"])],
        delay_s=(getattr(args, "delay_ms", 50) / 1000.0),
    )
    cap = PCMCapture(
        sample_rate=cfg.sample_rate, channels=cfg.channels, chunk_ms=10, source=src
    )
    orch = Orchestrator(
        controller=ctl,
        ring=ring,
        capture=cap,
        paste_fn=lambda t: print("FINAL:", t) or True,
        audio_feedback=getattr(cfg, "audio_feedback", True),
        beep_fn=system_beep,
    )
    orch.press()
    while cap.is_running():
        time.sleep(0.01)
    text = orch.release()
    print("DONE:", text)
    return 0


def _run_ptt(args) -> int:
    cfg_path = _find_repo_config(getattr(args, "config", None))
    cfg = Config(config_path=cfg_path)
    if getattr(cfg, "show_logo", True):
        print_logo(use_color=True, style=getattr(cfg, "logo_style", "simple"))
    # overlay CLI options
    for k in ("language", "model"):
        v = getattr(args, k, None)
        if v:
            setattr(cfg, k, v)
    if getattr(args, "prebuffer_ms", None) is not None:
        cfg.prebuffer_ms = int(args.prebuffer_ms)
    if getattr(args, "min_capture_ms", None) is not None:
        cfg.min_capture_ms = int(args.min_capture_ms)
    effective_mode = getattr(args, "mode", None) or getattr(cfg, "mode", None) or "hold"
    effective_hotkey = (
        getattr(args, "hotkey", None) or getattr(cfg, "hotkey", None) or "ctrl+space"
    )
    try:
        orch = _build_run_orchestrator(cfg)
    except Exception as e:
        print(f"Error initializing: {e}")
        print("- Ensure 'sounddevice', 'numpy', and 'faster-whisper' are installed.")
        return 1
    # logger
    lvl = {"QUIET": QUIET, "INFO": INFO, "DEBUG": DEBUG}[
        getattr(args, "log_level", "INFO")
    ]
    get_logger().set_level(lvl)
    if not getattr(args, "console", False):
        try:
            from .hotkey_pynput import GlobalHotkeyRunner
        except Exception as e:
            print(f"Global hotkey not available: {e}")
            return 1
        orch = _StatusOrch(orch)
        runner = GlobalHotkeyRunner(
            orch, mode=effective_mode, key_name=effective_hotkey
        )
        runner.start()
        get_logger().info(
            f"✓ Ready for voice input (press {effective_hotkey} to start)"
        )
        try:
            while True:
                time.sleep(0.2)
        except KeyboardInterrupt:
            pass
        finally:
            runner.stop()
        return 0
    # console mode
    orch = _StatusOrch(orch)
    hk = HotkeyHandler(orch, mode=effective_mode)
    get_logger().info("✓ Ready for voice input (console mode). Commands:")
    if effective_mode == "hold":
        get_logger().info(
            "- Type 'p'+Enter to press, 'r'+Enter to release, 'q'+Enter to quit"
        )
    else:
        get_logger().info("- Type 't'+Enter to toggle, 'q'+Enter to quit")
    try:
        while True:
            cmd = input("> ").strip().lower()
            if cmd == "q":
                if getattr(orch, "is_finalizing", False):
                    print("[PT] Finalizing... please wait")
                    continue
                try:
                    if orch.capture.is_running():
                        orch.capture.stop()
                except Exception:
                    pass
                break
            if effective_mode == "hold":
                if cmd == "p":
                    hk.handle_key_down()
                elif cmd == "r":
                    hk.handle_key_up()
            else:
                if cmd == "t":
                    hk.handle_key_down()
                    hk.handle_key_up()
    except KeyboardInterrupt:
        pass
    return 0


def _write_yaml(path: str, data: dict) -> None:
    lines = []
    for k, v in data.items():
        if isinstance(v, bool):
            vv = "true" if v else "false"
        else:
            vv = str(v)
        lines.append(f"{k}: {vv}\n")
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def _run_config(args) -> int:
    cfg_path = _find_repo_config(getattr(args, "config", None))
    cfg = Config(config_path=cfg_path)
    if getattr(args, "show", False):
        print("PressTalk Configuration (read-only)")
        print(f"Current hotkey: {cfg.hotkey}")
        print(f"Current language: {cfg.language}")
        print(f"Current model: {cfg.model}")
        print(f"Audio feedback: {getattr(cfg, 'audio_feedback', True)}")
        return 0

    # editors
    try:
        from .hotkey_pynput import validate_hotkey, normalize_hotkey
    except Exception:
        def normalize_hotkey(x: str) -> str: return x
        def validate_hotkey(x: str) -> bool: return bool(x)

    def edit_hotkey() -> None:
        cur = cfg.hotkey
        for _ in range(2):
            hk = input(
                f"New hotkey (e.g., ctrl+space, ctrl+shift+x) [{cur}]: "
            ).strip()
            if not hk:
                return
            hk = normalize_hotkey(hk)
            if validate_hotkey(hk):
                cfg.hotkey = hk
                return
            print("Invalid hotkey; please try again or press Enter to keep current.")

    def edit_language() -> None:
        cur = cfg.language
        lang = input(f"Language (en/ja/es/fr/de/...) [{cur}]: ").strip()
        if lang:
            cfg.language = lang

    def edit_model() -> None:
        cur_model = cfg.model or "small"
        allowed = {"tiny", "base", "small", "medium", "large"}
        m = input(f"Model (tiny/base/small/medium/large) [{cur_model}]: ").strip().lower()
        if m:
            if m in allowed:
                cfg.model = m
            else:
                print("Invalid model; keeping current.")

    def edit_audio() -> None:
        cur = bool(getattr(cfg, "audio_feedback", True))
        ans = input(
            f"Enable audio feedback? [{'Y' if cur else 'y'}/{'n' if cur else 'N'}]: "
        ).strip().lower()
        if ans in ("y", "yes"):
            cfg.audio_feedback = True
        elif ans in ("n", "no"):
            cfg.audio_feedback = False

    def save_and_exit() -> int:
        path = cfg_path
        if not path:
            pkg_dir = os.path.dirname(__file__)
            repo_root = os.path.abspath(os.path.join(pkg_dir, "..", ".."))
            path = os.path.join(repo_root, "presstalk.yaml")
        data = {
            "language": cfg.language,
            "model": cfg.model,
            "hotkey": cfg.hotkey,
            "audio_feedback": bool(getattr(cfg, "audio_feedback", True)),
        }
        _write_yaml(path, data)
        print(f"Configuration saved to {path}")
        return 0

    # simple (numbered) menu for accessibility and testability
    simple = os.getenv("PT_SIMPLE_UI") == "1" or not sys.stdin.isatty()
    if simple:
        while True:
            print("PressTalk Configuration")
            print(f"  1) Hotkey: {cfg.hotkey}")
            print(f"  2) Language: {cfg.language}")
            print(f"  3) Model: {cfg.model}")
            print(f"  4) Audio feedback: {getattr(cfg, 'audio_feedback', True)}")
            print("  5) Save changes")
            print("  6) Quit (discard)")
            sel = input("Select [1-6]: ").strip()
            if sel == "1":
                edit_hotkey()
            elif sel == "2":
                edit_language()
            elif sel == "3":
                edit_model()
            elif sel == "4":
                edit_audio()
            elif sel == "5":
                return save_and_exit()
            elif sel == "6":
                print("Aborted. No changes saved.")
                return 0
            else:
                continue
    else:
        # Arrow-key interactive menu (TTY)
        items = [
            ("Hotkey", edit_hotkey),
            ("Language", edit_language),
            ("Model", edit_model),
            ("Audio feedback", edit_audio),
            ("Save changes", None),
            ("Quit (discard)", None),
        ]

        def _render(idx: int) -> None:
            # Clear screen minimal: print separators for simplicity (no ANSI)
            print("PressTalk Configuration")
            for i, (label, _) in enumerate(items, start=1):
                pointer = ">" if (i - 1) == idx else " "
                value = {
                    0: cfg.hotkey,
                    1: cfg.language,
                    2: cfg.model,
                    3: str(getattr(cfg, 'audio_feedback', True)),
                }.get(i - 1, "")
                if value:
                    print(f" {pointer} {i}) {label}: {value}")
                else:
                    print(f" {pointer} {i}) {label}")
            print("Use ↑/↓ or j/k to navigate, Enter to select, digits 1-6 for shortcut, q to quit.")

        def _get_key():
            import sys
            try:
                import msvcrt  # type: ignore
                if msvcrt.kbhit():
                    ch = msvcrt.getch()
                else:
                    ch = msvcrt.getch()
                return ch
            except Exception:
                import tty, termios
                fd = sys.stdin.fileno()
                old = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    ch1 = sys.stdin.read(1)
                    if ch1 == "\x1b":  # ESC sequence
                        ch2 = sys.stdin.read(1)
                        if ch2 == "[":
                            ch3 = sys.stdin.read(1)
                            return (ch1 + ch2 + ch3).encode()
                        return (ch1 + ch2).encode()
                    return ch1.encode()
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)

        idx = 0
        while True:
            _render(idx)
            k = _get_key()
            # Windows arrows: b'\xe0H'(up), b'\xe0P'(down); Enter b'\r'
            # POSIX arrows: b'\x1b[A'(up), b'\x1b[B'(down); Enter b'\n'
            try:
                if k in (b"\x1b", b"q"):  # ESC or 'q'
                    print("Aborted. No changes saved.")
                    return 0
                if k in (b"j",):
                    idx = (idx + 1) % len(items)
                    continue
                if k in (b"k",):
                    idx = (idx - 1) % len(items)
                    continue
                if k in (b"\xe0H", b"\x1b[A"):
                    idx = (idx - 1) % len(items)
                    continue
                if k in (b"\xe0P", b"\x1b[B"):
                    idx = (idx + 1) % len(items)
                    continue
                if k in (b"\r", b"\n"):
                    sel = idx + 1
                elif k and k[:1].isdigit():
                    sel = int(k[:1].decode())
                else:
                    # ignore other keys
                    continue
            except Exception:
                continue

            if sel == 1:
                edit_hotkey()
            elif sel == 2:
                edit_language()
            elif sel == 3:
                edit_model()
            elif sel == 4:
                edit_audio()
            elif sel == 5:
                return save_and_exit()
            elif sel == 6:
                print("Aborted. No changes saved.")
                return 0
            idx = min(idx, len(items) - 1)


def main():
    parser = build_parser()
    args = parser.parse_args()
    if getattr(args, "version", False):
        print(f"presstalk {__version__}")
        return 0
    if not getattr(args, "cmd", None):
        args = parser.parse_args(["run"])  # populate defaults
    if args.cmd == "simulate":
        return _run_simulate(args)
    if args.cmd == "run":
        return _run_ptt(args)
    if args.cmd == "config":
        return _run_config(args)
    parser.print_help()
    return 0
