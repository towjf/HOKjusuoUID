"""打包 gscore 插件上传包：dist/gs_jusuo.zip

包内结构（解压后直接放进 gsuid_core/plugins/ 即可用）：
    gs_jusuo/__init__.py
    gs_jusuo/jusuo_*.py
    README.md / LICENSE / requirements.txt
"""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ZIP = DIST / "gs_jusuo.zip"

DIST.mkdir(exist_ok=True)
ZIP.unlink(missing_ok=True)

written: list[str] = []
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted((ROOT / "gs_jusuo").glob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        archive.write(path, rel)
        written.append(rel)
    for name in ("README.md", "LICENSE", "requirements.txt"):
        path = ROOT / name
        if path.is_file():
            archive.write(path, name)
            written.append(name)

print(f"已生成 {ZIP}（{len(written)} 个文件，{ZIP.stat().st_size / 1024:.1f} KB）")
for name in written:
    print("  ", name)
