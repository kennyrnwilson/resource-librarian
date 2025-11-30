# Release Process

This document describes how to create releases and publish to PyPI using GitHub's automated workflow.

## Overview

The project uses **GitHub Releases** to trigger automatic PyPI publishing:

1. Create a GitHub Release (via UI or CLI)
2. GitHub Actions automatically builds and publishes to PyPI
3. Uses PyPI Trusted Publishing (no API tokens needed)

## Prerequisites

### One-Time Setup: Configure PyPI Trusted Publishing

Before your first release, configure trusted publishing on PyPI:

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the form:
   - **PyPI Project Name**: `resource-librarian`
   - **Owner**: `kennyrnwilson` (your GitHub username)
   - **Repository name**: `resource-librarian`
   - **Workflow name**: `publish.yml`
   - **Environment name**: (leave blank)
4. Click "Add"

This allows GitHub Actions to publish without storing API tokens.

## Creating a Release

### Step 1: Update Version Number

Edit `pyproject.toml` and update the version:

```toml
[project]
name = "resource-librarian"
version = "0.2.0"  # <- Update this
```

Commit and push:

```bash
git add pyproject.toml
git commit -m "Bump version to 0.2.0"
git push origin main
```

### Step 2: Create a Git Tag

```bash
# Create annotated tag
git tag -a v0.2.0 -m "Release v0.2.0"

# Push tag to GitHub
git push origin v0.2.0
```

### Step 3: Create GitHub Release

**Option A: Via GitHub Web UI**

1. Go to https://github.com/kennyrnwilson/resource-librarian/releases
2. Click "Draft a new release"
3. Click "Choose a tag" and select `v0.2.0`
4. Fill in release details:
   - **Release title**: `v0.2.0` or `Version 0.2.0`
   - **Description**: What's new in this release (see template below)
5. Click "Publish release"

**Option B: Via GitHub CLI**

```bash
# Install gh CLI if needed: https://cli.github.com/

# Create release with notes
gh release create v0.2.0 \
  --title "Version 0.2.0" \
  --notes "$(cat <<'EOF'
## What's New

- Feature 1
- Feature 2
- Bug fix 1

## Documentation

- Updated documentation links
- Added release process guide

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.
EOF
)"
```

### Step 4: Verify Publishing

After creating the release:

1. Go to https://github.com/kennyrnwilson/resource-librarian/actions
2. Watch the "Publish to PyPI" workflow run
3. Verify it completes successfully (green checkmark)
4. Check https://pypi.org/project/resource-librarian/ to see the new version

## Release Notes Template

Use this template when creating release notes:

```markdown
## What's New in v0.2.0

### Features
- ✨ New feature 1
- ✨ New feature 2

### Improvements
- 🚀 Performance improvement
- 📚 Documentation updates

### Bug Fixes
- 🐛 Fixed issue #123
- 🐛 Fixed edge case in parsing

### Developer Experience
- 🔧 Added pre-push hooks
- 🧪 Improved test coverage

## Installation

```bash
pip install --upgrade resource-librarian
```

## Breaking Changes

⚠️ **None** - This release is fully backward compatible.

## Full Changelog

https://github.com/kennyrnwilson/resource-librarian/compare/v0.1.0...v0.2.0
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **Major** (1.0.0): Breaking changes
- **Minor** (0.2.0): New features, backward compatible
- **Patch** (0.1.1): Bug fixes, backward compatible

Examples:
- `0.1.0` → `0.2.0`: Added new commands
- `0.1.0` → `0.1.1`: Fixed bug in parsing
- `0.9.0` → `1.0.0`: First stable release with breaking changes

## Rollback a Release

If you need to rollback:

1. Delete the GitHub release (doesn't delete the tag)
2. Remove the package from PyPI (contact PyPI support)
3. Create a new patch version with the fix

## Testing Before Release

Always test before releasing:

```bash
# Run all checks
./check.sh

# Build locally to verify
python -m build

# Test the built package
pip install dist/resource_librarian-0.2.0-py3-none-any.whl
rl --version
```

## TestPyPI (Optional)

To test publishing without affecting production PyPI:

1. Configure TestPyPI trusted publishing at https://test.pypi.org/manage/account/publishing/
2. Create a release with a pre-release tag (e.g., `v0.2.0-beta.1`)
3. Modify workflow to publish to TestPyPI first

## Troubleshooting

### "Publishing not configured"

- Ensure PyPI trusted publishing is set up (see Prerequisites)
- Verify repository name and workflow name match exactly

### "Version already exists"

- You cannot overwrite PyPI versions
- Increment version number and create new release

### Workflow fails

- Check GitHub Actions logs for details
- Verify `pyproject.toml` is valid (`pip install build && python -m build`)
- Ensure all tests pass before releasing

## Quick Reference

```bash
# 1. Update version in pyproject.toml
# 2. Commit and push
git add pyproject.toml
git commit -m "Bump version to 0.2.0"
git push origin main

# 3. Create and push tag
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0

# 4. Create GitHub release (triggers auto-publish)
gh release create v0.2.0 --title "v0.2.0" --notes "Release notes here"

# 5. Verify at https://pypi.org/project/resource-librarian/
```

## Resources

- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [Semantic Versioning](https://semver.org/)
- [GitHub CLI](https://cli.github.com/)
