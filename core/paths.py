import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_NAME = "MetacriticReviewExporter"
DATA_DIR_ENV_VAR = "METACRITIC_EXPORT_DATA_DIR"


def get_project_root() -> Path:
    return PROJECT_ROOT


def get_default_data_directory() -> Path:
    override = os.getenv(DATA_DIR_ENV_VAR)
    if override:
        return Path(override).expanduser().resolve()

    repo_data_dir = PROJECT_ROOT / "data"
    if repo_data_dir.exists():
        return repo_data_dir

    if os.name == "nt":
        base = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    return base / APP_NAME / "data"


def get_data_directory() -> Path:
    return DATA_DIRECTORY


def set_data_directory(directory: str | Path) -> Path:
    global DATA_DIRECTORY
    DATA_DIRECTORY = Path(directory).expanduser().resolve()
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    return DATA_DIRECTORY


DATA_DIRECTORY = get_default_data_directory()
