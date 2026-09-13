"""Optional legacy entry — prefer root index.py on Vercel."""

# Re-export so older /api routing still reaches the same FastAPI app.
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

app = importlib.import_module("index").app
