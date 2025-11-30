# Release Checklist

Use this checklist when creating a new release.

## Pre-Release

- [ ] All tests pass: `./check.sh`
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG updated (if you maintain one)
- [ ] Documentation updated
- [ ] Commit all changes: `git commit -am "Prepare release v0.x.0"`
- [ ] Push to main: `git push origin main`

## Release

- [ ] Create git tag: `git tag -a v0.x.0 -m "Release v0.x.0"`
- [ ] Push tag: `git push origin v0.x.0`
- [ ] Create GitHub Release (triggers auto-publish):
  ```bash
  gh release create v0.x.0 --title "v0.x.0" --notes "Release notes..."
  ```

## Post-Release

- [ ] Verify GitHub Actions workflow completed successfully
- [ ] Verify package appears on PyPI: https://pypi.org/project/resource-librarian/
- [ ] Test installation: `pip install --upgrade resource-librarian`
- [ ] Verify `rl --version` shows correct version
- [ ] Announce release (if applicable)

## First Release Only

- [ ] Configure PyPI trusted publishing at https://pypi.org/manage/account/publishing/
  - Project: `resource-librarian`
  - Owner: `kennyrnwilson`
  - Repository: `resource-librarian`
  - Workflow: `publish.yml`

## Quick Commands

```bash
# Update version in pyproject.toml, then:
git add pyproject.toml
git commit -m "Bump version to 0.2.0"
git push origin main

# Create and push tag
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0

# Create release (auto-publishes to PyPI)
gh release create v0.2.0 \
  --title "Version 0.2.0" \
  --notes "Brief description of changes"
```
