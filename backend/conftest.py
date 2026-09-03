"""Backend pytest conftest.

Ensures the `app` package (this directory) is importable so test modules can
do `from app.db.base import Base` regardless of where pytest is invoked from.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
