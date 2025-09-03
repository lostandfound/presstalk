# ADR-001: Default Hotkey Change from Ctrl to Ctrl+Space

## Status
Accepted (Revised)

## Context

PressTalk currently uses a single `ctrl` key as the default global hotkey for Push-to-Talk functionality. This creates significant accessibility issues:

1. **Screen Reader Conflict**: NVDA and JAWS use `ctrl` alone to stop speech output, creating a direct functional conflict for visually impaired users
2. **WCAG 2.1 Violation**: Single modifier key shortcuts violate Success Criterion 2.1.4, which requires either disable/remap functionality or multi-key combinations to prevent accidental activation
3. **Accessibility Barrier**: Current configuration makes PressTalk unusable for screen reader users

## Decision

We will change the default hotkey from `ctrl` to `Ctrl+Space` for the following reasons:

### Requirements Framework (Revised)
1. **Accessibility (Non-negotiable)**: Zero conflicts with major screen readers
2. **Usability (Critical)**: Must not interfere with normal text input or system functions
3. **Cross-platform compatibility**: Must work on Windows/macOS/Linux
4. **Ergonomics**: Single-handed operation for Push-to-Talk usage

### Analysis Results (Revised)

| Candidate | OS Conflicts | App Conflicts | Text Input Issues | Usability | Final Score |
|-----------|--------------|---------------|-------------------|-----------|-------------|
| **Ctrl+Space** | Limited (macOS) | Limited (IDE) | None | Excellent | Best |
| Shift+Space | None | Minor | **Fatal** (continuous spaces) | **Unusable** | Rejected |
| Ctrl+Shift+Space | None | None | None | Good | Alternative |
| Alt+Space | High (Windows) | Medium | None | Poor | Rejected |

### Key Advantages of Ctrl+Space

- **Practical convention**: Simple, memorable two-key chord commonly used across apps
- **Optimal ergonomics**: Two-key combination with excellent single-handed operation
- **No text input interference**: Does not produce unwanted characters during hold operation
- **WCAG 2.1 compliant**: Multi-key combination prevents accidental activation
- **Screen reader safe**: No known critical conflicts with NVDA, JAWS, VoiceOver, Orca, or Windows Narrator
- **Practical usability**: 実環境での使用において許容範囲の競合に留まる（PTT用途では問題最小）

### Critical Issue Discovery

During practical testing, the initially selected `Shift+Space` was found to be **completely unusable** due to:
- **Continuous space insertion**: OS processes Shift+Space as repeated space characters during hold operations
- **Text corruption**: Normal typing becomes impossible while hotkey is active
- **Implementation oversight**: This practical issue was not identified in theoretical analysis

## Consequences

### Positive
- Eliminates accessibility barriers for screen reader users
- Achieves WCAG 2.1 Success Criterion 2.1.4 compliance
- **Resolves text input interference**: No unwanted character insertion during operation
- Maintains cross-platform consistency
- **Practical usability**: Works in real-world usage scenarios
- **Conflicts manageable**: Known OS/IDE conflicts have clear user-side mitigations

### Negative
- **Breaking change**: Existing users must adapt to new default
- **Limited platform conflicts**: macOS 入力ソース切替、IDE 補完と競合する可能性（回避策あり）
- Requires user migration and communication effort

### Implementation Requirements
- Update default configuration in `presstalk.yaml`
- Modify hotkey detection logic to support 2-key combinations
- Update ADR documentation to reflect industry analysis and practical considerations
- Implement migration path for existing users with clear communication
- Update all documentation and help materials

### Migration Strategy
- New users: Start with `Ctrl+Space` immediately  
- Existing users: Auto-migrate with one-time notification explaining the change
- Preserve customization options for users who prefer different combinations
- Provide clear explanation of accessibility improvements and industry alignment

## Alternatives Considered

1. **Shift+Space**: **Rejected due to fatal text input interference** (continuous space insertion)
2. **Ctrl+Shift+Space**: 誤起動耐性は高いが、ターミナル系で `^@` が連続入力される副作用があり不採用（デフォルトには不向き）
3. **Alt+Space**: Rejected due to Windows system menu conflict  
4. **Function keys**: Rejected due to inconsistent availability and poor ergonomics
5. **3-key combinations**: Considered but determined to be over-engineered for the use case

## References
- Screen reader hotkey analysis documentation
- WCAG 2.1 Success Criterion 2.1.4 guidelines  
- Cross-platform keyboard shortcut conflict research
- User ergonomics and accessibility requirements
- Detailed analysis: `docs/knowledge/report-hotkey.md`

## Date
2025-09-03 (Initial Decision)  
2025-09-03 (Revised after practical testing)
