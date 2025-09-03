import os
from typing import Dict, Optional, Sequence, Union, List
from .constants import is_env_enabled


class PasteGuard:
    @staticmethod
    def _normalize_blocklist(
        blocklist: Optional[Union[str, Sequence[str]]],
    ) -> List[str]:
        if blocklist is None:
            return []
        if isinstance(blocklist, str):
            items = [s.strip() for s in blocklist.split(",")]
        else:
            items = [str(s).strip() for s in blocklist]
        return [s.lower() for s in items if s]

    @staticmethod
    def _effective_guard(guard_enabled: Optional[bool]) -> bool:
        if guard_enabled is not None:
            return bool(guard_enabled)
        env = os.getenv("PT_PASTE_GUARD")
        return is_env_enabled(env, default=True)

    @staticmethod
    def _effective_blocklist(
        blocklist: Optional[Union[str, Sequence[str]]], default_blocklist: str
    ) -> List[str]:
        if blocklist is not None:
            return PasteGuard._normalize_blocklist(blocklist)
        env = os.getenv("PT_PASTE_BLOCKLIST")
        if env is not None:
            return PasteGuard._normalize_blocklist(env)
        return PasteGuard._normalize_blocklist(default_blocklist)

    @staticmethod
    def should_block(
        fg_info: Dict[str, str],
        guard_enabled: Optional[bool] = None,
        blocklist: Optional[Union[str, Sequence[str]]] = None,
        default_blocklist: str = "",
    ) -> bool:
        """Return True when paste should be blocked based on foreground app info.

        - guard_enabled: explicit on/off overrides ENV; if None, PT_PASTE_GUARD used; default True
        - blocklist: explicit list or comma-separated string; else PT_PASTE_BLOCKLIST; else default_blocklist
        - fg_info: foreground metadata (e.g., name, bundle_id); all string values are considered
        """
        if not fg_info:
            return False
        if not PasteGuard._effective_guard(guard_enabled):
            return False
        blocks = PasteGuard._effective_blocklist(blocklist, default_blocklist)
        if not blocks:
            return False
        targets = [str(v).lower() for v in fg_info.values() if isinstance(v, str) and v]
        if not targets:
            return False
        for b in blocks:
            if not b:
                continue
            for t in targets:
                if b in t:
                    return True
        return False
