"""Configuração e caminhos do projeto."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    database_url: str
    open_meteo_timeout_seconds: int

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def intermediate_dir(self) -> Path:
        return self.data_dir / "intermediate"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"


def get_settings() -> Settings:
    load_dotenv()
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://olist:olist_local@localhost:5433/olist_clima",
    )
    timeout = int(os.getenv("OPEN_METEO_TIMEOUT_SECONDS", "90"))
    return Settings(
        data_dir=data_dir,
        database_url=database_url,
        open_meteo_timeout_seconds=timeout,
    )
