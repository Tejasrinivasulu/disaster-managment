"""Build React frontend for Vercel (copies dist -> public for CDN)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
PUBLIC = ROOT / "public"


def main() -> int:
    print("Installing frontend dependencies...")
    subprocess.check_call(["npm", "install"], cwd=FRONTEND, shell=(sys.platform == "win32"))
    print("Building Vite production bundle...")
    subprocess.check_call(["npm", "run", "build"], cwd=FRONTEND, shell=(sys.platform == "win32"))

    dist = FRONTEND / "dist"
    if not dist.exists():
        raise SystemExit("frontend/dist missing after build")

    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    shutil.copytree(dist, PUBLIC)
    print(f"Copied {dist} -> {PUBLIC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
