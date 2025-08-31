# Versioning and Release Guidelines

This document describes the versioning strategy and release process for PressTalk.

## Version Numbering

We follow [Semantic Versioning 2.0.0](https://semver.org/) with the format: `MAJOR.MINOR.PATCH`

### Pre-1.0 Development Phase (Current)

During the `0.x.x` phase:
- The public API is considered unstable
- Breaking changes may occur in any release
- Version increments communicate the scale of changes:
  - `0.0.x` → Small fixes, experimental features
  - `0.x.0` → Significant features or architectural changes

### Post-1.0 Stable Phase

Once we reach `1.0.0`:
- `MAJOR`: Incremented for breaking API changes
- `MINOR`: Incremented for backwards-compatible feature additions
- `PATCH`: Incremented for backwards-compatible bug fixes

### Pre-release Versions

For testing releases before official versions:
```
0.1.0-beta.1   # First beta of 0.1.0
0.1.0-rc.1     # Release candidate
1.0.0-alpha.1  # Alpha testing phase
```

## Version Sources

Version information must be updated in these locations:

1. `pyproject.toml` - Primary version source
2. `src/presstalk/cli.py` - CLI version display (to be refactored)

Future improvement: Implement single source of truth using `__version__` in `src/presstalk/__init__.py`

## Release Process

### 1. Prepare Release

```bash
# Ensure all tests pass
make test

# Update version in pyproject.toml and cli.py
# Example: 0.0.2 → 0.0.3

# Update CHANGELOG.md (create if not exists)
# Follow Keep a Changelog format
```

### 2. Create Release Commit

```bash
git add pyproject.toml src/presstalk/cli.py CHANGELOG.md
git commit -m "Release v0.0.3"
```

### 3. Tag the Release

```bash
# Annotated tag with version
git tag -a v0.0.3 -m "Release version 0.0.3"

# Push commits and tags
git push origin main
git push origin v0.0.3
```

### 4. Create GitHub Release

```bash
# Using GitHub CLI
gh release create v0.0.3 \
  --title "v0.0.3" \
  --notes-file CHANGELOG.md \
  --target main
```

## Release Checklist

Before each release:

- [ ] All tests pass (`make test`)
- [ ] Documentation is up to date
- [ ] CHANGELOG.md reflects all changes
- [ ] Version numbers are updated consistently
- [ ] Branch is clean (no uncommitted changes)
- [ ] Previous version works as expected (regression check)

## Version Planning

### Current Roadmap

```
0.0.1 (Released) - Initial macOS-only version
0.0.2            - Bug fixes and minor improvements
0.0.3            - Windows support (planned)
0.1.0            - First stable beta with cross-platform support
0.2.0            - Linux support
0.3.0            - Enhanced configuration system
1.0.0            - API stability guaranteed
```

### Milestone Guidelines

- Create GitHub milestones for minor versions (0.1.0, 0.2.0)
- Associate issues with appropriate milestones
- Close milestones only after release is tagged

## Changelog Format

Follow [Keep a Changelog](https://keepachangelog.com/) principles:

```markdown
# Changelog

## [Unreleased]
### Added
- New features not yet released

## [0.0.3] - 2025-09-01
### Added
- Windows platform support
- Platform-specific paste implementations

### Fixed
- Hotkey detection on non-US keyboards

### Changed
- Improved error messages for missing permissions
```

## Deprecation Policy

Pre-1.0:
- No deprecation warnings required
- Document breaking changes in CHANGELOG

Post-1.0:
- Deprecate features at least one minor version before removal
- Use deprecation warnings in code
- Document deprecation timeline in CHANGELOG

## Distribution

### PyPI Publishing (Future)

Once ready for public distribution:

```bash
# Build distribution packages
make build

# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# After verification, upload to PyPI
make publish
```

### Platform-specific Packages (Future)

- Homebrew formula for macOS
- MSI installer for Windows
- AppImage/Snap for Linux

## Version Compatibility Matrix

Document tested combinations:

| PressTalk | Python | macOS | Windows | Linux |
|-----------|--------|-------|---------|-------|
| 0.0.1     | 3.9+   | 13+   | -       | -     |
| 0.0.3     | 3.9+   | 13+   | 10+     | -     |
| 0.1.0     | 3.9+   | 13+   | 10+     | TBD   |

## Automated Versioning (Future)

Consider implementing:
- `bump2version` or `poetry-dynamic-versioning`
- GitHub Actions for automated releases
- Version extraction from git tags
- Automatic CHANGELOG generation from commit messages

## Questions and Support

For questions about versioning or releases:
- Open a GitHub issue with the `type/chore` label
- Discuss in project meetings before major version changes