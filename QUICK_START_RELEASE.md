# Quick Start: First Release Checklist

Copy-paste these commands in order for your first release.

## Prerequisites

```bash
cd /home/kenne/code/resource-librarian
source venv/bin/activate
pip install build twine
```

## Step 1: Manual First Release to PyPI

```bash
# Build the package
python -m build

# Upload to PyPI (you'll be prompted for username/password)
twine upload dist/*
```

✅ Package is now on PyPI!

## Step 2: Configure Trusted Publishing

1. Go to: https://pypi.org/manage/project/resource-librarian/settings/publishing/
2. Click "Add a new publisher"
3. Fill in:
   - Owner: `kennyrnwilson`
   - Repository: `resource-librarian`
   - Workflow: `publish.yml`
   - Environment: (leave blank)
4. Click "Add"

✅ Trusted publishing configured!

## Step 3: Commit and Push

```bash
# Make sure all changes are committed
git status
git add .
git commit -m "Prepare for v0.1.0 release"
git push origin main
```

Wait for tests to pass at: https://github.com/kennyrnwilson/resource-librarian/actions

## Step 4: Create Tag

```bash
git tag -a v0.1.0 -m "Release v0.1.0 - First public release"
git push origin v0.1.0
```

## Step 5: Create GitHub Release

### Option A: Web Interface

Go to: https://github.com/kennyrnwilson/resource-librarian/releases/new
- Tag: v0.1.0
- Title: Version 0.1.0
- Description: (See FIRST_RELEASE_GUIDE.md for template)
- Click "Publish release"

### Option B: CLI

```bash
gh release create v0.1.0 \
  --title "Version 0.1.0" \
  --notes "First public release of Resource Librarian 🎉

## Features
- Book management (PDF, EPUB, Markdown)
- YouTube video transcript fetching
- Filesystem-based library organization
- Generated indices and catalogs

## Installation
\`\`\`bash
pip install resource-librarian
\`\`\`

See README for details."
```

## Step 6: Verify

Watch workflow: https://github.com/kennyrnwilson/resource-librarian/actions

After success:

```bash
# Test installation
cd /tmp
python -m venv test-env
source test-env/bin/activate
pip install resource-librarian
rl --version  # Should show: 0.1.0
```

## Done! 🎉

Your package is live at: https://pypi.org/project/resource-librarian/

## Future Releases (Automated)

```bash
# 1. Update version in pyproject.toml
# 2. Commit and push
git add pyproject.toml
git commit -m "Bump version to 0.2.0"
git push origin main

# 3. Create and push tag
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0

# 4. Create GitHub Release (auto-publishes to PyPI)
gh release create v0.2.0 --title "v0.2.0" --notes "Changes..."
```
