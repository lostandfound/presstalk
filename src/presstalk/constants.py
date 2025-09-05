from typing import Optional, Tuple

# Canonical falsy string representations used for env toggles
FALSY_VALUES: Tuple[str, ...] = ("0", "false")

# Supported Faster-Whisper model choices (used by CLI and Web UI)
MODEL_CHOICES: Tuple[str, ...] = ("tiny", "base", "small", "medium", "large")

# Representative language choices for UI menus (server accepts free-form)
LANG_CHOICES: Tuple[str, ...] = (
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
)


def is_env_enabled(env_var: Optional[str], default: bool = True) -> bool:
    """Return True if the env_var indicates an enabled flag.

    - None returns the provided default
    - Comparison is case-insensitive; leading/trailing spaces ignored
    - Values considered falsy: "0", "false"
    """
    if env_var is None:
        return default
    val = env_var.strip().lower()
    return val not in FALSY_VALUES
