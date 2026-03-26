"""Pytest configuration: ensure src is importable."""

import os
import sys

# Add the project root to the path so 'src' can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
