# Roadmap

## Confirmed / In Progress

Features that are decided and currently under development or planned.

### Cross-platform Support
Implementing Windows and Linux platform support
- Platform detection and dispatch (#7)
- Windows paste implementation (#6) 
- OS-specific configuration defaults (#8)
- Documentation and setup guides (#5, #9)
- Packaging improvements (#10)
- Linux support (X11/Wayland paste, audio systems)
- **Status**: Active development (Windows priority, Linux following)

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

