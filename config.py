from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class Settings:
    bot_token: str
    data_dir: Path
    db_path: Path
    backups_dir: Path



def load_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "")
    data_dir = Path(os.getenv("DATA_DIR", "/data"))
    db_path = Path(os.getenv("DB_PATH", str(data_dir / "bot.db")))
    backups_dir = Path(os.getenv("BACKUPS_DIR", str(data_dir / "backups")))

    data_dir.mkdir(parents=True, exist_ok=True)
    backups_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        bot_token=bot_token,
        data_dir=data_dir,
        db_path=db_path,
        backups_dir=backups_dir,
    )
