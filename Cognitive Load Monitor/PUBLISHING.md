# Publishing to PyPI - Step by Step Guide

## Prerequisites

1. **Create PyPI account**: https://pypi.org/account/register/
2. **Create TestPyPI account** (for testing): https://test.pypi.org/account/register/
3. **Install build tools**:
   ```bash
   pip install build twine
   ```

## Step 1: Verify Package Structure

Your package should look like this:
```
cognitive-load-monitor/
├── src/
│   └── cognitive_load_monitor/
│       ├── __init__.py
│       └── monitor.py
├── pyproject.toml
├── README.md
├── LICENSE
├── MANIFEST.in
└── .gitignore
```

## Step 2: Update Version (for future releases)

Edit `pyproject.toml` and `src/cognitive_load_monitor/__init__.py`:
```python
__version__ = "0.1.1"  # Increment version
```

## Step 3: Build the Package

From the project root directory:
```bash
python -m build
```

This creates:
- `dist/cognitive_load_monitor-0.1.0.tar.gz` (source distribution)
- `dist/cognitive_load_monitor-0.1.0-py3-none-any.whl` (wheel)

## Step 4: Test on TestPyPI (RECOMMENDED FIRST TIME)

Upload to TestPyPI:
```bash
python -m twine upload --repository testpypi dist/*
```

You'll be prompted for:
- Username: Your TestPyPI username
- Password: Your TestPyPI password (or API token)

Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ cognitive-load-monitor
```

## Step 5: Upload to Production PyPI

Once tested, upload to real PyPI:
```bash
python -m twine upload dist/*
```

Enter your PyPI credentials when prompted.

## Step 6: Verify Installation

```bash
pip install cognitive-load-monitor
```

Test it works:
```python
from cognitive_load_monitor import CognitiveLoadMonitor
monitor = CognitiveLoadMonitor()
print("Success!")
```

## Using API Tokens (More Secure)

### Create API Token
1. Go to https://pypi.org/manage/account/token/
2. Create a new token with "Upload packages" scope
3. Save the token (starts with `pypi-`)

### Configure `.pypirc`
Create `~/.pypirc` (Windows: `%USERPROFILE%\.pypirc`):
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
```

Now you can upload without entering credentials:
```bash
python -m twine upload dist/*
```

## Updating the Package

1. Make your changes to the code
2. Update version in `pyproject.toml` and `__init__.py`
3. Clean old builds: `rm -rf dist/ build/ *.egg-info`
4. Rebuild: `python -m build`
5. Upload: `python -m twine upload dist/*`

## Version Numbering

Follow semantic versioning (MAJOR.MINOR.PATCH):
- **PATCH** (0.1.1): Bug fixes, no API changes
- **MINOR** (0.2.0): New features, backward compatible
- **MAJOR** (1.0.0): Breaking changes

## Checklist Before Publishing

- [ ] All tests pass
- [ ] README is up to date
- [ ] Version number incremented
- [ ] LICENSE file is correct
- [ ] No sensitive data in code
- [ ] Package builds without errors
- [ ] Tested on TestPyPI first
- [ ] Git repository is clean and pushed

## Common Issues

**"File already exists"**
- You can't re-upload the same version
- Increment version number and rebuild

**"Invalid distribution"**
- Check `pyproject.toml` syntax
- Ensure all required files exist

**Import errors after install**
- Check `__init__.py` exports
- Verify package structure in `src/`

## Monitoring Your Package

- **PyPI page**: https://pypi.org/project/cognitive-load-monitor/
- **Download stats**: https://pypistats.org/packages/cognitive-load-monitor
- **Security**: Enable 2FA on PyPI account

## Support

For issues with PyPI itself: https://pypi.org/help/

---

**Ready to publish?** Start with TestPyPI, then move to production PyPI.
