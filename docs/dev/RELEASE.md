# Release Process Documentation

This document provides the essential steps for releasing PressTalk versions consistently and reliably.

## Overview

### Release Types
- **Patch** (0.1.0 → 0.1.1): Bug fixes, documentation updates
- **Minor** (0.1.0 → 0.2.0): New features, platform support
- **Major** (0.1.0 → 1.0.0): Breaking changes, API stability

## Pre-release Checklist

### Code Quality
- [ ] All tests pass: `uv run python -m unittest -v`
- [ ] CLI simulation works: `uv run presstalk simulate --chunks hello world --delay-ms 40`
- [ ] No critical bugs for target version
- [ ] Manual testing on primary platforms

### Code Review
- [ ] All PRs merged to `develop` branch
- [ ] No uncommitted changes in working directory
- [ ] `develop` branch is up-to-date

## Documentation Updates

### 1. CHANGELOG.md Updates

**Process**:
1. Add new version entry at the top:
   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD
   
   ### Added
   - New features
   
   ### Fixed
   - Bug fixes
   
   ### Changed
   - Breaking changes (if any)
   ```

2. **Validation**:
   - [ ] Version number matches `pyproject.toml`
   - [ ] Date is current release date
   - [ ] All significant PRs documented

### 2. ROADMAP.md Updates

**Process**:
1. Move completed features from "Planned" to "Recently Completed"
2. Update status of in-progress features
3. **Validation**:
   - [ ] Completed features moved appropriately
   - [ ] Version numbers updated for completed items

## Version Management

**Single Source**: `pyproject.toml` only (automatic sync via `importlib.metadata`)

### Process
1. Update version in `pyproject.toml`:
   ```toml
   [project]
   version = "X.Y.Z"
   ```

2. **Validation**:
   ```bash
   uv run presstalk --version
   # Should output: presstalk X.Y.Z
   ```

### Checklist
- [ ] `pyproject.toml` version updated
- [ ] CLI `--version` displays correct version
- [ ] CHANGELOG.md version entry matches

## Branch Workflow

### Standard Release
```bash
# 1. Create release branch
git checkout develop
git pull origin develop
git checkout -b release/vX.Y.Z

# 2. Update version and documentation
# Edit pyproject.toml, CHANGELOG.md, ROADMAP.md

# 3. Commit changes
git add .
git commit -m "Prepare release vX.Y.Z"

# 4. Create PR: release/vX.Y.Z → main
```

### Hotfix (Critical patches)
```bash
# 1. Create from main
git checkout main
git checkout -b hotfix/vX.Y.Z

# 2. Apply fix, update version, test
# 3. PR to main
# 4. Cherry-pick to develop after merge
```

## Testing Requirements

### Automated Tests
```bash
# Unit tests
uv run python -m unittest discover tests -v

# CLI functionality  
uv run presstalk --help
uv run presstalk --version
uv run presstalk simulate --chunks hello world --delay-ms 40
```

### Manual Testing
- [ ] PTT recording works: `uv run presstalk --console`
- [ ] Audio capture starts/stops correctly
- [ ] Text transcription accuracy acceptable
- [ ] Platform-specific functionality (macOS hotkey, paste guard)

## GitHub Release Creation

### Process
```bash
# 1. Tag release
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin vX.Y.Z

# 2. Create GitHub release
gh release create vX.Y.Z \
  --title "PressTalk vX.Y.Z" \
  --notes-file CHANGELOG.md \
  --target main
```

### Release Notes Template
```markdown
## PressTalk vX.Y.Z

### New Features
- Feature descriptions with issue links

### Bug Fixes  
- Fix descriptions (#issue-number)

### Installation
`uv run presstalk` or see installation guide
```

## Post-release Verification

### Within 1 Hour
- [ ] GitHub release published
- [ ] CLI version displays correctly
- [ ] Installation instructions accurate

## Rollback Procedures

### When to Rollback
- Critical security vulnerability
- Widespread installation failures  
- Severe functionality regressions

### Process
1. **Immediate**: Hide GitHub release (mark as draft)
2. **Communication**: Create issue explaining the situation
3. **Technical**: Create hotfix release reverting problematic changes
4. **Documentation**: Update CHANGELOG.md with rollback entry

## Troubleshooting

### Version Mismatch
**Issue**: CLI shows wrong version  
**Solution**: Verify `pyproject.toml`, reinstall with `uv pip install -e .`

### Test Failures  
**Issue**: Tests fail in release branch  
**Solution**: Check dependencies, platform-specific code, Python version

### Git Issues
**Issue**: Merge conflicts during release  
**Solution**: Sync `develop` and `main`, resolve conflicts carefully

## Related Documentation

- [GitHub Workflow](GITHUB.md) - Issue management and PR guidelines
- [Usage Guide](../usage.md) - User installation and configuration
- [Architecture](../architecture.md) - Technical system design

---

**Last Updated**: 2025-09-02  
**Maintainer**: PressTalk Development Team