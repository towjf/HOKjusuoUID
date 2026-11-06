"""打包 gscore 插件上传包。

产物：
    dist/HOKjusuoUID-flat.zip   根层直接是 __init__.py，供控制台「上传 zip 安装」
    dist/HOKjusuoUID.zip        根层是 HOKjusuoUID/ 文件夹，供手动解压到 plugins/

用法：python scripts/build_release.py
"""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "HOKjusuoUID"
DIST = ROOT / "dist"

EXTRA_FILES = ("README.md", "INSTALL.md", "LICENSE", "requirements.txt")


def build(zip_path: Path, wrapper: bool) -> int:
    zip_path.unlink(missing_ok=True)
    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(PKG.glob("*.py")):
            arcname = f"{PKG.name}/{path.name}" if wrapper else path.name
            archive.write(path, arcname)
            count += 1
        for name in EXTRA_FILES:
            path = ROOT / name
            if path.is_file():
                archive.write(path, name)
                count += 1
    return count


def main() -> None:
    DIST.mkdir(exist_ok=True)
    for filename, wrapper in (("HOKjusuoUID-flat.zip", False), ("HOKjusuoUID.zip", True)):
        target = DIST / filename
        count = build(target, wrapper)
        print(f"{target.name}: {count} 个文件，{target.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
