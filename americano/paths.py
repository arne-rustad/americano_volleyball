from pathlib import Path

# Base directory of the package
PACKAGE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = PACKAGE_DIR.parent

SAVED_PLAYERS_PATH = BACKEND_DIR / "saved_players.yaml"