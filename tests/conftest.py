"""Shared fixtures — makes the service package importable from the tests."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for pkg_dir in ("service",):
    path = os.path.join(ROOT, pkg_dir)
    if path not in sys.path:
        sys.path.insert(0, path)
