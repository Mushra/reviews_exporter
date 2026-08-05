import json
import os
from pathlib import Path

from core.paths import get_data_directory
from core.logger import Logger


logger = Logger(__name__)


YOUTUBE_API_KEY_ENV_VAR = "YOUTUBE_API_KEY"


def get_config_file() -> Path:

    return get_data_directory() / "config.json"


def load_config() -> dict:

    file = get_config_file()

    if not file.exists():

        return {}

    try:

        with open(file, encoding="utf-8") as f:

            return json.load(f)

    except Exception as error:

        logger.warning(f"Config illisible : {error}")

        return {}


def save_config(config: dict) -> None:

    file = get_config_file()

    file.parent.mkdir(parents=True, exist_ok=True)

    with open(file, "w", encoding="utf-8") as f:

        json.dump(config, f, indent=2, ensure_ascii=False)


def get_youtube_api_key() -> str | None:

    config = load_config()

    key = config.get("youtube_api_key")

    if key:

        return key

    return os.getenv(YOUTUBE_API_KEY_ENV_VAR)


def set_youtube_api_key(key: str) -> None:

    config = load_config()

    config["youtube_api_key"] = key.strip()

    save_config(config)
