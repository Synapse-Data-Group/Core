# Contributing to MEO

Thank you for your interest in contributing to MEO (Memory Embedded Orchestration)!

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs or suggest features
- Provide clear reproduction steps for bugs
- Include your Python version and relevant dependencies

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests: `python test_meo.py`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to new classes and methods
- Keep functions focused and modular

### Testing

- Add tests for new features
- Ensure all existing tests pass
- Run `python test_meo.py` before submitting

### Documentation

- Update README.md if adding new features
- Add examples to `examples/` directory if applicable
- Update docstrings and inline comments

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/meo.git
cd meo

# Install in development mode
pip install -e .

# Run tests
python test_meo.py
```

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## Questions?

Feel free to open an issue for questions or discussions.

---

© 2026 Synapse Data / Ivan Lluch
