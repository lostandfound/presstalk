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
            r" ____                   _____     _ _    ",
            r"|  _ \ _ __ ___  ___ __|_   _|_ _| | | __",
            r"| |_) | '__/ _ \/ __/ __|| |/ _` | | |/ /",
            r"|  __/| | |  __/\__ \__ \| | (_| | |   < ",
            r"|_|   |_|  \___||___/___/|_|\__,_|_|_|\_\\",
        ]
        if not color:
            # ASCII art + single plain wordmark
            word = "PressTalk"
            underline = "=" * len(word)
            return "\n".join(art + [word, underline])
        c1, c2 = ANSI_CYAN, ANSI_MAGENTA
        lines = []
        for i, ln in enumerate(art):
            c = c1 if i % 2 == 0 else c2
            lines.append(f"{c}{ANSI_BOLD}{ln}{ANSI_RESET}")
        # Add a clear wordmark under the ASCII art for readability (single occurrence)
        word = "PressTalk"
        underline = "=" * len(word)
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
