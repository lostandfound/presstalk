# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Windows platform support (in progress)
- LICENSE file with MIT License
- Single source of truth for version number (`__version__`)
- CHANGELOG.md for tracking releases
- Versioning guidelines in docs/dev/VERSIONING.md

### Changed
- Version is now imported from `__init__.py` instead of hardcoded in CLI

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