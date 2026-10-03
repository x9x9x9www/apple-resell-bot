from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import logging
import re
from typing import List, Optional, Any

from core.models import RawItem, Platform
from core.deduplicator import RedisDeduplicator
from core.parser import parse_marketplace_datetime
from parsers.base import BaseWorker
from parsers.network import StealthHttpClient
from config import settings

logger = logging.getLogger(__name__)


class AvitoWorker(BaseWorker):
    """
    Модульный воркер мониторинга свежих объявлений на Авито.
    Использует внутренний/мобильный эндпоинт с сортировкой sort=104 (по дате / самые свежие).
    Запрашивает строго 1 страницу (первые 10–20 карточек).
    """

    def __init__(
        self,
        queue: asyncio.Queue[RawItem],
        deduplicator: RedisDeduplicator,
        http_client: StealthHttpClient,
        location_id: Optional[str] = None,
        poll_interval: Optional[float] = None,
        max_item_age_seconds: Optional[int] = None,
    ):
        super().__init__(
            platform=Platform.AVITO,
            queue=queue,
            deduplicator=deduplicator,
            http_client=http_client,
            poll_interval=poll_interval or settings.AVITO_POLL_INTERVAL_SEC,
            max_item_age_seconds=max_item_age_seconds or settings.MAX_ITEM_AGE_SECONDS,
        )
        self.location_id = location_id or settings.AVITO_LOCATION_ID
        self.city_name: str = "Москва"
        # Внутренний эндпоинт выдачи Авито
        self.api_url = "https://www.avito.ru/api/9/items"
        self.queries = [
            ("84", "iPhone"),
            ("99", "MacBook"),
            ("84", "Samsung Galaxy"),
            ("84", "Google Pixel"),
            ("96", "iPad"),
            ("97", "PlayStation"),
        ]
        self._query_idx = 0

    def set_location(self, location_id: str, city_name: Optional[str] = None) -> None:
        """Динамическое переключение региона поиска Авито."""
        self.location_id = location_id
        if city_name:
            self.city_name = city_name
        logger.info("[Авито] Регион поиска переключен на locationId: %s (%s)", location_id, self.city_name)

    def _parse_time(self, raw_time: Any) -> Optional[datetime]:
        """
        Нормализует временную метку публикации в UTC datetime.
        Если дата старая ('вчера', 'позавчера', старое число) или неизвестна — возвращает None.
        """
        return parse_marketplace_datetime(raw_time)

    async def fetch_fresh_items(self) -> List[RawItem]:
        """Запрашивает первую страницу выдачи Авито по ротируемым категориям гаджетов."""
        cat_id, q_text = self.queries[self._query_idx % len(self.queries)]
        self._query_idx += 1

        params = {
            "categoryId": cat_id,
            "sort": "104",  # 104 = Сортировка по дате (самые свежие)
            "locationId": self.location_id,
            "q": q_text,
            "page": "1",
            "perPage": "20",
        }

        headers = {
            "Host": "www.avito.ru",
            "Referer": "https://www.avito.ru/moskva/telefony/apple-ASgBAgICAUSTAcYOtA0?s=104",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        data = await self.http_client.get(
            url=self.api_url,
            params=params,
            headers=headers,
        )

        if not data or not isinstance(data, dict):
            return []

        raw_items: List[RawItem] = []
        items_list = data.get("result", {}).get("items", []) or data.get("items", [])

        for it in items_list:
            try:
                item_id = str(it.get("id") or "")
                if not item_id:
                    continue

                title = it.get("title") or it.get("name") or ""
                description = it.get("description") or ""

                # Извлечение цены
                price = 0
                price_detailed = it.get("priceDetailed", {})
                if isinstance(price_detailed, dict):
                    price = price_detailed.get("value", 0)
                if not price:
                    price = it.get("price", 0) or 0
                price = int(price)

                # Дата
                time_val = it.get("time") or it.get("sortTimeStamp") or it.get("timeSort")
                published_at = self._parse_time(time_val)
                if not published_at:
                    continue

                # Ссылка
                url_path = it.get("urlPath") or it.get("uri_mweb") or f"/item/{item_id}"
                url = f"https://www.avito.ru{url_path}" if not url_path.startswith("http") else url_path

                # Локация
                geo = it.get("geo", {})
                location = self.city_name
                if isinstance(geo, dict):
                    location = geo.get("formattedAddress") or geo.get("geoReferences", [{}])[0].get("content") or self.city_name

                # Фотография
                image_url = None
                images = it.get("images") or it.get("gallery") or []
                if isinstance(images, list) and images:
                    first_img = images[0]
                    if isinstance(first_img, dict):
                        image_url = (
                            first_img.get("640x480")
                            or first_img.get("1280x960")
                            or first_img.get("url")
                            or (list(first_img.values())[0] if first_img else None)
                        )
                    elif isinstance(first_img, str):
                        image_url = first_img
                elif isinstance(it.get("image"), dict):
                    img_dict = it.get("image")
                    image_url = (
                        img_dict.get("640x480")
                        or img_dict.get("url")
                        or (list(img_dict.values())[0] if img_dict else None)
                    )
                elif isinstance(it.get("image"), str):
                    image_url = it.get("image")

                raw_items.append(
                    RawItem(
                        platform=Platform.AVITO,
                        item_id=item_id,
                        title=title,
                        description=description,
                        price=price,
                        url=url,
                        location=str(location),
                        published_at=published_at,
                        image_url=image_url,
                        raw_payload=it,
                    )
                )
            except Exception as e:
                logger.debug("Ошибка разбора карточки Авито: %s", e)
                continue

        return raw_items
