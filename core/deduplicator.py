from __future__ import annotations

import logging
import re
import sqlite3
import time
from pathlib import Path
from typing import Optional, TYPE_CHECKING
import redis.asyncio as aioredis
from config import settings

if TYPE_CHECKING:
    from core.models import ParsedIPhone

logger = logging.getLogger(__name__)


def extract_image_key(url: Optional[str]) -> Optional[str]:
    """Извлекает уникальный хеш/имя файла фотографии из CDN Авито или Юлы."""
    if not url:
        return None
    try:
        clean = url.split("?")[0].split("#")[0].rstrip("/")
        parts = clean.split("/")
        if not parts:
            return None
        filename = parts[-1]
        name = filename.split(".")[0]
        return name if len(name) >= 6 else filename
    except Exception:
        return None


def normalize_text_fingerprint(title: str, description: str = "") -> str:
    """Нормализует заголовок и начало описания для поиска текстовых дублей."""
    combined = f"{title} {description[:80]}".lower()
    cleaned = re.sub(r"[^a-zа-я0-9]", "", combined)
    for word in ["продам", "куплю", "телефон", "смартфон", "apple", "iphone", "айфон"]:
        cleaned = cleaned.replace(word, "")
    return cleaned[:40]


def normalize_location(loc: str) -> str:
    """Извлекает нормализованное имя города."""
    if not loc:
        return "москва"
    parts = loc.lower().split(",")
    return parts[0].strip() or "москва"


class RedisDeduplicator:
    """
    Многоуровневый интеллектуальный конвейер дедупликации:
    1. L1 (In-Memory LRU): моментальная проверка в оперативной памяти (0.01 мс).
    2. L2 (Redis Cluster / Single): распределенная дедупликация между воркерами.
    3. L3 (Persistent SQLite): гарантирует сохранение истории лотов при любых перезапусках бота.
    4. Детекция семантических дублей:
       - Кросспостинг между Авито и Юлой (один и тот же товар на двух сайтах).
       - Перевыкладка продавцом (новые ID одного и того же устройства).
       - Повтор по хешу фотографий.
    5. Защита от колебаний цен: отсекает микро-изменения цены (< MIN_PRICE_DROP_RUB).
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        ttl_hours: Optional[int] = None,
        db_path: Optional[str | Path] = None,
        min_price_drop: Optional[int] = None,
        semantic_window_hours: Optional[int] = None,
    ):
        self.redis_url = redis_url or settings.REDIS_URL
        self.ttl_seconds = int((ttl_hours or settings.REDIS_TTL_HOURS) * 3600)
        self.semantic_window_seconds = int(
            (semantic_window_hours or settings.SEMANTIC_DEDUP_WINDOW_HOURS) * 3600
        )
        self.min_price_drop = (
            min_price_drop if min_price_drop is not None else settings.MIN_PRICE_DROP_RUB
        )

        # Путь к локальной SQLite базе
        if db_path is not None:
            self.db_path = str(db_path)
        else:
            self.db_path = str(settings.BASE_DIR / settings.DEDUP_DB_FILE)

        self._redis: Optional[aioredis.Redis] = None
        self._memory_cache: dict[str, tuple[int, float]] = {}  # key -> (price, expires_at)
        self._fp_cache: dict[str, float] = {}  # fp -> expires_at
        self._sqlite_conn: Optional[sqlite3.Connection] = None

    async def connect(self) -> None:
        """Инициализация SQLite постоянного хранилища и подключение к Redis."""
        # 1. Инициализация локального персистентного хранилища SQLite
        try:
            self._init_sqlite()
        except Exception as e:
            logger.error("Ошибка инициализации SQLite хранилища дедупликации: %s", e)

        # 2. Подключение к Redis (если настроен и доступен)
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
                "Redis недоступен (%s). Используется локальное постоянное хранилище SQLite (%s). Ошибка: %s",
                self.redis_url,
                self.db_path,
                e,
            )
            self._redis = None

    def _init_sqlite(self) -> None:
        """Создает таблицы и загружает актуальный кэш из SQLite."""
        self._sqlite_conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._sqlite_conn.execute("PRAGMA journal_mode=WAL;")
        self._sqlite_conn.execute("PRAGMA synchronous=NORMAL;")

        with self._sqlite_conn:
            self._sqlite_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_items (
                    key TEXT PRIMARY KEY,
                    price INTEGER,
                    expires_at REAL
                );
                """
            )
            self._sqlite_conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_seen_items_exp ON seen_items(expires_at);
                """
            )
            self._sqlite_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_fingerprints (
                    fp TEXT PRIMARY KEY,
                    item_id TEXT,
                    platform TEXT,
                    expires_at REAL
                );
                """
            )
            self._sqlite_conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_seen_fps_exp ON seen_fingerprints(expires_at);
                """
            )

            # Очистка устаревших записей
            now = time.time()
            self._sqlite_conn.execute("DELETE FROM seen_items WHERE expires_at <= ?;", (now,))
            self._sqlite_conn.execute("DELETE FROM seen_fingerprints WHERE expires_at <= ?;", (now,))

            # Прогрев быстрой памяти из SQLite
            cursor = self._sqlite_conn.execute(
                "SELECT key, price, expires_at FROM seen_items WHERE expires_at > ? LIMIT 50000;",
                (now,),
            )
            for row in cursor.fetchall():
                self._memory_cache[row[0]] = (int(row[1]), float(row[2]))

            cursor_fp = self._sqlite_conn.execute(
                "SELECT fp, expires_at FROM seen_fingerprints WHERE expires_at > ? LIMIT 50000;",
                (now,),
            )
            for row in cursor_fp.fetchall():
                self._fp_cache[row[0]] = float(row[1])

        logger.info(
            "SQLite хранилище дедупликации загружено. В памяти: %d лотов, %d отпечатков.",
            len(self._memory_cache),
            len(self._fp_cache),
        )

    async def close(self) -> None:
        """Корректное закрытие соединений."""
        if self._redis:
            await self._redis.aclose()
            self._redis = None
        if self._sqlite_conn:
            self._sqlite_conn.close()
            self._sqlite_conn = None

    def _make_key(self, platform: str, item_id: str) -> str:
        return f"resell:seen:{platform}:{item_id}"

    async def check_and_update(
        self,
        platform: str,
        item_id: str,
        current_price: int,
    ) -> tuple[bool, bool, Optional[int]]:
        """
        Проверяет лот на уникальность по ID и отслеживает СНИЖЕНИЕ ЦЕНЫ.
        Возвращает:
            (is_new, is_price_drop, old_price)
        """
        key = self._make_key(platform, item_id)
        now = time.time()
        expires_at = now + self.ttl_seconds

        # 1. Попытка через Redis
        if self._redis:
            try:
                val = await self._redis.get(key)
                if val is None:
                    # Новый лот -> фиксируем цену
                    await self._redis.set(key, current_price, ex=self.ttl_seconds)
                    self._save_item_sqlite(key, current_price, expires_at)
                    self._memory_cache[key] = (current_price, expires_at)
                    return True, False, None
                else:
                    try:
                        old_price = int(val)
                    except (ValueError, TypeError):
                        old_price = 0

                    diff = old_price - current_price
                    # Проверяем значительное снижение цены (>= min_price_drop)
                    if current_price > 0 and old_price > 0 and diff >= self.min_price_drop:
                        await self._redis.set(key, current_price, ex=self.ttl_seconds)
                        self._save_item_sqlite(key, current_price, expires_at)
                        self._memory_cache[key] = (current_price, expires_at)
                        return False, True, old_price
                    else:
                        return False, False, old_price
            except Exception as e:
                logger.error("Сбой Redis (%s). Используется локальный кэш: %s", key, e)

        # 2. Локальное хранилище (SQLite + In-Memory)
        cached = self._memory_cache.get(key)
        if not cached or cached[1] <= now:
            # Новый лот
            self._memory_cache[key] = (current_price, expires_at)
            self._save_item_sqlite(key, current_price, expires_at)
            return True, False, None

        old_price, _ = cached
        diff = old_price - current_price
        if current_price > 0 and old_price > 0 and diff >= self.min_price_drop:
            # Значимое снижение цены
            self._memory_cache[key] = (current_price, expires_at)
            self._save_item_sqlite(key, current_price, expires_at)
            return False, True, old_price

        return False, False, old_price

    def _save_item_sqlite(self, key: str, price: int, expires_at: float) -> None:
        """Синхронная быстрая запись в SQLite (в WAL-режиме занимает доли миллисекунды)."""
        if not self._sqlite_conn:
            return
        try:
            with self._sqlite_conn:
                self._sqlite_conn.execute(
                    "INSERT OR REPLACE INTO seen_items (key, price, expires_at) VALUES (?, ?, ?);",
                    (key, price, expires_at),
                )
        except Exception as e:
            logger.debug("Ошибка записи в SQLite seen_items: %s", e)

    async def check_and_mark_semantic_duplicate(
        self, item: ParsedIPhone
    ) -> tuple[bool, str]:
        """
        Умная семантическая дедупликация:
        Вычисляет хеш-отпечатки товара и отсекает:
        1. Одинаковые фото (хеш файла обложки совпадает с ранее отправленным).
        2. Кросспостинг (тот же iPhone, память, цена, АКБ и город на другой площадке).
        3. Перевыкладку и спам-шаблоны продавцов.

        Возвращает:
            (is_duplicate, reason_string)
        """
        # Если это подтвержденное снижение цены на существующий лот — пропускаем
        if item.is_price_drop:
            self._update_item_fingerprints(item)
            return False, ""

        now = time.time()
        fps_to_check: list[tuple[str, str]] = []

        # 1. Отпечаток фотографии
        photo_key = extract_image_key(item.image_url)
        if photo_key:
            fps_to_check.append(
                (f"photo:{photo_key}", "Совпадение фотографии с ранее отправленным лотом (дубликат фото)")
            )

        # 2. Отпечаток характеристик и цены (iPhone + память + цена + АКБ + город)
        city_norm = normalize_location(item.location)
        battery_str = str(item.battery_health) if item.battery_health is not None else "na"
        specs_key = f"specs:{item.model.lower().strip()}:{item.storage_gb}:{item.price}:{battery_str}:{city_norm}"
        fps_to_check.append(
            (specs_key, "Идентичные характеристики, цена и город (кросспостинг или перевыкладка)")
        )

        # 3. Отпечаток текста
        clean_text = normalize_text_fingerprint(item.title, item.description)
        if len(clean_text) >= 12:
            text_key = f"text:{item.model.lower().strip()}:{item.price}:{clean_text}"
            fps_to_check.append((text_key, "Повторяющийся шаблонный текст объявления (спам-дубликат)"))

        # Проверяем, встречался ли хоть один из отпечатков
        for fp, reason in fps_to_check:
            # Проверка в Redis
            if self._redis:
                try:
                    exists = await self._redis.get(f"resell:fp:{fp}")
                    if exists:
                        return True, reason
                except Exception:
                    pass

            # Проверка в локальной памяти
            exp = self._fp_cache.get(fp)
            if exp and exp > now:
                return True, reason

        # Если не дубликат — регистрируем все отпечатки в базе
        self._record_fingerprints(item, [fp for fp, _ in fps_to_check])
        return False, ""

    def _record_fingerprints(self, item: ParsedIPhone, fingerprints: list[str]) -> None:
        """Сохраняет отпечатки свежего лота для защиты от будущих дублей."""
        now = time.time()
        expires_at = now + self.semantic_window_seconds

        for fp in fingerprints:
            self._fp_cache[fp] = expires_at
            if self._sqlite_conn:
                try:
                    with self._sqlite_conn:
                        self._sqlite_conn.execute(
                            "INSERT OR REPLACE INTO seen_fingerprints (fp, item_id, platform, expires_at) VALUES (?, ?, ?, ?);",
                            (fp, item.item_id, item.platform.value, expires_at),
                        )
                except Exception as e:
                    logger.debug("Ошибка записи seen_fingerprints в SQLite: %s", e)

            # Сохранение в Redis (если активен)
            if self._redis:
                try:
                    import asyncio
                    asyncio.create_task(
                        self._redis.set(f"resell:fp:{fp}", item.item_id, ex=self.semantic_window_seconds)
                    )
                except Exception:
                    pass

    def _update_item_fingerprints(self, item: ParsedIPhone) -> None:
        """Обновляет отпечатки при снижении цены."""
        photo_key = extract_image_key(item.image_url)
        fps = []
        if photo_key:
            fps.append(f"photo:{photo_key}")
        city_norm = normalize_location(item.location)
        battery_str = str(item.battery_health) if item.battery_health is not None else "na"
        fps.append(f"specs:{item.model.lower().strip()}:{item.storage_gb}:{item.price}:{battery_str}:{city_norm}")
        self._record_fingerprints(item, fps)

    async def is_new_and_mark(self, platform: str, item_id: str, price: int = 0) -> bool:
        """Обратная совместимость: возвращает True если лот новый или снизилась цена."""
        is_new, is_price_drop, _ = await self.check_and_update(platform, item_id, price)
        return is_new or is_price_drop
