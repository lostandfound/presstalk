ANSI_RESET = "\x1b[0m"
ANSI_BOLD = "\x1b[1m"
ANSI_CYAN = "\x1b[36m"
ANSI_MAGENTA = "\x1b[35m"
ANSI_WHITE = "\x1b[37m"


def render_logo(color: bool = True, style: str = "simple") -> str:
    """Render the PressTalk logo.
    style: 'simple' (clear text) or 'standard' (ASCII art)
    """
    if style == "standard":
        # Clearer figlet-style ASCII for "PressTalk"
        art = [
            r"  ____                 _____         _ _    ",
            r" |  _ \ _ __ ___  ___ |_   _|__  ___| | | __",
            r" | |_) | '__/ _ \/ _ \  | |/ _ \/ __| | |/ /",
            r" |  __/| | |  __/  __/  | |  __/\__ \ |   < ",
            r" |_|   |_|  \___|\___|  |_|\___||___/_|_|\_\",
        ]
        title = "   PressTalk"
        if not color:
            return "\n".join(art + [title])
        c1, c2 = ANSI_CYAN, ANSI_MAGENTA
        lines = []
        for i, ln in enumerate(art):
            c = c1 if i % 2 == 0 else c2
            lines.append(f"{c}{ANSI_BOLD}{ln}{ANSI_RESET}")
        # Add a clear wordmark under the ASCII art for readability
        word = "PressTalk"
        underline = "=" * len(word)
        lines.append(f"{ANSI_BOLD}{title}{ANSI_RESET}")
        lines.append(f"{ANSI_BOLD}{ANSI_MAGENTA}{word}{ANSI_RESET}")
        lines.append(f"{ANSI_WHITE}{underline}{ANSI_RESET}")
        return "\n".join(lines)

    # simple style (default): clear, unambiguous wordmark
    word = "PressTalk"
    underline = "=" * len(word)
    if not color:
        return f"{word}\n{underline}"
    return f"{ANSI_BOLD}{ANSI_MAGENTA}{word}{ANSI_RESET}\n{ANSI_WHITE}{underline}{ANSI_RESET}"


def print_logo(use_color: bool = True, style: str = "simple") -> None:
    try:
        # Print logo followed by a blank line for spacing
        print(render_logo(color=use_color, style=style))
        print()
    except Exception:
        pass
