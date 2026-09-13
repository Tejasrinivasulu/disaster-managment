"""Build React for Vercel (frontend/dist used by index.py)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"


def main() -> int:
    print("Installing frontend dependencies...")
    subprocess.check_call(
        ["npm", "install"],
        cwd=FRONTEND,
        shell=(sys.platform == "win32"),
    )
    print("Building Vite production bundle...")
    subprocess.check_call(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        shell=(sys.platform == "win32"),
    )
    dist = FRONTEND / "dist" / "index.html"
    if not dist.exists():
        raise SystemExit("frontend/dist/index.html missing after build")
    print(f"Frontend ready at {dist.parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
