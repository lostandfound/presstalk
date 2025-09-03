import io
import shutil
from pathlib import Path
from unittest import TestCase, mock

import task


class TestTaskRunner(TestCase):
    def test_help_task_prints_usage(self):
        buf = io.StringIO()
        with mock.patch("sys.stdout", buf):
            rc = task.main(["help"])
        self.assertEqual(rc, 0)
        self.assertIn("Cross-platform tasks for PressTalk", buf.getvalue())

    def test_install_dry_run(self):
        with mock.patch.object(task, "subprocess") as m_sub:
            rc = task.main(["--dry-run", "-v", "install"])
            self.assertEqual(rc, 0)
            m_sub.call.assert_not_called()

    def test_test_all_and_file_dry_run(self):
        with mock.patch.object(task, "subprocess") as m_sub:
            rc = task.main(["--dry-run", "-v", "test"])
            self.assertEqual(rc, 0)
            m_sub.call.assert_not_called()

        with mock.patch.object(task, "subprocess") as m_sub:
            rc = task.main(
                ["--dry-run", "-v", "test", "--file", "tests/test_controller.py"]
            )
            self.assertEqual(rc, 0)
            m_sub.call.assert_not_called()

    def test_simulate_and_run_dry_run(self):
        with mock.patch.object(task, "subprocess") as m_sub:
            rc = task.main(
                [
                    "--dry-run",
                    "-v",
                    "simulate",
                    "--chunks",
                    "hello",
                    "world",
                    "--delay-ms",
                    "40",
                ]
            )
            self.assertEqual(rc, 0)
            m_sub.call.assert_not_called()

    def test_install_global_with_uv(self):
        with mock.patch.object(task, "which", return_value="/usr/bin/uv"):
            with mock.patch.object(task, "subprocess") as m_sub:
                m_sub.call.return_value = 0
                rc = task.main(["install-global"])
                self.assertEqual(rc, 0)
                m_sub.call.assert_called_with(
                    ["uv", "tool", "install", "--editable", "."]
                )

    def test_bootstrap_prefers_uv(self):
        with mock.patch.object(task, "which", side_effect=["/usr/bin/uv"]):
            with mock.patch.object(task, "subprocess") as m_sub:
                m_sub.call.return_value = 0
                rc = task.main(["bootstrap"])
                self.assertEqual(rc, 0)
                m_sub.call.assert_called_with(
                    ["uv", "tool", "install", "--editable", "."]
                )

    def test_bootstrap_uses_pipx_when_no_uv(self):
        with mock.patch.object(task, "which", side_effect=[None, "/usr/bin/pipx"]):
            with mock.patch.object(task, "subprocess") as m_sub:
                m_sub.call.return_value = 0
                rc = task.main(["bootstrap"])
                self.assertEqual(rc, 0)
                m_sub.call.assert_called_with(["pipx", "install", "."])

    def test_bootstrap_fallback_venv(self):
        with mock.patch.object(task, "which", side_effect=[None, None]):
            with (
                mock.patch.object(task, "subprocess") as m_sub,
                mock.patch.object(task, "Path") as m_path,
                mock.patch.object(task, "sys") as m_sys,
            ):
                m_sub.call.return_value = 0
                # Simulate POSIX
                m_sys.platform = "darwin"
                # Fake home
                fake_home = Path.cwd() / ".tmp_home"
                fake_home.mkdir(exist_ok=True)
                m_path.home.return_value = fake_home
                rc = task.main(["bootstrap"])
                self.assertEqual(rc, 0)
                # First command should be python3 -m venv <dir>
                first_call = m_sub.call.call_args_list[0][0][0]
                self.assertEqual(first_call[:3], ["python3", "-m", "venv"])

        with mock.patch.object(task, "subprocess") as m_sub:
            rc = task.main(["--dry-run", "-v", "run", "--console"])
            self.assertEqual(rc, 0)
            m_sub.call.assert_not_called()

    def test_lint_with_ruff(self):
        with mock.patch.object(task, "which", return_value="/usr/bin/ruff"):
            with mock.patch.object(task, "subprocess") as m_sub:
                m_sub.call.return_value = 0
                rc = task.main(["-v", "lint"])
                self.assertEqual(rc, 0)
                m_sub.call.assert_called_with(["uv", "run", "ruff", "check", "."])

    def test_lint_with_flake8(self):
        with mock.patch.object(task, "which", side_effect=[None, "/usr/bin/flake8"]):
            with mock.patch.object(task, "subprocess") as m_sub:
                m_sub.call.return_value = 0
                rc = task.main(["-v", "lint"])
                self.assertEqual(rc, 0)
                m_sub.call.assert_called_with(["uv", "run", "flake8", "."])

    def test_lint_none_available(self):
        with mock.patch.object(task, "which", return_value=None):
            buf = io.StringIO()
            rc = None
            with mock.patch("sys.stdout", buf):
                rc = task.main(["lint"])  # prints message, succeeds
            self.assertEqual(rc, 0)
            self.assertIn("No linter found", buf.getvalue())

    def test_format_with_ruff(self):
        with mock.patch.object(task, "which", return_value="/usr/bin/ruff"):
            with mock.patch.object(task, "subprocess") as m_sub:
                m_sub.call.return_value = 0
                rc = task.main(["-v", "format"])
                self.assertEqual(rc, 0)
                m_sub.call.assert_called_with(["uv", "run", "ruff", "format", "."])

    def test_format_with_black(self):
        with mock.patch.object(task, "which", side_effect=[None, "/usr/bin/black"]):
            with mock.patch.object(task, "subprocess") as m_sub:
                m_sub.call.return_value = 0
                rc = task.main(["-v", "format"])
                self.assertEqual(rc, 0)
                m_sub.call.assert_called_with(["uv", "run", "black", "."])

    def test_format_none_available(self):
        with mock.patch.object(task, "which", return_value=None):
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                rc = task.main(["format"])  # prints message, succeeds
            self.assertEqual(rc, 0)
            self.assertIn("No formatter found", buf.getvalue())

    def test_clean_dry_run_outputs(self):
        # Create controlled targets in repo root
        build = Path("build")
        dist = Path("dist")
        cache = Path(".pytest_cache")
        for p in (build, dist, cache):
            p.mkdir(parents=True, exist_ok=True)
        try:
            buf = io.StringIO()
            with mock.patch("sys.stdout", buf):
                rc = task.main(["--dry-run", "-v", "clean"])
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn("rm -rf build", out)
            self.assertIn("rm -rf dist", out)
            self.assertIn("rm -rf .pytest_cache", out)
        finally:
            # Clean up created dirs (if they still exist)
            for p in (build, dist, cache):
                if p.exists():
                    shutil.rmtree(p, ignore_errors=True)
