from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    BASE_DIR: Path = Path(__file__).resolve().parent

    # Telegram
    BOT_TOKEN: str = Field(default="YOUR_BOT_TOKEN_HERE")
    TARGET_CHAT_ID: int = Field(default=0)

    @field_validator("TARGET_CHAT_ID", mode="before")
    @classmethod
    def parse_target_chat_id(cls, v: Any) -> int:
        if v is None or v == "" or (isinstance(v, str) and not v.strip()):
            return 0
        try:
            return int(v)
        except (ValueError, TypeError):
            return 0

    # Redis & Deduplication
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_TTL_HOURS: int = Field(default=48)
    DEDUP_DB_FILE: str = Field(default="dedup_cache.db")
    MIN_PRICE_DROP_RUB: int = Field(default=500)  # Минимальная скидка для алерта (отсекает колебания)
    SEMANTIC_DEDUP_WINDOW_HOURS: int = Field(default=12)  # Окно отсева семантических дублей (часов)

    # Latency & Monitoring Settings
    MAX_ITEM_AGE_SECONDS: int = Field(default=300)  # 5 min freshness window
    AVITO_POLL_INTERVAL_SEC: float = Field(default=3.0)
    YOULA_POLL_INTERVAL_SEC: float = Field(default=3.0)

    # Regional search
    AVITO_LOCATION_ID: str = Field(default="637640")  # Москва
    YOULA_CITY_ID: str = Field(default="576d06124994ee94589d8194")  # Москва

    # Proxies
    PROXIES_FILE: str = Field(default="proxies.txt")

    # Pricing matrix path
    PRICING_FILE: str = Field(default="pricing_matrix.json")

    def load_pricing_matrix(self) -> dict[str, dict[str, dict[str, int]]]:
        pricing_path = Path(self.PRICING_FILE)
        if not pricing_path.exists():
            # Try finding it relative to root
            pricing_path = Path(__file__).parent / "pricing_matrix.json"
        if pricing_path.exists():
            with open(pricing_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def load_proxies(self) -> List[str]:
        proxy_path = Path(self.PROXIES_FILE)
        if not proxy_path.exists():
            return []
        with open(proxy_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            return lines


settings = Settings()
