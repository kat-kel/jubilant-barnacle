from pathlib import Path

from src.__version__ import __version__ as VERSION

VERSION

LOG_DIR = Path("log")
LOG_DIR.mkdir(exist_ok=True)
for f in LOG_DIR.iterdir():
    f.unlink()
