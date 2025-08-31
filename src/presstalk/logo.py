ANSI_RESET = "\x1b[0m"
ANSI_BOLD = "\x1b[1m"
ANSI_CYAN = "\x1b[36m"
ANSI_MAGENTA = "\x1b[35m"


def render_logo(color: bool = True) -> str:
    # Simple ASCII logo for "PressTalk"
    art = [
        r"  ____                 _____     _ _   ",
        r" |  _ \ _ __ ___  ___ |_   _|__ | | |__  ",
        r" | |_) | '__/ _ \/ __|  | |/ _ \| | '_ \ ",
        r" |  __/| | | (_) \__ \  | | (_) | | | | |",
        r" |_|   |_|  \___/|___/  |_|\___/|_|_| |_|",
    ]
    title = " PressTalk"
    if not color:
        return "\n".join(art + [title])
    # Apply simple two-tone gradient
    c1, c2 = ANSI_CYAN, ANSI_MAGENTA
    lines = []
    for i, ln in enumerate(art):
        c = c1 if i % 2 == 0 else c2
        lines.append(f"{c}{ANSI_BOLD}{ln}{ANSI_RESET}")
    lines.append(f"{ANSI_BOLD}{title}{ANSI_RESET}")
    return "\n".join(lines)


def print_logo(use_color: bool = True) -> None:
    try:
        print(render_logo(color=use_color))
    except Exception:
        pass

