import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import presstalk.cli as cli  # type: ignore


class TestCliRefactor(unittest.TestCase):
    def test_build_parser_simulate_defaults(self):
        p = cli.build_parser()
        args = p.parse_args(["simulate"])
        self.assertEqual(args.cmd, "simulate")
        self.assertEqual(args.chunks, ["aa", "bb", "cc"])  # default
        self.assertEqual(args.delay_ms, 50)

    def test_build_parser_run_flags_parse(self):
        p = cli.build_parser()
        args = p.parse_args(
            [
                "run",
                "--mode",
                "toggle",
                "--console",
                "--hotkey",
                "cmd",
                "--log-level",
                "DEBUG",
                "--language",
                "ja",
                "--model",
                "small",
                "--prebuffer-ms",
                "123",
                "--min-capture-ms",
                "456",
            ]
        )
        self.assertEqual(args.cmd, "run")
        self.assertEqual(args.mode, "toggle")
        self.assertTrue(args.console)
        self.assertEqual(args.hotkey, "cmd")
        self.assertEqual(args.log_level, "DEBUG")
        self.assertEqual(args.language, "ja")
        self.assertEqual(args.model, "small")
        self.assertEqual(args.prebuffer_ms, 123)
        self.assertEqual(args.min_capture_ms, 456)

    def test_build_parser_version_flag(self):
        p = cli.build_parser()
        args = p.parse_args(["--version"])
        self.assertTrue(args.version)

    def test_find_repo_config_prefers_explicit(self):
        explicit = os.path.abspath("presstalk.yaml")
        self.assertTrue(os.path.isfile(explicit))
        # Should return explicit when provided
        got = cli._find_repo_config(explicit)
        self.assertEqual(os.path.abspath(got), explicit)

    def test_find_repo_config_repo_root(self):
        # When no explicit is provided, should find repository root yaml if present
        got = cli._find_repo_config(None)
        self.assertIsNotNone(got)
        self.assertTrue(str(got).endswith("presstalk.yaml"))

    def test_run_simulate_happy_path(self):
        args = SimpleNamespace(config=None, chunks=["aa"], delay_ms=1)
        # Patch heavy deps
        with (
            mock.patch.object(cli, "print_logo"),
            mock.patch.object(cli, "RingBuffer") as _m_ring,
            mock.patch.object(cli, "DummyAsrEngine") as _m_eng,
            mock.patch.object(cli, "Controller") as _m_ctl,
            mock.patch.object(cli, "PCMCapture") as m_cap,
            mock.patch.object(cli, "Orchestrator") as m_orch,
        ):
            m_cap.return_value.is_running.return_value = False
            m_orch.return_value.press.return_value = None
            m_orch.return_value.release.return_value = "ok"
            rc = cli._run_simulate(args)
            self.assertEqual(rc, 0)
            self.assertTrue(m_orch.called)

    def test_run_ptt_console_quick_exit(self):
        # Minimal args for console path
        args = SimpleNamespace(
            config=None,
            language=None,
            model=None,
            prebuffer_ms=None,
            min_capture_ms=None,
            mode="hold",
            console=True,
            hotkey=None,
            log_level="QUIET",
        )

        class FakeCapture:
            def is_running(self):
                return False

        class FakeOrch:
            def __init__(self):
                self.capture = FakeCapture()
                self.is_finalizing = False

        with (
            mock.patch.object(cli, "_build_run_orchestrator", return_value=FakeOrch()),
            mock.patch.object(cli, "get_logger") as m_logger,
            mock.patch.object(cli, "HotkeyHandler") as _m_hk,
            mock.patch.object(cli, "_StatusOrch", side_effect=lambda o: o),
            mock.patch("builtins.input", side_effect=["q"]),
        ):
            rc = cli._run_ptt(args)
            self.assertEqual(rc, 0)
            # Quiet level set
            self.assertTrue(m_logger.return_value.set_level.called)


if __name__ == "__main__":
    unittest.main()
