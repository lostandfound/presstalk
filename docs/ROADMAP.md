# Roadmap

## Recently Completed

Features that have been successfully implemented and released.

### Performance and User Experience Improvements - Completed in v0.1.2
Startup optimization and version management enhancements
- ✅ Startup model preloading: Eliminated 30s-2min delay on first voice recognition (#46)
- ✅ Progress display during model loading for better user feedback
- ✅ Dynamic version display in application logo
- ✅ Version consistency improvements using importlib.metadata
- ✅ Enhanced user experience with immediate readiness after startup
- **Status**: Released in v0.1.2 (September 2025)

### Cross-platform Support (Complete) - Completed in v0.1.0
Full cross-platform support for macOS, Windows, and Linux
- ✅ Platform detection and dispatch (#7)
- ✅ Windows paste implementation (#6)
- ✅ Linux paste implementation (#20-25)
- ✅ OS-specific configuration defaults (#8)
- ✅ X11 and Wayland compatibility (Linux)
- ✅ Documentation and setup guides (#5, #9)
- ✅ Comprehensive testing suite
- ✅ Packaging improvements (#10)
- **Status**: Released in v0.1.0 (September 2025)

## Confirmed / In Progress

Features that are decided and currently under development or planned.

### Accessibility Improvements - Priority for Next Release
Critical accessibility enhancements to support users with disabilities
- 🔥 **Screen reader compatibility**: Address hotkey conflicts with NVDA/JAWS (#43)
- 🔥 **WCAG 2.1 compliance**: Resolve Success Criterion 2.1.4 violations
- ⏳ **Interactive configuration system**: Accessible setup and hotkey customization
- ⏳ **Audio feedback system**: 
  - System beep integration (cross-platform, no external files required)
  - Recording start/stop audio cues (default: enabled, user configurable)
  - Voice announcements for recording status and transcription results
- ⏳ **Visual indicator improvements**: High contrast mode and system tray support
- **Priority**: High (Phase 0 emergency response needed)
- **Target**: Next minor release (v0.1.3)

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
- **Enhanced configuration interfaces**:
  - Interactive CLI configuration (`presstalk config`) - TUI with step-by-step guidance
  - Web-based configuration server (`presstalk config --web`) - WCAG 2.1 compliant browser interface
  - Real-time conflict detection and NVDA/JAWS compatibility warnings
  - Accessible hotkey testing and validation
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

