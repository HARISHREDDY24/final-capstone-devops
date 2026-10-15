from pathlib import Path
import sys

# Ensure the backend package is importable whether pytest is launched as a
# console script or as `python -m pytest`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
