"""Pytest root conftest.

Ensures `backend/` is importable as the package root so test modules can do
`from app.db.base import Base` without the test runner being invoked from
inside `backend/`.
"""

import os
import sys

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)