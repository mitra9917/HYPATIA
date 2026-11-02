"""Run fixture eval suite: python -m evals"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_run = Path(__file__).with_name("run.py")
_spec = importlib.util.spec_from_file_location("hypatia_evals_run", _run)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)
main = _mod.main

if __name__ == "__main__":
    main()
