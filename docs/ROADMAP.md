# Roadmap

## Recently Completed

Features that have been successfully implemented and released.

### Cross-platform Support (Windows) - Completed in v0.1.0-beta.1
Full Windows platform support implementation
- ✅ Platform detection and dispatch (#7) 
- ✅ Windows paste implementation (#6)
- ✅ OS-specific configuration defaults (#8)
- ✅ Documentation and setup guides (#5, #9)
- ✅ Packaging improvements (#10)
- **Status**: Released in v0.1.0-beta.1 (September 2025)

## Confirmed / In Progress

Features that are decided and currently under development or planned.

### Linux Platform Support
Implementing Linux platform support as next major milestone
- Linux paste implementation (X11/Wayland compatibility)
- Linux-specific audio system integration
- Package distribution (AppImage, Snap, deb)
- **Status**: Planning phase

---

## Ideas / Future Considerations

Features to consider for future development (priority and timeline TBD).

### Streaming & Real-time Features
- Partial results during capture; token-diff stabilization
- Smarter finalize timing (VAD, silence detection)
- Real-time transcription display

### Engine & Performance
- Pluggable backends (e.g., whisper.cpp, Azure Speech)
- Model warmup and caching controls  
- Latency/throughput metrics; optional telemetry (local-only)
- Graceful device reconnection and error handling

### Input & Interaction
- Custom hotkey combos (e.g., ctrl+space) with chord support
- App-specific profiles and advanced paste guard rules
- Voice commands ("new line", "period", "delete")
- Multi-language simultaneous recognition

### User Experience
- Menu bar helper (macOS) for quick status and controls
- GUI configuration interface
- Profile management (work/personal settings)
- Usage statistics and insights

### Distribution & Deployment
- Signed app bundle or Homebrew formula
- Windows installer (MSI)
- Linux packages (AppImage, Snap, deb)
- Auto-updater functionality

### Developer Experience
- Plugin/extension system
- API for external tool integration
- VS Code extension
- CLI scripting capabilities

