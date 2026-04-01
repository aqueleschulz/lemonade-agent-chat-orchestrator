import os
from pathlib import Path

# ---------------------------------------------------------------------------
# DRIVE_ROOT — root of the files accessed by the agent.
#
# Resolution order:
#   1. LUMINA_DRIVE_ROOT environment variable (defined in .env or docker-compose)
#   2. ./data folder relative to this file    (original behavior / fallback)
#
# Example values for LUMINA_DRIVE_ROOT:
#   Windows – Google Drive   : C:\Users\Name\Google Drive\Lumina
#   Windows – OneDrive       : C:\Users\Name\OneDrive\Lumina
#   Linux / NFS              : /mnt/shared/lumina
#   Docker (default value)   : /app/data  (mapped via volume in docker-compose)
# ---------------------------------------------------------------------------

_env_path = os.environ.get("LUMINA_DRIVE_ROOT", "").strip()

if _env_path:
    DRIVE_ROOT = Path(_env_path).resolve()
else:
    DRIVE_ROOT = (Path(__file__).parent / "data").resolve()

DRIVE_ROOT.mkdir(parents=True, exist_ok=True)

CHROMA_PATH = Path(os.environ.get("LUMINA_CHROMA_PATH", str(Path(__file__).parent / "chroma_db"))).resolve()
CHROMA_PATH.mkdir(parents=True, exist_ok=True)
