# MEO Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation Methods

### Method 1: Development Installation (Recommended for Testing)

```bash
# Navigate to the MEO directory
cd C:\Users\Usuario\Desktop\Synapse\AI\Tools\MEO

# Install in editable mode
pip install -e .
```

This allows you to modify the code and see changes immediately without reinstalling.

### Method 2: Standard Installation

```bash
cd C:\Users\Usuario\Desktop\Synapse\AI\Tools\MEO
pip install .
```

### Method 3: Build and Install Wheel

```bash
# Install build tools
pip install build

# Build the package
python -m build

# Install the wheel
pip install dist/synapse_meo-0.1.0-py3-none-any.whl
```

## Optional Dependencies

### For LangChain Integration

```bash
pip install synapse-meo[langchain]
```

### For Autogen Integration

```bash
pip install synapse-meo[autogen]
```

### For Development

```bash
pip install synapse-meo[dev]
```

## Verify Installation

Run the test suite to verify everything works:

```bash
python test_meo.py
```

Expected output:
```
============================================================
MEO Package Test Suite
============================================================
Testing imports...
✓ All imports successful

Testing basic orchestration...
✓ Basic orchestration works

Testing memory system...
✓ Memory system works

Testing evaluation system...
✓ Evaluation system works

Testing policy adapter...
✓ Policy adapter works

Testing storage backends...
✓ Storage backends work

Testing framework integrations...
✓ Integration wrappers available

Testing full workflow with all components...
✓ Full workflow integration works

============================================================
Results: 8/8 tests passed
============================================================

✓ All tests passed! MEO package is working correctly.
```

## Quick Test

```python
from meo import WisdomOrchestrator

orchestrator = WisdomOrchestrator()
print("MEO installed successfully!")
```

## Run Examples

```bash
# Basic usage example
python examples/basic_usage.py

# LangChain integration example
python examples/langchain_example.py

# Autogen integration example
python examples/autogen_example.py

# Custom components example
python examples/custom_components.py
```

## Troubleshooting

### Import Error

If you get `ModuleNotFoundError: No module named 'meo'` (note: the package name is `synapse-meo` but you import as `meo`):
- Ensure you're in the correct directory
- Try reinstalling: `pip install -e .`
- Check Python path: `python -c "import sys; print(sys.path)"`

### Permission Error

If you get permission errors on Windows:
- Run command prompt as Administrator
- Or use: `pip install --user -e .`

### Missing Dependencies

If you get import errors for numpy:
```bash
pip install numpy>=1.20.0
```

## Uninstall

```bash
pip uninstall synapse-meo
```

## Next Steps

1. Read the [QUICKSTART.md](QUICKSTART.md) for a 5-minute tutorial
2. Check [README.md](README.md) for comprehensive documentation
3. Explore [examples/](examples/) for usage patterns
4. Review [STRUCTURE.md](STRUCTURE.md) for architecture details

## Support

For issues or questions:
- Check the documentation files
- Review example scripts
- Run the test suite to identify problems
