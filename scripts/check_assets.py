"""Fail before deployment if Pages asset limits are exceeded."""

from pathlib import Path

root = Path(__file__).resolve().parents[1] / "web" / "build"
if not root.is_dir():
    raise SystemExit("Build web first")
files = [p for p in root.rglob("*") if p.is_file()]
large = [p for p in files if p.stat().st_size > 25 * 1024 * 1024]
if large or len(files) > 20000:
    raise SystemExit(f"Pages limits exceeded: {large}; files={len(files)}")
print(
    f"Pages asset check: {len(files)} files; largest {max(p.stat().st_size for p in files):,} bytes"
)
