from __future__ import annotations

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Optional

from core.models import RawItem, Platform
from core.deduplicator import RedisDeduplicator
from parsers.network import StealthHttpClient
from config import settings

logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    """
    Базовый асинхронный воркер мониторинга с поддержкой Zero-Latency конвейера.
    Опрашивает только первую страницу выдачи (самые свежие лоты).
    """

    def __init__(
        self,
        platform: Platform,
        queue: asyncio.Queue[RawItem],
        deduplicator: RedisDeduplicator,
        http_client: StealthHttpClient,
        poll_interval: float = 3.0,
        max_item_age_seconds: int = 300,
    ):
        self.platform = platform
        self.queue = queue
        self.deduplicator = deduplicator
        self.http_client = http_client
        self.poll_interval = poll_interval
        self.max_item_age_seconds = max_item_age_seconds
        self.is_running = False

    @abstractmethod
    async def fetch_fresh_items(self) -> List[RawItem]:
        """
        Запрашивает первую страницу (10-20 карточек) с сортировкой 'по дате/свежие'.
        Возвращает список сырых объектов RawItem.
        """
        raise NotImplementedError

    def is_fresh(self, published_at: Optional[datetime]) -> bool:
        """
        Проверяет, опубликовано ли объявление в пределах допустимого окна свежести.
        Если дата неизвестна (None) или старше max_item_age_seconds — объявление отклоняется.
        """
        if published_at is None:
            return False

        now = datetime.now(timezone.utc)
        if published_at.tzinfo is None:
            pub_utc = published_at.replace(tzinfo=timezone.utc)
        else:
            pub_utc = published_at.astimezone(timezone.utc)

        age = (now - pub_utc).total_seconds()
        # Допустимы только объявления от -30с (погрешность часов) до max_item_age_seconds
        return -30 <= age <= self.max_item_age_seconds

    async def run(self) -> None:
        """Основной цикл фонового мониторинга."""
        self.is_running = True
        logger.info(
            "Воркер [%s] запущен. Интервал: %.1fс, Окно свежести: %dс.",
            self.platform.value,
            self.poll_interval,
            self.max_item_age_seconds,
        )

        while self.is_running:
            try:
                items = await self.fetch_fresh_items()

                for item in items:
                    # 1. Проверка времени публикации («Только что появилось»)
                    if not self.is_fresh(item.published_at):
                        continue

                    # 2. Мгновенная атомарная проверка и сохранение в Redis + Детекция снижения цены
                    is_new, is_price_drop, old_price = await self.deduplicator.check_and_update(
                        platform=self.platform.value,
                        item_id=item.item_id,
                        current_price=item.price,
                    )

                    # 3. Если лот новый ИЛИ снизилась цена — передаем в конвейер отправки
                    if is_new or is_price_drop:
                        item.is_price_drop = is_price_drop
                        item.old_price = old_price
                        tag = "📉 СНИЖЕНИЕ ЦЕНЫ" if is_price_drop else "⚡️ СВЕЖИЙ ЛОТ"
                        logger.info(
                            "[%s] %s #%s: '%s' за %d ₽ (было: %s)",
                            self.platform.value,
                            tag,
                            item.item_id,
                            item.title,
                            item.price,
                            f"{old_price} ₽" if old_price else "—",
                        )
                        await self.queue.put(item)

            except asyncio.CancelledError:
                logger.info("Воркер [%s] остановлен по сигналу отмены.", self.platform.value)
                break
            except Exception as e:
                logger.error("Ошибка в цикле воркера [%s]: %s", self.platform.value, e, exc_info=True)

            # Рандомизация интервала (jitter) для имитации поведения реального пользователя
            jitter = random.uniform(0.95, 1.25)
            await asyncio.sleep(self.poll_interval * jitter)

    def stop(self) -> None:
        self.is_running = False
