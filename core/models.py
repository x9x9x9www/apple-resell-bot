from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class Platform(str, Enum):
    AVITO = "Авито"
    YOULA = "Юла"


class RawItem(BaseModel):
    """Сырые данные о лоте напрямую с площадки до NLP обработки."""
    platform: Platform
    item_id: str
    title: str
    description: str = ""
    price: int
    url: str
    image_url: Optional[str] = None
    location: str = "Локация не указана"
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    # Поля для снижения цены
    old_price: Optional[int] = None
    is_price_drop: bool = False
    # Расширенные метаданные объявления (продавец, бронь, чат назначения)
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    seller_reviews_count: Optional[int] = None
    is_reserved: bool = False
    is_promoted: bool = False
    target_chat_id: Optional[int] = None


class ParsedGadget(BaseModel):
    """Нормализованный лот гаджета с вычлененными характеристиками и оценкой маржинальности."""
    platform: Platform
    item_id: str
    title: str
    description: str
    category: str = "other"  # iphone, macbook, samsung, pixel, ipad, consoles, watch, other
    model: str  # Например, "MacBook Air M2", "Samsung Galaxy S24 Ultra", "iPhone 15 Pro", "Pixel 8 Pro"
    storage_gb: int = 128  # Для телефонов ROM, для ноутбуков SSD (например, 256, 512, 1024)
    ram_gb: Optional[int] = None  # Оперативная память для ноутбуков/ПК (8, 16, 24, 32, 64)
    battery_health: Optional[int] = None  # АКБ (%)
    price: int  # Текущая цена продавца в рублях
    old_price: Optional[int] = None  # Предыдущая цена при снижении
    is_price_drop: bool = False  # Флаг снижения цены
    battery_penalty: int = 0  # Снижение лимита из-за износа батареи
    max_buy_price: Optional[int] = None  # Лимит выкупа
    market_price: Optional[int] = None  # Среднерыночная цена
    profit: Optional[int] = None  # market_price - price
    location: str
    url: str
    image_url: Optional[str] = None
    published_at: datetime
    is_profitable: bool = False
    rejection_reason: Optional[str] = None
    # Расширенные метаданные
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    seller_reviews_count: Optional[int] = None
    is_reserved: bool = False
    is_promoted: bool = False
    target_chat_id: Optional[int] = None


# Псевдоним для обратной совместимости
ParsedIPhone = ParsedGadget
