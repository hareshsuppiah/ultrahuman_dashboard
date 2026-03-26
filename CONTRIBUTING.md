# Contributing to the Ultrahuman Dashboard

Thank you for your interest in contributing to the Ultrahuman Dashboard. This document outlines how to report issues, suggest improvements, and submit code changes.

## Reporting Bugs

If you encounter a bug, please open an issue on the [GitHub issue tracker](https://github.com/hareshsuppiah/ultrahuman_dashboard/issues) with:

- A clear description of the problem
- Steps to reproduce the issue
- Your operating system and Python version
- Any relevant error messages or screenshots

## Suggesting Features

Feature requests are welcome. Please open an issue describing the proposed feature, its use case, and how it would benefit researchers or practitioners using the dashboard.

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run the test suite to ensure nothing is broken:
   ```bash
   source venv/bin/activate
   python -m pytest tests/ -v
   ```
5. Commit your changes with a descriptive message
6. Push to your fork and open a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/hareshsuppiah/ultrahuman_dashboard.git
cd ultrahuman_dashboard

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install pytest

# Run the application
python src/main.py

# Run tests
python -m pytest tests/ -v
```

## Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to new functions and modules

## Questions

If you have questions about contributing, please open an issue on GitHub.
