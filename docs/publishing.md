# Publishing Cicadas to PyPI

This document describes how to publish the `cicadas` package to PyPI.

## Package Information

- **Package Name**: `cicadas`
- **PyPI URL**: https://pypi.org/project/cicadas/
- **TestPyPI URL**: https://test.pypi.org/project/cicadas/

## Prerequisites

### GitHub Repository Setup

1. **Create PyPI Trusted Publisher** (recommended):
   - Go to https://pypi.org/manage/account/publishing/
   - Add a new pending publisher:
     - PyPI Project Name: `cicadas`
     - Owner: `ecodan` (or your GitHub org/user)
     - Repository: `cicadas`
     - Workflow name: `publish.yml`
     - Environment name: `pypi`

2. **Create TestPyPI Trusted Publisher** (for testing):
   - Go to https://test.pypi.org/manage/account/publishing/
   - Add a new pending publisher with:
     - Environment name: `testpypi`

3. **Create GitHub Environments**:
   - Go to your repository Settings → Environments
   - Create `pypi` environment (optionally add protection rules)
   - Create `testpypi` environment

## Publishing Methods

### Method 1: Automatic Publishing via GitHub Release (Recommended)

1. Update the version in `pyproject.toml` and `src/cicadas/__init__.py`
2. Commit the version bump
3. Create a new GitHub Release:
   - Go to Releases → Draft a new release
   - Create a new tag (e.g., `v0.3.1`)
   - Write release notes
   - Publish the release

The `publish.yml` workflow will automatically build and publish to PyPI.

### Method 2: Manual Publishing via Workflow Dispatch

1. Go to Actions → "Build and Publish to PyPI"
2. Click "Run workflow"
3. Select the destination:
   - `testpypi` for testing
   - `pypi` for production

### Method 3: Local Publishing (Development)

For local testing or manual publishing:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Version Management

The version is defined in two places (keep them in sync):

1. `pyproject.toml`: `version = "X.Y.Z"`
2. `src/cicadas/__init__.py`: `__version__ = "X.Y.Z"`

Follow [Semantic Versioning](https://semver.org/):

- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

## Testing the Package

### Test Installation from TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cicadas
```

### Test Installation from PyPI

```bash
pip install cicadas
```

### Verify Installation

```bash
cicadas --version
cicadas --help
```

## Troubleshooting

### "Package already exists" Error

Each version can only be uploaded once. Bump the version number and try again.

### Trusted Publisher Not Working

1. Verify the workflow name matches exactly (`publish.yml`)
2. Verify the environment name matches (`pypi` or `testpypi`)
3. Check that the repository owner/name matches

### Build Failures

Run locally to debug:

```bash
python -m build --no-isolation
```

## CI/CD Pipeline

The repository includes two workflows:

1. **`ci.yml`**: Runs on every push/PR
   - Tests (Python 3.11, 3.12, 3.13)
   - Linting (ruff)
   - Build verification

2. **`publish.yml`**: Publishes to PyPI
   - Triggered by GitHub releases (→ PyPI)
   - Manual dispatch (→ TestPyPI or PyPI)
