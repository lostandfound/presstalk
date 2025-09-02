# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2025-09-02

### Added
- Startup model preloading with progress display: Eliminates 30s-2min delay on first voice recognition by loading ASR models during initialization
- Version number display in application logo for better user experience
- Progress feedback during model loading ("Loading ASR model... Ready!")

### Fixed
- Version consistency issues through dynamic version retrieval from pyproject.toml using importlib.metadata
- Improved user experience with immediate readiness after startup

### Technical Implementation
- Enhanced FasterWhisperBackend to preload models during __init__ instead of lazy loading
- Added show_progress parameter for user feedback during model initialization
- Updated logo rendering to dynamically display version information
- Comprehensive test coverage for preloading functionality

## [0.1.1] - 2025-08-31

### Changed
- Refactored internal code structure for better maintainability and readability
- Reduced duplication by centralizing paste guard logic across platforms
- Split large CLI `main()` into smaller, testable helpers
- Simplified configuration initialization into focused helper methods
- Consolidated environment boolean parsing into shared constants and utility

### Notes
- No user-facing changes; behavior and CLI remain compatible
- All existing tests pass; simulation and paste flows unchanged

## [0.1.0] - 2025-08-31

### Added
- **Complete Linux support**: Full platform compatibility alongside macOS and Windows
- Linux-specific paste implementation with X11 and Wayland compatibility
  - Clipboard management: wl-copy (Wayland) → xclip → xsel priority
  - Keystroke injection: pynput → xdotool fallback
  - Frontmost app detection for paste guard (X11: xdotool+xprop, Wayland: swaymsg)
- Linux-specific paste guard defaults for common terminals
  - gnome-terminal, org.gnome.Terminal, konsole, xterm, alacritty, kitty, wezterm, terminator, tilix, xfce4-terminal, lxterminal, io.elementary.terminal
- **Cross-platform task runner** (`task.py`): Python-based replacement for Makefile
  - Windows/macOS/Linux compatible workflow commands
  - Tasks: clean, install, test, simulate, run, lint, format
  - Bootstrap and install-global capabilities
  - Comprehensive test coverage for task runner
- Comprehensive Linux testing suite
- Linux setup documentation and platform-specific guidance

### Changed
- **Stable release**: Promoted from beta to stable after successful cross-platform validation
- Enhanced platform abstraction layer for three-platform support
- Documentation updated to reflect complete cross-platform capabilities
- Makefile simplified to delegate core tasks to task.py (maintains Unix compatibility)

### Technical Implementation
- Added `src/presstalk/paste_linux.py` with comprehensive Linux implementation
- Enhanced platform dispatcher for Linux detection (`sys.platform.startswith('linux')`)
- Extended `src/presstalk/config.py` with Linux-specific defaults
- Added Linux-specific test coverage (`tests/test_paste_linux.py`)
- Added `task.py` cross-platform task runner with comprehensive test suite (`tests/test_task.py`)
- Updated package classifiers for Linux support
- Updated README and documentation to prioritize task.py over Makefile

### Notes
- **Major Milestone**: Complete cross-platform support for macOS, Windows, and Linux
- All platform-specific implementations maintain consistent API
- Comprehensive testing and documentation across all platforms
- Production-ready for all major desktop operating systems

## [0.1.0-beta.1] - 2025-09-01

### Added
- **Cross-platform support**: Windows 10/11 compatibility alongside macOS
- Windows-specific paste implementation using `clip.exe` and `Ctrl+V`
- Platform-specific paste guard configurations
  - macOS: Terminal, iTerm2, com.apple.Terminal, com.googlecode.iterm2
  - Windows: cmd.exe, powershell.exe, pwsh.exe, WindowsTerminal.exe, wt.exe, conhost.exe
- Unified cross-platform API with automatic platform detection
- Windows-specific documentation in usage guides
- Platform classifier for Windows in packaging metadata

### Changed
- Restructured paste functionality with platform abstraction layer
- Configuration defaults now adapt to operating system
- Documentation updated to reflect cross-platform capabilities

### Technical Implementation
- Added `src/presstalk/paste.py` for platform dispatch
- Added `src/presstalk/paste_windows.py` for Windows implementation
- Enhanced `src/presstalk/config.py` with OS-specific defaults
- Updated architecture documentation for platform support

### Notes
- This is a beta release for Windows platform testing
- All existing macOS functionality remains unchanged
- Windows implementation uses native Windows APIs and tools

## [0.0.1] - 2025-08-31

### Added
- Initial release with macOS support
- Push-to-talk voice input using local ASR (faster-whisper)
- Global hotkey support (default: ctrl)
- Console input mode as alternative to global hotkey
- Configurable paste guard to prevent accidental paste in terminals
- YAML-based configuration with auto-discovery
- Prebuffer for smooth audio capture
- Support for multiple Whisper model sizes
- Japanese and English language support
- Simulation mode for testing without audio devices
- Comprehensive test suite
- Documentation for usage and architecture

### Known Issues
- macOS only (Windows support planned for v0.0.3)
- Requires Microphone and Accessibility permissions on first run

[Unreleased]: https://github.com/lostandfound/presstalk/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/lostandfound/presstalk/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/lostandfound/presstalk/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/lostandfound/presstalk/compare/v0.1.0-beta.1...v0.1.0
[0.1.0-beta.1]: https://github.com/lostandfound/presstalk/compare/v0.0.1...v0.1.0-beta.1
[0.0.1]: https://github.com/lostandfound/presstalk/releases/tag/v0.0.1
