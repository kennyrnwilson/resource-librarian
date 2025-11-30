# First Release Guide - Complete Setup

This guide walks you through publishing your first release to PyPI from scratch.

## Overview

You'll complete these steps:
1. Create PyPI account (if needed)
2. Set up Trusted Publishing on PyPI
3. Prepare your code for release
4. Create GitHub Release (triggers auto-publish)

**Time required:** ~15 minutes

---

## Step 1: Create PyPI Account (If Needed)

If you don't have a PyPI account yet:

1. Go to https://pypi.org/account/register/
2. Fill in:
   - Username
   - Email address
   - Password
3. Verify your email address
4. **Enable 2FA (Two-Factor Authentication)** - Required for trusted publishing
   - Go to https://pypi.org/manage/account/
   - Click "Add 2FA with authentication application"
   - Use an app like Google Authenticator or Authy
   - Save your recovery codes!

---

## Step 2: Reserve Project Name on PyPI

Before setting up trusted publishing, you need to create the project on PyPI.

### Option A: Manual First Release (Recommended for First Time)

We'll do a manual first release, then subsequent releases will be automated.

**Install build tools:**

```bash
cd /home/kenne/code/resource-librarian
source venv/bin/activate
pip install build twine
```

**Build the package:**

```bash
python -m build
```

This creates files in `dist/`:
- `resource_librarian-0.1.0-py3-none-any.whl`
- `resource_librarian-0.1.0.tar.gz`

**Upload to PyPI:**

```bash
twine upload dist/*
```

You'll be prompted for:
- Username: (your PyPI username)
- Password: (your PyPI password)

✅ **Success!** Your package is now on PyPI: https://pypi.org/project/resource-librarian/

### Option B: Create Placeholder Project (Alternative)

If you want to set up trusted publishing FIRST:

1. Go to https://pypi.org/manage/projects/
2. Click "Publishing" tab
3. Add a pending publisher (see Step 3)
4. Then do the first release via GitHub

**Note:** Option A is recommended because it's simpler for the first release.

---

## Step 3: Configure Trusted Publishing on PyPI

Now that your project exists on PyPI, configure trusted publishing:

1. **Go to your project page:**
   - https://pypi.org/manage/project/resource-librarian/settings/publishing/

2. **Scroll to "GitHub Actions Publishing"**

3. **Click "Add a new publisher"**

4. **Fill in the form EXACTLY:**
   ```
   Owner: kennyrnwilson
   Repository name: resource-librarian
   Workflow name: publish.yml
   Environment name: (leave blank)
   ```

5. **Click "Add"**

✅ **Done!** PyPI will now trust your GitHub Actions workflow.

---

## Step 4: Verify Your Package Version

Check that `pyproject.toml` has the correct version:

```bash
grep "^version" pyproject.toml
```

Should show:
```
version = "0.1.0"
```

If it's different, update it:

```toml
[project]
name = "resource-librarian"
version = "0.1.0"  # Make sure this is 0.1.0
```

---

## Step 5: Commit and Push All Changes

Make sure all your recent work is committed:

```bash
# Check what's changed
git status

# Add all files
git add .

# Commit
git commit -m "Prepare for v0.1.0 release

- Added GitHub Actions publish workflow
- Added release documentation
- Fixed linting errors
- Added pre-push hooks
- Updated documentation"

# Push to GitHub
git push origin main
```

**Wait for CI to pass!** Check https://github.com/kennyrnwilson/resource-librarian/actions

---

## Step 6: Create Git Tag

Create a version tag for v0.1.0:

```bash
git tag -a v0.1.0 -m "Release v0.1.0 - First public release"
```

Push the tag:

```bash
git push origin v0.1.0
```

---

## Step 7: Create GitHub Release

### Option A: Via GitHub Web Interface (Easier)

1. **Go to:** https://github.com/kennyrnwilson/resource-librarian/releases

2. **Click:** "Draft a new release"

3. **Choose tag:** Select `v0.1.0` from dropdown

4. **Release title:** `Version 0.1.0`

5. **Description:** Use this template:

```markdown
# Resource Librarian v0.1.0

First public release! 🎉

## Features

### 📚 Book Management
- Support for PDF, EPUB, and Markdown formats
- Automatic metadata extraction
- EPUB chapter extraction
- Organized by author with normalized naming

### 🎥 YouTube Video Management
- Automatic transcript downloading
- Video metadata capture
- Organized by channel
- Batch processing support

### 🗂️ Library Organization
- Filesystem-first architecture (no database)
- YAML manifests for structured metadata
- Generated Markdown indices
- Searchable catalog

### 🔍 Browse & Search
- List books and videos
- Filter by author, channel, category
- Retrieve content and summaries
- Navigate with generated indices

## Installation

```bash
pip install resource-librarian
```

## Quick Start

```bash
# Initialize a new library
rl init my-library
cd my-library

# Add a book
rl book add /path/to/book.epub --author "Author Name"

# Fetch a YouTube video transcript
export YOUTUBE_API_KEY="your-api-key"
rl video fetch https://youtube.com/watch?v=VIDEO_ID

# List your collection
rl book list
rl video list
```

## Documentation

- [README](https://github.com/kennyrnwilson/resource-librarian#readme)
- [Getting Started Guide](https://github.com/kennyrnwilson/resource-librarian/blob/main/docs/GETTING_STARTED.md)
- [Architecture](https://github.com/kennyrnwilson/resource-librarian/blob/main/docs/ARCHITECTURE.md)

## Requirements

- Python 3.11+
- YouTube Data API key (for video features)

## What's Next

See our [project roadmap](https://github.com/kennyrnwilson/resource-librarian/blob/main/docs/IMPLEMENTATION_PLAN.md) for upcoming features.
```

6. **Click:** "Publish release"

### Option B: Via GitHub CLI (Faster)

Install GitHub CLI if needed: https://cli.github.com/

```bash
gh release create v0.1.0 \
  --title "Version 0.1.0" \
  --notes-file - <<'EOF'
# Resource Librarian v0.1.0

First public release! 🎉

## Features

### 📚 Book Management
- Support for PDF, EPUB, and Markdown formats
- Automatic metadata extraction
- EPUB chapter extraction

### 🎥 YouTube Video Management
- Automatic transcript downloading
- Video metadata capture

### 🗂️ Library Organization
- Filesystem-first architecture
- YAML manifests
- Generated indices

## Installation

```bash
pip install resource-librarian
```

See [README](https://github.com/kennyrnwilson/resource-librarian#readme) for more details.
EOF
```

---

## Step 8: Watch the Magic Happen!

1. **Go to Actions tab:**
   - https://github.com/kennyrnwilson/resource-librarian/actions

2. **You should see:** "Publish to PyPI" workflow running

3. **Click on it** to watch the progress

4. **Wait for green checkmark** (takes ~2-3 minutes)

---

## Step 9: Verify Publication

After the workflow succeeds:

1. **Check PyPI:**
   - Go to https://pypi.org/project/resource-librarian/
   - You should see version 0.1.0

2. **Test installation in fresh environment:**

```bash
# Create test directory
cd /tmp
python -m venv test-install
source test-install/bin/activate

# Install from PyPI
pip install resource-librarian

# Test it works
rl --version

# Should output: 0.1.0
```

---

## Troubleshooting

### "Project name already exists"
If someone else took the name, you'll need to:
1. Change project name in `pyproject.toml`
2. Choose a unique name like `resource-librarian-kw`

### "Publisher not found"
- Double-check trusted publishing configuration
- Make sure repository name is exact: `resource-librarian`
- Workflow name must be: `publish.yml`
- Wait a few minutes and try again

### "Workflow failed"
Check the logs:
1. Go to Actions tab
2. Click on failed workflow
3. Read the error message
4. Common issues:
   - Build failed: Run `./check.sh` locally first
   - Permission denied: Check trusted publishing config
   - Version conflict: Version 0.1.0 already exists

### "403 Forbidden"
- Make sure you have 2FA enabled on PyPI
- Verify trusted publishing is configured correctly
- Repository owner must match exactly

---

## Success Checklist

- [ ] PyPI account created with 2FA enabled
- [ ] First release uploaded (manual or via workflow)
- [ ] Trusted publishing configured on PyPI
- [ ] Git tag v0.1.0 created and pushed
- [ ] GitHub Release created
- [ ] Workflow ran successfully (green checkmark)
- [ ] Package visible on https://pypi.org/project/resource-librarian/
- [ ] `pip install resource-librarian` works
- [ ] `rl --version` shows 0.1.0

---

## What's Next?

For future releases:

1. Update version in `pyproject.toml`
2. Commit and push
3. Create tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
4. Push tag: `git push origin v0.2.0`
5. Create GitHub Release → Auto-publishes to PyPI!

See [RELEASE.md](RELEASE.md) for detailed release process.

---

## Quick Reference

```bash
# Build locally
python -m build

# Manual upload (first time only)
twine upload dist/*

# For subsequent releases (automated)
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
gh release create v0.2.0 --title "v0.2.0" --notes "Changes..."
```

---

**Need help?** Open an issue: https://github.com/kennyrnwilson/resource-librarian/issues
