import sys

if sys.platform == "darwin":
    from .paste_macos import insert_text  # noqa: F401
elif sys.platform == "win32":
    from .paste_windows import insert_text  # noqa: F401
elif sys.platform.startswith("linux"):
    from .paste_linux import insert_text  # noqa: F401
else:
    # Fallback: import macOS variant; callers can supply stubs in tests
    from .paste_macos import insert_text  # type: ignore # noqa: F401
