import tempfile
from pathlib import Path

_BASE = Path(tempfile.mkdtemp(prefix="gs_res_"))


def get_res_path(name="gsuid_core"):
    path = _BASE / name
    path.mkdir(parents=True, exist_ok=True)
    return path
