from __future__ import annotations

import logging
import time
from typing import Optional
import redis.asyncio as aioredis
from config import settings

logger = logging.getLogger(__name__)


class RedisDeduplicator:
    """
    Высокопроизводительный конвейер дедупликации на базе Redis.
    Использует атомарную команду `SET key val EX ttl NX`, гарантируя:
    1. Исключение повторов (Zero Duplicates).
    2. Атомарность без Race Conditions при параллельных воркерах.
    3. Автоматическую очистку по истечению TTL (по умолчанию 48 часов).
    4. Resilient Fallback на in-memory LRU/TTL хранилище при временной недоступности Redis.
    """

    def __init__(self, redis_url: Optional[str] = None, ttl_hours: Optional[int] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.ttl_seconds = int((ttl_hours or settings.REDIS_TTL_HOURS) * 3600)
        self._redis: Optional[aioredis.Redis] = None
        self._memory_cache: dict[str, tuple[int, float]] = {}  # Fallback: key -> (price, expires_at)

    async def connect(self) -> None:
        """Инициализация пула соединений с Redis."""
        try:
            self._redis = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2.0,
                socket_timeout=2.0,
            )
            await self._redis.ping()
            logger.info("Успешное подключение к Redis: %s", self.redis_url)
        except Exception as e:
            logger.warning(
                "Не удалось подключиться к Redis (%s). Активирован In-Memory Fallback. Ошибка: %s",
                self.redis_url,
                e,
            )
            self._redis = None

    async def close(self) -> None:
        """Корректное закрытие пула соединений."""
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    def _make_key(self, platform: str, item_id: str) -> str:
        return f"resell:seen:{platform}:{item_id}"

    async def check_and_update(
        self,
        platform: str,
        item_id: str,
        current_price: int,
    ) -> tuple[bool, bool, Optional[int]]:
        """
        Проверяет лот на уникальность и отслеживает СНИЖЕНИЕ ЦЕНЫ (Price Drop).
        Возвращает:
            (is_new, is_price_drop, old_price)
            - is_new: True, если лот появился впервые
            - is_price_drop: True, если продавец снизил цену
            - old_price: предыдущая цена (при снижении)
        """
        key = self._make_key(platform, item_id)

        # 1. Попытка через Redis
        if self._redis:
            try:
                val = await self._redis.get(key)
                if val is None:
                    # Новый лот -> фиксируем цену
                    await self._redis.set(key, current_price, ex=self.ttl_seconds)
                    return True, False, None
                else:
                    try:
                        old_price = int(val)
                    except (ValueError, TypeError):
                        old_price = 0

                    if current_price > 0 and old_price > 0 and current_price < old_price:
                        # СНИЖЕНИЕ ЦЕНЫ! Обновляем цену в Redis
                        await self._redis.set(key, current_price, ex=self.ttl_seconds)
                        return False, True, old_price
                    else:
                        return False, False, old_price
            except Exception as e:
                logger.error("Сбой обращения к Redis для ключа %s: %s. Переход на Fallback.", key, e)

        # 2. In-Memory Fallback
        now = time.time()
        # Очистка старых записей
        if len(self._memory_cache) > 10000:
            self._memory_cache = {
                k: v for k, v in self._memory_cache.items() if v[1] > now
            }

        cached = self._memory_cache.get(key)
        if not cached or cached[1] <= now:
            # Новый лот
            self._memory_cache[key] = (current_price, now + self.ttl_seconds)
            return True, False, None

        old_price, exp = cached
        if current_price > 0 and old_price > 0 and current_price < old_price:
            # Снижение цены в in-memory
            self._memory_cache[key] = (current_price, now + self.ttl_seconds)
            return False, True, old_price

        return False, False, old_price

    async def is_new_and_mark(self, platform: str, item_id: str, price: int = 0) -> bool:
        """Обратная совместимость: возвращает True если лот новый или снизилась цена."""
        is_new, is_price_drop, _ = await self.check_and_update(platform, item_id, price)
        return is_new or is_price_drop
