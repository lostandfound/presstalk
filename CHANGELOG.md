# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/lostandfound/presstalk/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/lostandfound/presstalk/releases/tag/v0.0.1