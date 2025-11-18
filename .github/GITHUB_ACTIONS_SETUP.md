# GitHub Actions Setup Complete! 🎉

Your project now has GitHub Actions configured with the following workflows:

## Workflows Created

### 1. **CI Workflow** (`.github/workflows/ci.yml`)
Runs on every push and pull request to `main` and `develop` branches.

**Jobs:**
- ✅ **Test** - Runs on Ubuntu, Windows, and macOS with Python 3.9-3.12
- ✅ **Lint** - Runs Ruff, Black, and mypy checks
- ✅ **Build** - Builds the package distribution

**Features:**
- Matrix testing across multiple OS and Python versions
- Code coverage with Codecov integration
- UV package manager for fast dependency installation
- Artifact uploads for built packages

### 2. **Release Workflow** (`.github/workflows/release.yml`)
Triggers when you push a version tag (e.g., `v1.0.0`).

**Features:**
- Runs full test suite before release
- Builds distribution packages
- Creates GitHub Release with notes
- Publishes to PyPI (requires setup)

## Setup Steps

### 1. Enable GitHub Actions
GitHub Actions should be automatically enabled for your repository.

### 2. Add Status Badges to README
Add these badges to your `README.md`:

```markdown
[![CI](https://github.com/TiredRebel/personal-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/TiredRebel/personal-assistant/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/TiredRebel/personal-assistant/branch/main/graph/badge.svg)](https://codecov.io/gh/TiredRebel/personal-assistant)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

### 3. Setup Codecov (Optional)
1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Add your repository
4. No token needed for public repos!

### 4. Setup PyPI Publishing (Optional)
To enable automatic PyPI publishing on release:

1. **Create PyPI Account**: Go to [pypi.org](https://pypi.org)
2. **Generate API Token**:
   - Go to Account Settings → API tokens
   - Create token with "Entire account" scope
3. **Add to GitHub Secrets**:
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI token (starts with `pypi-`)

### 5. Create a Release
```bash
# Tag your release
git tag v1.0.0
git push origin v1.0.0

# Or create via GitHub UI: Releases → Draft a new release
```

## Testing Locally Before Push

```bash
# Run tests
uv run pytest

# Check code formatting
uv run black --check src/ tests/

# Run linter
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

## What Happens on Push

1. **On every push/PR**: CI workflow runs
   - Tests on 3 OS × 4 Python versions = 12 test jobs
   - Linting checks (Ruff, Black, mypy)
   - Package build verification

2. **On tag push (v*.*.*)**: Release workflow runs
   - All tests must pass
   - Creates GitHub Release
   - Publishes to PyPI (if configured)

## Workflow Status

Check your workflows at:
`https://github.com/TiredRebel/personal-assistant/actions`

## Customization

### Modify Python Versions
Edit `.github/workflows/ci.yml`:
```yaml
python-version: ['3.9', '3.10', '3.11', '3.12', '3.13']
```

### Change Trigger Branches
```yaml
on:
  push:
    branches: [ main, develop, feature/* ]
```

### Skip CI on Specific Commits
Add to commit message:
```
[skip ci]
# or
[ci skip]
```

## Troubleshooting

### Tests failing on Windows?
Check path separators and line endings in tests.

### UV installation issues?
The workflow uses `astral-sh/setup-uv@v4` which handles all platforms.

### Coverage not uploading?
Make sure your repo is public or add `CODECOV_TOKEN` to secrets.

## Next Steps

1. ✅ Commit and push the workflow files
2. ✅ Watch the Actions tab for first run
3. ✅ Add status badges to README
4. ✅ (Optional) Setup Codecov and PyPI

Happy coding! 🚀
