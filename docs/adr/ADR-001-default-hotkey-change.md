# ADR-001: Default Hotkey Change from Ctrl to Ctrl+Shift+Space

## Status
Accepted (Revised)

## Context

PressTalk currently uses a single `ctrl` key as the default global hotkey for Push-to-Talk functionality. This creates significant accessibility issues:

1. **Screen Reader Conflict**: NVDA and JAWS use `ctrl` alone to stop speech output, creating a direct functional conflict for visually impaired users
2. **WCAG 2.1 Violation**: Single modifier key shortcuts violate Success Criterion 2.1.4, which requires either disable/remap functionality or multi-key combinations to prevent accidental activation
3. **Accessibility Barrier**: Current configuration makes PressTalk unusable for screen reader users

## Decision

We will change the default hotkey from `ctrl` to `Ctrl+Shift+Space` for the following reasons:

### Requirements Framework
1. **Accessibility (Non-negotiable)**: Zero conflicts with major screen readers
2. **2-key limitation**: User requirement for maximum simplicity
3. **Cross-platform compatibility**: Must work on Windows/macOS/Linux
4. **Ergonomics**: Single-handed operation for Push-to-Talk usage

### Analysis Results

| Candidate | OS Conflicts | App Conflicts | Ergonomics | Risk Score |
|-----------|--------------|---------------|------------|------------|
| **Shift+Space** | None | Minor (acceptable) | Excellent | 6 (best) |
| Ctrl+Space | High (macOS input switching) | High (IDE autocomplete) | Good | 13 |
| Alt+Space | High (Windows menu) | Medium | Good | 11 |

### Key Advantages of Shift+Space

- **Zero OS-level conflicts**: No competition with core operating system functions
- **Minimal application conflicts**: Limited to non-critical functions (e.g., Firefox scroll)
- **Optimal ergonomics**: Natural left-hand operation (pinky + thumb)
- **WCAG 2.1 compliant**: Modifier key + space key combination prevents accidental activation
- **Screen reader safe**: No conflicts with NVDA, JAWS, VoiceOver, Orca, or Windows Narrator

## Consequences

### Positive
- Eliminates accessibility barriers for screen reader users
- Achieves WCAG 2.1 Success Criterion 2.1.4 compliance
- Provides superior ergonomics for Push-to-Talk operation
- Maintains cross-platform consistency
- Resolves the most critical user-blocking issue

### Negative
- **Breaking change**: Existing users must adapt to new default
- Minor application conflicts in specific contexts (Firefox page scroll)
- Requires user migration and communication effort

### Implementation Requirements
- Update default configuration in `presstalk.yaml`
- Modify hotkey detection logic to support key combinations
- Implement migration path for existing users with clear communication
- Update all documentation and help materials

### Migration Strategy
- New users: Start with `Shift+Space` immediately  
- Existing users: Auto-migrate with one-time notification explaining the change
- Preserve customization options for users who prefer different combinations
- Provide clear explanation of accessibility improvements

## Alternatives Considered

1. **Ctrl+Space**: Rejected due to high conflicts (macOS input switching, IDE autocomplete)
2. **Alt+Space**: Rejected due to Windows system menu conflict
3. **3-key combinations**: Rejected per user requirement for simplicity
4. **Function keys**: Rejected due to inconsistent availability across keyboards

## References
- Screen reader hotkey analysis documentation
- WCAG 2.1 Success Criterion 2.1.4 guidelines  
- Cross-platform keyboard shortcut conflict research
- User ergonomics and accessibility requirements
- Detailed analysis: `docs/knowledge/report-hotkey.md`

## Date
2025-09-03