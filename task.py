#!/usr/bin/env python3
"""
Cross-platform task runner for PressTalk.

Usage:
  uv run python task.py <task> [options]

Tasks:
  - clean:     Remove build/ dist/ .pytest_cache and all **/__pycache__
  - install:   uv pip install -e .
  - test:      uv run python -m unittest -v [--file PATH]
  - simulate:  uv run presstalk simulate [--chunks ... --delay-ms INT]
  - run:       uv run presstalk run [--console]
  - lint:      Try ruff or flake8 (if available); otherwise no-op message
  - format:    Try ruff format or black (if available); otherwise no-op message

Common flags:
  --dry-run / -n   Show actions without executing
  --verbose / -v   Print commands and details

This script avoids shell-specific syntax to work on Windows/macOS/Linux.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Sequence, Optional


ROOT = Path(__file__).resolve().parent


class TaskError(RuntimeError):
    pass


def run_cmd(cmd: Sequence[str], *, dry_run: bool = False, verbose: bool = False) -> int:
    if verbose or dry_run:
        print("$", " ".join(cmd))
    if dry_run:
        return 0
    try:
        return subprocess.call(list(cmd))
    except FileNotFoundError as e:
        raise TaskError(f"Command not found: {cmd[0]}") from e


def which(prog: str) -> Optional[str]:
    return shutil.which(prog)


def task_clean(dry_run: bool, verbose: bool) -> None:
    targets: List[Path] = []
    # Fixed targets
    for name in ("build", "dist", ".pytest_cache"):
        p = ROOT / name
        if p.exists():
            targets.append(p)
    # Recursively collect __pycache__
    targets.extend(Path(ROOT).rglob("__pycache__"))

    if not targets and verbose:
        print("Nothing to clean.")

    for p in targets:
        if p.is_dir():
            if verbose or dry_run:
                print(f"rm -rf {p.relative_to(ROOT)}")
            if not dry_run:
                shutil.rmtree(p, ignore_errors=True)
        else:
            if verbose or dry_run:
                print(f"rm -f {p.relative_to(ROOT)}")
            if not dry_run:
                try:
                    p.unlink()
                except FileNotFoundError:
                    pass


def task_install(dry_run: bool, verbose: bool) -> None:
    code = run_cmd(["uv", "pip", "install", "-e", "."], dry_run=dry_run, verbose=verbose)
    if code != 0:
        raise TaskError(f"install failed with exit code {code}")


def task_test(file: Optional[str], dry_run: bool, verbose: bool) -> None:
    # Use discovery by default to match repo guidelines
    if file:
        args = ["uv", "run", "python", "-m", "unittest", file, "-v"]
    else:
        args = [
            "uv",
            "run",
            "python",
            "-m",
            "unittest",
            "discover",
            "-v",
            "-s",
            "tests",
            "-p",
            "test_*.py",
        ]
    code = run_cmd(args, dry_run=dry_run, verbose=verbose)
    if code != 0:
        raise TaskError(f"tests failed with exit code {code}")


def task_simulate(chunks: Optional[Iterable[str]], delay_ms: Optional[int], dry_run: bool, verbose: bool) -> None:
    args: List[str] = ["uv", "run", "presstalk", "simulate"]
    if chunks:
        args.append("--chunks")
        args.extend(list(chunks))
    if delay_ms is not None:
        args.extend(["--delay-ms", str(delay_ms)])
    code = run_cmd(args, dry_run=dry_run, verbose=verbose)
    if code != 0:
        raise TaskError(f"simulate failed with exit code {code}")


def task_run(console: bool, dry_run: bool, verbose: bool) -> None:
    args: List[str] = ["uv", "run", "presstalk", "run"]
    if console:
        args.append("--console")
    code = run_cmd(args, dry_run=dry_run, verbose=verbose)
    if code != 0:
        raise TaskError(f"run failed with exit code {code}")


def task_lint(dry_run: bool, verbose: bool) -> None:
    # Prefer ruff, fallback to flake8; otherwise no-op message
    if which("ruff"):
        code = run_cmd(["uv", "run", "ruff", "check", "."], dry_run=dry_run, verbose=verbose)
        if code != 0:
            raise TaskError("lint failed")
        return
    if which("flake8"):
        code = run_cmd(["uv", "run", "flake8", "."], dry_run=dry_run, verbose=verbose)
        if code != 0:
            raise TaskError("lint failed")
        return
    print("No linter found (install ruff or flake8). Skipping.")


def task_format(dry_run: bool, verbose: bool) -> None:
    # Prefer ruff format, fallback to black; otherwise no-op message
    if which("ruff"):
        code = run_cmd(["uv", "run", "ruff", "format", "."], dry_run=dry_run, verbose=verbose)
        if code != 0:
            raise TaskError("format failed")
        return
    if which("black"):
        code = run_cmd(["uv", "run", "black", "."], dry_run=dry_run, verbose=verbose)
        if code != 0:
            raise TaskError("format failed")
        return
    print("No formatter found (install ruff or black). Skipping.")


def task_install_global(dry_run: bool, verbose: bool) -> None:
    if not which("uv"):
        raise TaskError("'uv' not found; install uv or use 'bootstrap' (will try pipx/venv)")
    code = run_cmd(["uv", "tool", "install", "--editable", "."], dry_run=dry_run, verbose=verbose)
    if code != 0:
        raise TaskError("install-global failed")
    print("Installed as a user tool. Ensure ~/.local/bin (or equivalent) is in PATH.")


def task_bootstrap(dry_run: bool, verbose: bool) -> None:
    # 1) Prefer uv tool install (global shim)
    if which("uv"):
        code = run_cmd(["uv", "tool", "install", "--editable", "."], dry_run=dry_run, verbose=verbose)
        if code != 0:
            raise TaskError("bootstrap: uv tool install failed")
        print("[ok] presstalk installed globally via uv. If not found, add ~/.local/bin to PATH.")
        return
    # 2) Fallback to pipx if available
    if which("pipx"):
        code = run_cmd(["pipx", "install", "."], dry_run=dry_run, verbose=verbose)
        if code != 0:
            raise TaskError("bootstrap: pipx install failed")
        print("[ok] presstalk installed globally via pipx. Run 'pipx ensurepath' if needed.")
        return
    # 3) Final fallback: create venv under ~/.venvs/presstalk and print usage
    home = Path.home()
    venv_dir = home / ".venvs" / "presstalk"
    py = "python" if sys.platform == "win32" else "python3"
    cmds = [
        [py, "-m", "venv", str(venv_dir)],
        [str(venv_dir / ("Scripts" if sys.platform == "win32" else "bin") / py), "-m", "pip", "install", "-U", "pip"],
        [str(venv_dir / ("Scripts" if sys.platform == "win32" else "bin") / py), "-m", "pip", "install", "-e", "."],
    ]
    for c in cmds:
        code = run_cmd(c, dry_run=dry_run, verbose=verbose)
        if code != 0:
            raise TaskError("bootstrap: venv setup failed")
    exe = venv_dir / ("Scripts" if sys.platform == "win32" else "bin") / "presstalk"
    print(f"[ok] venv ready at {venv_dir}")
    if sys.platform == "win32":
        print(f"Run: {exe} run")
    else:
        print(f"Add alias, e.g.: echo \"alias pt='{exe} run'\" >> ~/.zshrc && source ~/.zshrc")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="task.py", description="Cross-platform tasks for PressTalk")
    p.add_argument("--dry-run", "-n", action="store_true", help="Show actions without executing")
    p.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    sp = p.add_subparsers(dest="task", required=True)

    sp_clean = sp.add_parser("clean", help="Remove build artifacts and caches")

    sp_install = sp.add_parser("install", help="Editable install via uv")

    sp_test = sp.add_parser("test", help="Run unit tests")
    sp_test.add_argument("--file", help="Run a specific test file (e.g., tests/test_controller.py)")

    sp_sim = sp.add_parser("simulate", help="Run simulated capture")
    sp_sim.add_argument("--chunks", nargs="+", help="Text chunks to simulate (space-separated)")
    sp_sim.add_argument("--delay-ms", type=int, default=None, help="Inter-chunk delay in ms")

    sp_run = sp.add_parser("run", help="Run PressTalk locally")
    sp_run.add_argument("--console", action="store_true", help="Use console mode instead of global hotkey")

    sp.add_parser("lint", help="Run linter if available (ruff/flake8)")
    sp.add_parser("format", help="Run formatter if available (ruff/black)")

    sp.add_parser("install-global", help="Install globally via uv tool (shim)")
    sp.add_parser("bootstrap", help="One-shot setup: uv tool install or pipx, fallback to venv")

    sp.add_parser("help", help="Show this help")

    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    dry = bool(args.dry_run)
    verbose = bool(args.verbose)

    try:
        if args.task == "clean":
            task_clean(dry, verbose)
        elif args.task == "install":
            task_install(dry, verbose)
        elif args.task == "test":
            task_test(getattr(args, "file", None), dry, verbose)
        elif args.task == "simulate":
            task_simulate(getattr(args, "chunks", None), getattr(args, "delay_ms", None), dry, verbose)
        elif args.task == "run":
            task_run(getattr(args, "console", False), dry, verbose)
        elif args.task == "lint":
            task_lint(dry, verbose)
        elif args.task == "format":
            task_format(dry, verbose)
        elif args.task == "install-global":
            task_install_global(dry, verbose)
        elif args.task == "bootstrap":
            task_bootstrap(dry, verbose)
        elif args.task == "help":
            parser.print_help()
        else:
            parser.error(f"Unknown task: {args.task}")
        return 0
    except TaskError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
