import argparse
import time
import os
import sys

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
from .constants import MODEL_CHOICES
from .logger import get_logger, QUIET, INFO, DEBUG
from .logo import print_logo


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
    cfgp.add_argument(
        "--show", action="store_true", help="Show current config and exit"
    )
    cfgp.add_argument(
        "--web", action="store_true", help="Open web-based configuration UI (localhost)"
    )
    cfgp.add_argument("--port", type=int, default=8765, help="Port for --web (default: 8765)")
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


def _write_yaml_preserve_comments(path: str, data: dict) -> None:
    """Best-effort in-place YAML update that preserves comments and ordering.

    Only updates top-level scalar keys present in `data` if their lines exist.
    If a key is missing, it will be appended at the end (without comments).
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        # Fallback to simple writer
        return _write_yaml(path, data)

    import re

    updated = {k: False for k in data.keys()}

    def _to_scalar(v) -> str:
        if isinstance(v, bool):
            return "true" if v else "false"
        return str(v)

    new_lines = []
    for line in lines:
        replaced = False
        # skip pure comment lines
        stripped = line.lstrip()
        if stripped.startswith("#"):
            new_lines.append(line)
            continue
        for k, v in data.items():
            # match: <indent>key : <value> [#comment]
            # keep indentation and inline comments
            pat = rf"^(\s*{re.escape(k)}\s*:\s*)([^#\n]*?)(\s*(#.*)?)$"
            m = re.match(pat, line)
            if m:
                prefix, _old, suffix = m.group(1), m.group(2), m.group(3)
                val = _to_scalar(v)
                new_line = (
                    f"{prefix}{val}{suffix}\n"
                    if not line.endswith("\n")
                    else f"{prefix}{val}{suffix}"
                )
                new_lines.append(new_line)
                updated[k] = True
                replaced = True
                break
        if not replaced:
            new_lines.append(line)

    # append missing keys at end
    for k, v in data.items():
        if not updated.get(k, False):
            new_lines.append(f"{k}: {_to_scalar(v)}\n")

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def _run_config(args) -> int:
    # Web-based UI
    if getattr(args, "web", False):
        try:
            from .web_config.server import serve_web_config
        except Exception as e:
            print(f"Web config unavailable: {e}")
            return 1
        try:
            serve_web_config(
                port=int(getattr(args, "port", 8765) or 8765),
                open_browser=True,
                config_path=getattr(args, "config", None),
            )
        except KeyboardInterrupt:
            pass
        return 0
    cfg_path = _find_repo_config(getattr(args, "config", None))
    cfg = Config(config_path=cfg_path)
    show_logo = bool(getattr(cfg, "show_logo", True))
    logo_style = getattr(cfg, "logo_style", "simple")
    if getattr(args, "show", False):
        if show_logo:
            print_logo(use_color=True, style=logo_style)
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

        def normalize_hotkey(x: str) -> str:
            return x

        def validate_hotkey(x: str) -> bool:
            return bool(x)

    def _read_line_with_esc(prompt: str) -> tuple[bool, str]:
        """Read a line from TTY, returning (escaped, text).
        - If ESC is pressed (without Enter), returns (True, '').
        - Otherwise returns (False, the entered text without trailing newline).
        In non-TTY environments, falls back to input().
        """
        try:
            if os.name == "nt":
                import msvcrt  # type: ignore

                if not sys.stdin.isatty():
                    s = input(prompt)
                    return (False, s)
                print(prompt, end="", flush=True)
                buf: list[str] = []
                while True:
                    ch = msvcrt.getwch()
                    # Arrow/function keys start with \xe0
                    if ch == "\xe0":
                        key2 = msvcrt.getwch()
                        # Up/Down -> ignore; Left/Right -> cancel
                        if key2 in ("H", "P"):  # up, down
                            continue
                        if key2 in ("K", "M"):  # left, right
                            print()
                            return (True, "")
                        continue
                    if ch == "\x1b":  # ESC
                        print()
                        return (True, "")
                    if ch in ("\r", "\n"):
                        print()
                        return (False, "".join(buf))
                    if ch in ("\b", "\x08"):
                        if buf:
                            buf.pop()
                            # erase last char
                            print("\b \b", end="", flush=True)
                        continue
                    buf.append(ch)
                    print(ch, end="", flush=True)
            else:
                import tty
                import termios

                if not sys.stdin.isatty():
                    s = input(prompt)
                    return (False, s)
                print(prompt, end="", flush=True)
                fd = sys.stdin.fileno()
                old = termios.tcgetattr(fd)
                buf: list[str] = []
                try:
                    tty.setraw(fd)
                    while True:
                        ch = sys.stdin.read(1)
                        if ch == "\x1b":  # ESC or ANSI sequence
                            # Peek possible '[' for arrow sequence
                            sys.stdin.flush()
                            ch2 = sys.stdin.read(1)
                            if ch2 == "[":
                                ch3 = sys.stdin.read(1)
                                # Up/Down: ignore; Left/Right: cancel
                                if ch3 in ("A", "B"):  # up, down
                                    continue
                                if ch3 in ("C", "D"):  # right, left
                                    print()
                                    return (True, "")
                                # Unknown sequence: ignore
                                continue
                            # Bare ESC: cancel
                            print()
                            return (True, "")
                        if ch in ("\r", "\n"):
                            print()
                            return (False, "".join(buf))
                        if ch == "\x7f":  # backspace
                            if buf:
                                buf.pop()
                                print("\b \b", end="", flush=True)
                            continue
                        buf.append(ch)
                        print(ch, end="", flush=True)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            # fallback
            s = input(prompt)
            return (False, s)

    # Note: legacy 'record mode' hotkey editor has been removed in favor of unified list/manual UI.

    def edit_language() -> None:
        cur = cfg.language
        # Representative list + manual entry option
        options = [
            "en",
            "ja",
            "es",
            "fr",
            "de",
            "it",
            "pt",
            "zh",
            "ko",
            "hi",
            "ar",
            "ru",
            "other (type manually)",
        ]
        if sys.stdin.isatty():

            def _clr():
                try:
                    if os.name == "nt":
                        os.system("cls")
                    else:
                        print("\033[2J\033[H", end="")
                except Exception:
                    pass

            def _key():
                try:
                    if os.name == "nt":
                        import msvcrt  # type: ignore

                        ch = msvcrt.getwch()
                        if ch == "\xe0":
                            ch2 = msvcrt.getwch()
                            return ("win", ch2)
                        return ("chr", ch)
                    else:
                        import tty
                        import termios

                        fd = sys.stdin.fileno()
                        old = termios.tcgetattr(fd)
                        try:
                            tty.setraw(fd)
                            ch1 = sys.stdin.read(1)
                            if ch1 == "\x1b":
                                ch2 = sys.stdin.read(1)
                                if ch2 == "[":
                                    ch3 = sys.stdin.read(1)
                                    return ("ansi", ch3)
                                return ("esc", None)
                            return ("chr", ch1)
                        finally:
                            termios.tcsetattr(fd, termios.TCSADRAIN, old)
                except Exception:
                    return ("chr", "\n")

            # position cursor on current language if listed
            try:
                idx = options.index(cur)  # type: ignore[arg-type]
            except Exception:
                idx = 0
            while True:
                _clr()
                if bool(getattr(cfg, "show_logo", True)):
                    print_logo(
                        use_color=True, style=getattr(cfg, "logo_style", "simple")
                    )
                print("Select Language (↑/↓ to move, Enter=Choose, ESC/←/→=Cancel)")
                for i, name in enumerate(options):
                    pointer = ">" if i == idx else " "
                    star = "*" if name == cur else " "
                    print(f" {pointer} {star} {name}")
                kind, val = _key()
                if kind == "ansi":
                    if val == "A":
                        idx = (idx - 1) % len(options)
                        continue
                    if val == "B":
                        idx = (idx + 1) % len(options)
                        continue
                    if val in ("C", "D"):
                        return
                    continue
                if kind == "win":
                    if val == "H":
                        idx = (idx - 1) % len(options)
                        continue
                    if val == "P":
                        idx = (idx + 1) % len(options)
                        continue
                    if val in ("K", "M"):
                        return
                    continue
                if kind == "esc":
                    return
                if kind == "chr":
                    if val in ("\r", "\n"):
                        if options[idx].startswith("other"):
                            # manual entry prompt
                            esc2, lang2 = _read_line_with_esc(
                                f"Language code (e.g., en/ja) [{cur}] (ESC to cancel, Enter to keep): "
                            )
                            lang2 = lang2.strip()
                            if esc2:
                                return
                            if not lang2:
                                return
                            cfg.language = lang2
                            return
                        else:
                            cfg.language = options[idx]
                            return
                    if val.isdigit():
                        d = int(val)
                        if 1 <= d <= len(options):
                            if options[d - 1].startswith("other"):
                                esc2, lang2 = _read_line_with_esc(
                                    f"Language code (e.g., en/ja) [{cur}] (ESC to cancel, Enter to keep): "
                                )
                                lang2 = lang2.strip()
                                if esc2:
                                    return
                                if not lang2:
                                    return
                                cfg.language = lang2
                                return
                            cfg.language = options[d - 1]
                            return
                    continue
        else:
            esc, lang = _read_line_with_esc(
                f"Language (en/ja/es/fr/de/...) [{cur}] (ESC to cancel, Enter to keep): "
            )
            lang = lang.strip()
            if esc or lang.lower() == "esc":
                return
            if lang:
                cfg.language = lang

    def edit_model() -> None:
        cur_model = cfg.model or "small"
        options = list(MODEL_CHOICES)
        # TTY: arrow selection; non-TTY: fallback to line input
        if sys.stdin.isatty():
            # simple screen clear
            def _clr():
                try:
                    if os.name == "nt":
                        os.system("cls")
                    else:
                        print("\033[2J\033[H", end="")
                except Exception:
                    pass

            def _key():
                try:
                    if os.name == "nt":
                        import msvcrt  # type: ignore

                        ch = msvcrt.getwch()
                        if ch == "\xe0":
                            ch2 = msvcrt.getwch()
                            return ("win", ch2)
                        return ("chr", ch)
                    else:
                        import tty
                        import termios

                        fd = sys.stdin.fileno()
                        old = termios.tcgetattr(fd)
                        try:
                            tty.setraw(fd)
                            ch1 = sys.stdin.read(1)
                            if ch1 == "\x1b":
                                ch2 = sys.stdin.read(1)
                                if ch2 == "[":
                                    ch3 = sys.stdin.read(1)
                                    return ("ansi", ch3)
                                return ("esc", None)
                            return ("chr", ch1)
                        finally:
                            termios.tcsetattr(fd, termios.TCSADRAIN, old)
                except Exception:
                    return ("chr", "\n")

            idx = options.index(cur_model) if cur_model in options else 0
            while True:
                _clr()
                if bool(getattr(cfg, "show_logo", True)):
                    print_logo(
                        use_color=True, style=getattr(cfg, "logo_style", "simple")
                    )
                print("Select Model (↑/↓ to move, Enter=Choose, ESC/←/→=Cancel)")
                for i, name in enumerate(options):
                    pointer = ">" if i == idx else " "
                    star = "*" if name == cur_model else " "
                    print(f" {pointer} {star} {name}")
                kind, val = _key()
                if kind == "ansi":
                    if val == "A":  # up
                        idx = (idx - 1) % len(options)
                        continue
                    if val == "B":  # down
                        idx = (idx + 1) % len(options)
                        continue
                    if val in ("C", "D"):  # right/left => cancel
                        return
                    continue
                if kind == "win":
                    if val == "H":  # up
                        idx = (idx - 1) % len(options)
                        continue
                    if val == "P":  # down
                        idx = (idx + 1) % len(options)
                        continue
                    if val in ("K", "M"):  # left/right => cancel
                        return
                    continue
                if kind == "esc":
                    return
                if kind == "chr":
                    if val in ("\r", "\n"):
                        cfg.model = options[idx]
                        return
                    # digits quick select 1..len
                    if val.isdigit():
                        d = int(val)
                        if 1 <= d <= len(options):
                            cfg.model = options[d - 1]
                            return
                    # other keys ignored
                    continue
        else:
            allowed = set(options)
            esc, m = _read_line_with_esc(
                f"Model ({'/'.join(options)}) [{cur_model}] (ESC to cancel, Enter to keep): "
            )
            m = m.strip().lower()
            if esc or m == "esc":
                return
            if m:
                if m in allowed:
                    cfg.model = m
                else:
                    print("Invalid model; keeping current.")

    def edit_audio() -> None:
        cur = bool(getattr(cfg, "audio_feedback", True))
        esc, ans = _read_line_with_esc(
            f"Enable audio feedback? [{'Y' if cur else 'y'}/{'n' if cur else 'N'}] (ESC to cancel, Enter to keep): "
        )
        ans = ans.strip().lower()
        if esc or ans == "esc":
            return
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
        # Confirm before writing
        esc, ans = _read_line_with_esc(f"Save changes to {path}? [Y/n] (Enter=Yes): ")
        ans = ans.strip().lower()
        # Default is Yes: Enter == Yes
        if esc or ans in ("n", "no"):
            print("Canceled. Not saved.")
            return 1
        data = {
            "language": cfg.language,
            "model": cfg.model,
            "hotkey": cfg.hotkey,
            "audio_feedback": bool(getattr(cfg, "audio_feedback", True)),
        }
        # Preserve comments when possible
        _write_yaml_preserve_comments(path, data)
        print(f"Configuration saved to {path}")
        return 0

    def _edit_hotkey_list() -> None:
        cur = cfg.hotkey
        options = [
            "ctrl+space",
            "ctrl+shift",
            "ctrl+shift+space",
            "other (type manually)",
        ]

        # Manual prompt helper with validation + retry
        def _prompt_hotkey_manual(current: str) -> None:
            while True:
                esc, hk = _read_line_with_esc(
                    f"New hotkey (e.g., x, space, ctrl, ctrl+shift+space) [{current}] (ESC to cancel, Enter to keep): "
                )
                hk = hk.strip()
                if esc or not hk:
                    return
                hkn = normalize_hotkey(hk)
                if validate_hotkey(hkn):
                    cfg.hotkey = hkn
                    return
                print(
                    "Invalid hotkey; please try again or press Enter to keep current."
                )

        if sys.stdin.isatty():

            def _clr():
                try:
                    if os.name == "nt":
                        os.system("cls")
                    else:
                        print("\033[2J\033[H", end="")
                except Exception:
                    pass

            def _key():
                try:
                    if os.name == "nt":
                        import msvcrt  # type: ignore

                        ch = msvcrt.getwch()
                        if ch == "\xe0":
                            ch2 = msvcrt.getwch()
                            return ("win", ch2)
                        return ("chr", ch)
                    else:
                        import tty
                        import termios

                        fd = sys.stdin.fileno()
                        old = termios.tcgetattr(fd)
                        try:
                            tty.setraw(fd)
                            ch1 = sys.stdin.read(1)
                            if ch1 == "\x1b":
                                ch2 = sys.stdin.read(1)
                                if ch2 == "[":
                                    ch3 = sys.stdin.read(1)
                                    return ("ansi", ch3)
                                return ("esc", None)
                            return ("chr", ch1)
                        finally:
                            termios.tcsetattr(fd, termios.TCSADRAIN, old)
                except Exception:
                    return ("chr", "\n")

            try:
                idx = options.index(cur)
            except Exception:
                idx = 0
            while True:
                _clr()
                if bool(getattr(cfg, "show_logo", True)):
                    print_logo(
                        use_color=True, style=getattr(cfg, "logo_style", "simple")
                    )
                print("Select Hotkey (↑/↓ to move, Enter=Choose, ESC/←/→=Cancel)")
                for i, name in enumerate(options):
                    pointer = ">" if i == idx else " "
                    star = "*" if name == cur else " "
                    print(f" {pointer} {star} {name}")
                kind, val = _key()
                if kind == "ansi":
                    if val == "A":
                        idx = (idx - 1) % len(options)
                        continue
                    if val == "B":
                        idx = (idx + 1) % len(options)
                        continue
                    if val in ("C", "D"):
                        return
                    continue
                if kind == "win":
                    if val == "H":
                        idx = (idx - 1) % len(options)
                        continue
                    if val == "P":
                        idx = (idx + 1) % len(options)
                        continue
                    if val in ("K", "M"):
                        return
                    continue
                if kind == "esc":
                    return
                if kind == "chr":
                    if val in ("\r", "\n"):
                        choice = options[idx]
                        if choice.startswith("other"):
                            _prompt_hotkey_manual(cur)
                            return
                        else:
                            if validate_hotkey(choice):
                                cfg.hotkey = choice
                            return
                    if val.isdigit():
                        d = int(val)
                        if 1 <= d <= len(options):
                            choice = options[d - 1]
                            if choice.startswith("other"):
                                _prompt_hotkey_manual(cur)
                                return
                            else:
                                if validate_hotkey(choice):
                                    cfg.hotkey = choice
                                return
                    continue
        else:
            # Simple numbered list in non-TTY environments
            while True:
                print("Select Hotkey (type 1-4, Enter=keep current, or type a combo)")
                for i, name in enumerate(options, start=1):
                    star = "*" if name == cur else " "
                    print(f"  {i}) {name} {star}")
                sel = input("Select [1-4 or combo]: ").strip()
                if not sel:
                    return
                if sel.isdigit():
                    d = int(sel)
                    if 1 <= d <= len(options):
                        choice = options[d - 1]
                        if choice.startswith("other"):
                            _prompt_hotkey_manual(cur)
                            return
                        if validate_hotkey(choice):
                            cfg.hotkey = choice
                            return
                        print(
                            "Invalid hotkey; try again or press Enter to keep current."
                        )
                        continue
                    print("Invalid selection; try again.")
                    continue
                # treat as direct text input
                hkn = normalize_hotkey(sel)
                if validate_hotkey(hkn):
                    cfg.hotkey = hkn
                    return
                print("Invalid hotkey; try again.")
                continue

    # simple (numbered) menu for accessibility and testability
    simple = os.getenv("PT_SIMPLE_UI") == "1" or not sys.stdin.isatty()
    if simple:
        if show_logo:
            print_logo(use_color=True, style=logo_style)
        while True:
            print("PressTalk Configuration")
            print("- Type 1-6 then Enter to select. Ctrl+C to cancel.")
            print("- In editors: press Enter with no input to keep current value.")
            print(f"  1) Hotkey: {cfg.hotkey}")
            print(f"  2) Language: {cfg.language}")
            print(f"  3) Model: {cfg.model}")
            print(f"  4) Audio feedback: {getattr(cfg, 'audio_feedback', True)}")
            print("  5) Save changes")
            print("  6) Quit (discard)")
            sel = input("Select [1-6]: ").strip()
            if sel == "1":
                _edit_hotkey_list()
            elif sel == "2":
                edit_language()
            elif sel == "3":
                edit_model()
            elif sel == "4":
                edit_audio()
            elif sel == "5":
                rc = save_and_exit()
                if rc == 0:
                    return 0
                # else back to menu
            elif sel == "6":
                print("Aborted. No changes saved.")
                return 0
            else:
                continue
    else:
        # Arrow-key interactive menu (TTY)
        items = [
            ("Hotkey", _edit_hotkey_list),
            ("Language", edit_language),
            ("Model", edit_model),
            ("Audio feedback", edit_audio),
            ("Save changes", None),
            ("Quit (discard)", None),
        ]

        def _clear_screen() -> None:
            try:
                if sys.stdout.isatty():
                    if os.name == "nt":
                        os.system("cls")
                    else:
                        # ANSI clear + home
                        print("\033[2J\033[H", end="")
            except Exception:
                pass

        def _render(idx: int) -> None:
            _clear_screen()
            if show_logo:
                print_logo(use_color=True, style=logo_style)
            print("PressTalk Configuration")
            for i, (label, _) in enumerate(items, start=1):
                pointer = ">" if (i - 1) == idx else " "
                value = {
                    0: cfg.hotkey,
                    1: cfg.language,
                    2: cfg.model,
                    3: str(getattr(cfg, "audio_feedback", True)),
                }.get(i - 1, "")
                if value:
                    print(f" {pointer} {i}) {label}: {value}")
                else:
                    print(f" {pointer} {i}) {label}")
            print(
                "Use ↑/↓ or j/k to navigate, Enter to select, digits 1-6 for shortcut, q to quit."
            )
            try:
                sys.stdout.flush()
            except Exception:
                pass

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
                import tty
                import termios

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
                _edit_hotkey_list()
            elif sel == 2:
                edit_language()
            elif sel == 3:
                edit_model()
            elif sel == 4:
                edit_audio()
            elif sel == 5:
                rc = save_and_exit()
                if rc == 0:
                    return 0
                # else back to menu
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
