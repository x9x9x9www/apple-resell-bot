from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import logging
import re
from typing import List, Optional, Any, TYPE_CHECKING

from core.models import RawItem, Platform
from core.deduplicator import RedisDeduplicator
from core.parser import parse_marketplace_datetime
from parsers.base import BaseWorker
from parsers.network import StealthHttpClient
from config import settings

if TYPE_CHECKING:
    from core.link_stream import StreamManager, SearchStream

logger = logging.getLogger(__name__)


class AvitoWorker(BaseWorker):
    """
    Модульный воркер мониторинга свежих объявлений на Авито.
    Использует внутренний/мобильный эндпоинт с сортировкой sort=104 (по дате / самые свежие).
    Поддерживает как общий мониторинг каталога, так и персональные пользовательские стримы по ссылкам.
    """

    def __init__(
        self,
        queue: asyncio.Queue[RawItem],
        deduplicator: RedisDeduplicator,
        http_client: StealthHttpClient,
        location_id: Optional[str] = None,
        poll_interval: Optional[float] = None,
        max_item_age_seconds: Optional[int] = None,
        stream_manager: Optional[Any] = None,
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
        self.stream_manager = stream_manager
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

    def add_custom_query(self, query: str, cat_id: str = "") -> None:
        """Добавляет новый пользовательский поисковый запрос (бренд или модель)."""
        q_clean = query.strip()
        if not q_clean:
            return
        if any(q.lower() == q_clean.lower() for _, q in self.queries):
            return
        self.queries.append((cat_id, q_clean))
        logger.info("[Авито] Добавлен кастомный поисковый запрос: '%s'", q_clean)

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

    def _parse_items_from_json(
        self,
        data: dict,
        default_location: str = "Москва",
        target_chat_id: Optional[int] = None,
    ) -> List[RawItem]:
        """Универсальный разбор JSON выдачи Авито с обогащением рейтинга продавца, брони и промо."""
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

                # Дата публикации
                time_val = it.get("time") or it.get("sortTimeStamp") or it.get("timeSort")
                published_at = self._parse_time(time_val)
                if not published_at:
                    continue

                # Ссылка
                url_path = it.get("urlPath") or it.get("uri_mweb") or f"/item/{item_id}"
                url = f"https://www.avito.ru{url_path}" if not url_path.startswith("http") else url_path

                # Локация
                geo = it.get("geo", {})
                location = default_location
                if isinstance(geo, dict):
                    location = geo.get("formattedAddress") or geo.get("geoReferences", [{}])[0].get("content") or default_location

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

                # Промо / Продвижение
                is_promoted = bool(it.get("isPaidAd") or it.get("vip") or it.get("highlight") or it.get("xl"))

                # Бронь (Авито Доставка)
                delivery = it.get("delivery") or {}
                is_reserved = bool(
                    delivery.get("isDeliveryBlocked")
                    or delivery.get("isReserved")
                    or it.get("isReserved")
                    or "забронирован" in (title + " " + description).lower()
                )

                # Продавец и рейтинг
                seller = it.get("seller") or it.get("user") or {}
                seller_name = seller.get("name") or it.get("sellerName")
                seller_rating = None
                score_val = seller.get("score") or it.get("rating")
                if isinstance(score_val, (int, float)):
                    seller_rating = float(score_val)
                elif isinstance(score_val, str) and score_val.replace(".", "", 1).isdigit():
                    seller_rating = float(score_val)

                rev_val = seller.get("reviewsCount") or it.get("reviewsCount")
                seller_reviews_count = int(rev_val) if rev_val and str(rev_val).isdigit() else None

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
                        seller_name=seller_name,
                        seller_rating=seller_rating,
                        seller_reviews_count=seller_reviews_count,
                        is_reserved=is_reserved,
                        is_promoted=is_promoted,
                        target_chat_id=target_chat_id,
                    )
                )
            except Exception as e:
                logger.debug("Ошибка парсинга отдельной карточки Авито: %s", e)
                continue

        return raw_items

    async def _fetch_stream_items(self, stream: Any) -> List[RawItem]:
        """Запрашивает карточки по конкретной пользовательской ссылке поиска с Авито."""
        params = {
            "categoryId": stream.category_id or "84",
            "sort": "104",  # Самые свежие по дате
            "locationId": stream.location_id or self.location_id,
            "page": "1",
            "perPage": "20",
        }
        if stream.query:
            params["q"] = stream.query
        if stream.pmin:
            params["pmin"] = str(stream.pmin)
        if stream.pmax:
            params["pmax"] = str(stream.pmax)

        # Пробрасываем параметры из ссылки пользователя
        for k, v in stream.raw_params.items():
            if k not in params and k not in ("page", "perPage"):
                params[k] = str(v)

        headers = {
            "Host": "www.avito.ru",
            "Referer": stream.url,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        data = await self.http_client.get(
            url=self.api_url,
            params=params,
            headers=headers,
        )
        if not data:
            return []

        raw_items = self._parse_items_from_json(
            data,
            default_location=stream.city_name or self.city_name,
            target_chat_id=stream.chat_id,
        )

        # Фильтруем лоты правилами конкретного стрима (бронь, промо, стоп-слова, фото)
        filtered_items: List[RawItem] = []
        for it in raw_items:
            passed, reason = self.stream_manager.evaluate_item_for_stream(stream, it)
            if passed:
                filtered_items.append(it)
            else:
                logger.debug("[Стрим %s] Отклонен лот #%s: %s", stream.stream_id, it.item_id, reason)

        return filtered_items

    async def fetch_fresh_items(self) -> List[RawItem]:
        """Сбор свежих объявлений Авито: общие категории + пользовательские ссылки."""
        all_items: List[RawItem] = []

        # 1. Опрос пользовательских активных стримов (по ссылкам)
        if self.stream_manager:
            active_streams = self.stream_manager.get_all_active_streams()
            for st in active_streams:
                if st.platform == Platform.AVITO:
                    try:
                        s_items = await self._fetch_stream_items(st)
                        all_items.extend(s_items)
                    except Exception as ex:
                        logger.error("Ошибка опроса стрима Авито %s: %s", st.stream_id, ex)

        # 2. Опрос общего каталога гаджетов
        cat_id, q_text = self.queries[self._query_idx % len(self.queries)]
        self._query_idx += 1

        params = {
            "sort": "104",
            "locationId": self.location_id,
            "q": q_text,
            "page": "1",
            "perPage": "20",
        }
        if cat_id:
            params["categoryId"] = cat_id

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
        catalog_items = self._parse_items_from_json(data, default_location=self.city_name)
        all_items.extend(catalog_items)

        return all_items
