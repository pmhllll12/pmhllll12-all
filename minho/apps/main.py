"""`backend/apps` 에서 API 서버 실행 (실제 앱은 `../main.py`).

  cd backend\\apps
  python main.py
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
_APPS = _BACKEND / "apps"
_backend_str = str(_BACKEND)
_apps_str = str(_APPS)
if _backend_str not in sys.path:
    sys.path.insert(0, _backend_str)
if _apps_str not in sys.path:
    sys.path.append(_apps_str)

from _import_aliases import install_secom_aliases  # noqa: E402

install_secom_aliases()

if __name__ == "__main__":
    runpy.run_path(str(_BACKEND / "main.py"), run_name="__main__")
