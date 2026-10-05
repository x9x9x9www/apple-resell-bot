from __future__ import annotations

import asyncio
import json
import re
import html
from datetime import datetime, timezone
import logging
from typing import List, Optional, Any

from core.models import RawItem, Platform
from core.deduplicator import RedisDeduplicator
from core.parser import parse_marketplace_datetime
from parsers.base import BaseWorker
from parsers.network import StealthHttpClient
from config import settings

logger = logging.getLogger(__name__)


class YoulaWorker(BaseWorker):
    """
    Модульный воркер мониторинга свежих объявлений на Юле (Youla).
    Использует внутренний API выдачи с сортировкой sort_field=date (сначала новые).
    Запрашивает строго 1 страницу (первые 10–20 карточек).
    """

    def __init__(
        self,
        queue: asyncio.Queue[RawItem],
        deduplicator: RedisDeduplicator,
        http_client: StealthHttpClient,
        city_id: Optional[str] = None,
        poll_interval: Optional[float] = None,
        max_item_age_seconds: Optional[int] = None,
        stream_manager: Optional[Any] = None,
    ):
        super().__init__(
            platform=Platform.YOULA,
            queue=queue,
            deduplicator=deduplicator,
            http_client=http_client,
            poll_interval=poll_interval or settings.YOULA_POLL_INTERVAL_SEC,
            max_item_age_seconds=max_item_age_seconds or settings.MAX_ITEM_AGE_SECONDS,
        )
        self.stream_manager = stream_manager
        self.city_id = city_id or settings.YOULA_CITY_ID
        self.city_slug = "moskva"
        self.city_name = "Москва"
        self.graphql_url = "https://api-gw.youla.io/federation/graphql"
        self.rest_url = "https://api.youla.io/api/v1/products"
        self.queries = ["iPhone", "MacBook", "Samsung Galaxy", "Google Pixel", "iPad", "PlayStation"]
        self._query_idx = 0

    def add_custom_query(self, query: str) -> None:
        """Добавляет новый пользовательский поисковый запрос (бренд или модель)."""
        q_clean = query.strip()
        if not q_clean:
            return
        if any(q.lower() == q_clean.lower() for q in self.queries):
            return
        self.queries.append(q_clean)
        logger.info("[Юла] Добавлен кастомный поисковый запрос: '%s'", q_clean)

    def set_location(self, city_id: str, city_slug: str = "moskva", city_name: Optional[str] = None) -> None:
        """Динамическое переключение региона поиска Юлы."""
        self.city_id = city_id
        self.city_slug = city_slug
        if city_name:
            self.city_name = city_name
        logger.info("[Юла] Регион поиска переключен на city_id: %s, slug: %s, city: %s", city_id, city_slug, self.city_name)

    async def _fetch_via_graphql(self) -> List[RawItem]:
        """Запрос через GraphQL эндпоинт federation API (схема 2026: feed(input: SearchFilter!, after: Cursor!))."""
        q_text = self.queries[self._query_idx % len(self.queries)]
        self._query_idx += 1

        query_payload = {
            "operationName": "feedProducts",
            "variables": {
                "input": {
                    "search": q_text,
                    "sort": "DATE_PUBLISHED_DESC",
                    "location": {"city": self.city_id},
                },
                "after": "",
            },
            "query": """
            query feedProducts($input: SearchFilter!, $after: Cursor!) {
              feed(input: $input, after: $after) {
                items {
                  ... on ProductItem {
                    product {
                      id
                      name
                      description
                      url
                      datePublished
                      images { url }
                      price { realPrice { price } }
                    }
                  }
                }
              }
            }
            """,
        }

        headers = {
            "Origin": "https://youla.ru",
            "Referer": f"https://youla.ru/{self.city_slug}",
            "X-App-Id": "web/3",
        }

        data = await self.http_client.post(
            url=self.graphql_url,
            json_data=query_payload,
            headers=headers,
        )

        if not data or not isinstance(data, dict):
            return []

        errors = data.get("errors")
        if errors:
            logger.warning("[Юла] GraphQL вернул ошибки: %s", str(errors[0].get("message", ""))[:200])

        feed_items = data.get("data", {}).get("feed", {}).get("items", []) or []
        raw_items: List[RawItem] = []
        for it in feed_items:
            try:
                # Рекламные/промо карточки не содержат product — пропускаем
                product = (it or {}).get("product") or {}
                item_id = str(product.get("id") or "")
                if not item_id:
                    continue

                title = product.get("name") or ""
                if not title:
                    continue

                description = product.get("description") or ""

                # Цена в GraphQL всегда приходит в копейках (x100)
                price_val = ((product.get("price") or {}).get("realPrice") or {}).get("price") or 0
                price = int(price_val) // 100 if price_val else 0

                # datePublished — Unix-секунды (int или строка цифр)
                ts = product.get("datePublished")
                if isinstance(ts, str) and ts.isdigit():
                    ts = int(ts)
                if not isinstance(ts, (int, float)) or ts <= 0:
                    continue
                published_at = datetime.fromtimestamp(ts, tz=timezone.utc)

                url_path = product.get("url") or f"/p/{item_id}"
                url = url_path if url_path.startswith("http") else f"https://youla.ru{url_path}"

                # Строгий региональный фильтр по slug из URL (защита от устаревших city_id)
                if self.city_slug not in ("rossiya", "all_russia"):
                    slug_match = re.match(r"^/([^/]+)/", url_path)
                    if slug_match and slug_match.group(1).lower() != self.city_slug:
                        logger.debug("[Юла] GraphQL: отсев чужого региона %s (активен %s)", slug_match.group(1), self.city_slug)
                        continue

                image_url = None
                images = product.get("images") or []
                if images and isinstance(images[0], dict):
                    image_url = images[0].get("url")

                raw_items.append(
                    RawItem(
                        platform=Platform.YOULA,
                        item_id=item_id,
                        title=title,
                        description=description,
                        price=price,
                        url=url,
                        location=self.city_name,
                        published_at=published_at,
                        image_url=image_url,
                        raw_payload=product,
                    )
                )
            except Exception as e:
                logger.debug("Ошибка разбора GraphQL карточки Юлы: %s", e)
                continue

        return raw_items

    async def _fetch_via_rest(self) -> List[RawItem]:
        """Резервный запрос через REST API выдачи."""
        q_text = self.queries[self._query_idx % len(self.queries)]
        params = {
            "sort_field": "date",
            "sort_order": "desc",
            "q": q_text,
            "city": self.city_id,
            "limit": "20",
        }
        headers = {
            "Referer": f"https://youla.ru/{self.city_slug}?q={q_text}&sort_field=date",
        }

        data = await self.http_client.get(
            url=self.rest_url,
            params=params,
            headers=headers,
        )

        if not data or not isinstance(data, dict):
            return []

        items_list = data.get("data", []) or data.get("items", [])
        return self._parse_items_list(items_list)

    def _parse_items_list(self, items: list[dict[str, Any]]) -> List[RawItem]:
        raw_items: List[RawItem] = []
        now = datetime.now(timezone.utc)

        for it in items:
            try:
                item_id = str(it.get("id") or "")
                if not item_id:
                    continue

                title = it.get("name") or it.get("title") or ""
                description = it.get("description") or ""

                # Цена (в Юле бывает как в копейках, так и в рублях)
                price_obj = it.get("price")
                price = 0
                if isinstance(price_obj, dict):
                    price = price_obj.get("realPrice") or price_obj.get("price") or 0
                elif isinstance(price_obj, (int, float)):
                    price = price_obj

                # Если цена пришла в копейках (>100_000_000 или типичный формат Юлы x100)
                if price > 20_000_000:
                    price = price // 100
                price = int(price)

                # Дата создания / публикации
                created_ts = it.get("datePublished") or it.get("dateCreated") or it.get("date_created")
                published_at = parse_marketplace_datetime(created_ts)
                if not published_at:
                    # Без подтвержденной даты пропускаем
                    continue

                # Ссылка
                slug_or_url = it.get("url") or f"/p/{item_id}"
                if not slug_or_url.startswith("http"):
                    url = f"https://youla.ru{slug_or_url}"
                else:
                    url = slug_or_url

                # Локация
                loc_obj = it.get("location") or {}
                location = self.city_name
                if isinstance(loc_obj, dict):
                    location = loc_obj.get("description") or loc_obj.get("city_name") or self.city_name
                elif isinstance(loc_obj, str) and loc_obj.strip():
                    location = loc_obj.strip()

                # Фотография
                image_url = None
                images = it.get("images") or it.get("gallery") or []
                if isinstance(images, list) and images:
                    first_img = images[0]
                    if isinstance(first_img, dict):
                        image_url = first_img.get("url") or first_img.get("big") or first_img.get("preview")
                    elif isinstance(first_img, str):
                        image_url = first_img
                elif isinstance(it.get("image"), str):
                    image_url = it.get("image")
                elif isinstance(it.get("photo"), str):
                    image_url = it.get("photo")

                raw_items.append(
                    RawItem(
                        platform=Platform.YOULA,
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
                logger.debug("Ошибка разбора карточки Юлы: %s", e)
                continue

        return raw_items

    async def _fetch_via_web_api(self) -> List[RawItem]:
        """Парсинг выдачи через web-api Юлы со строгой валидацией времени публикации."""
        q_text = self.queries[self._query_idx % len(self.queries)]
        self._query_idx += 1

        params = {
            "q": q_text,
            "sort_field": "date",
            "sort_order": "desc",
        }

        headers = {
            "Referer": f"https://youla.ru/{self.city_slug}?q={q_text}&sort_field=date",
        }
        if self.city_slug and self.city_slug != "rossiya":
            import urllib.parse
            loc_cookie = urllib.parse.quote(json.dumps({"citySlug": self.city_slug}))
            headers["Cookie"] = f"location={loc_cookie}"

        data = await self.http_client.get(
            url="https://youla.ru/web-api/products",
            params=params,
            headers=headers,
        )
        if not data or not isinstance(data, dict):
            return []

        raw_html = data.get("html", "")
        if not raw_html:
            return []

        item_matches = re.finditer(
            r'<li(?P<header>[^>]*)>(?P<content>.*?)</li>',
            raw_html,
            re.DOTALL,
        )

        raw_items: List[RawItem] = []

        for m in item_matches:
            try:
                header = m.group("header")
                content = m.group("content")

                id_match = re.search(r'data-id=\"([^\"]+)\"', header)
                if not id_match:
                    continue
                item_id = id_match.group(1)

                # 1. Отсекаем проплаченные рекомендации и поднятые лоты (isPaidAd / fast-sell)
                full_tag = header + " " + content
                is_paid = "isPaidAd" in full_tag or "product_item--promoted" in full_tag or "fast-sell" in full_tag
                if is_paid:
                    continue

                # 2. Извлечение заголовка и ссылки
                link_match = re.search(r'<a[^>]*href=\"(?P<url>[^\"]+)\"[^>]*title=\"(?P<title>[^\"]+)\"', content)
                if not link_match:
                    continue
                title = link_match.group("title").strip()
                url_path = link_match.group("url")
                url = f"https://youla.ru{url_path}" if not url_path.startswith("http") else url_path

                # Проверка и отсев чужих регионов по slug из URL (например, /moskva/... при активном ekaterinburg)
                item_city_slug = ""
                slug_match = re.match(r"^/([^/]+)/", url_path)
                if slug_match:
                    item_city_slug = slug_match.group(1).lower()

                if self.city_slug not in ("rossiya", "all_russia"):
                    if item_city_slug and item_city_slug != self.city_slug:
                        continue

                # Извлечение города: из заголовка ("в Екатеринбурге") или slug
                loc_match = re.search(r'\s+в\s+([А-Яа-яЁёA-Za-z\s-]+)$', title)
                if loc_match:
                    location = loc_match.group(1).strip()
                elif item_city_slug:
                    location = item_city_slug
                else:
                    location = self.city_name

                # 3. Извлечение цены из data-discount
                price_match = re.search(r'data-discount=\"([^\"]+)\"', header)
                price = 0
                if price_match:
                    d_raw = html.unescape(price_match.group(1))
                    d_json = json.loads(d_raw)
                    price_val = d_json.get("price_after_discount") or d_json.get("price") or 0
                    price = int(price_val) // 100 if price_val > 100000 else int(price_val)

                # 4. Высокоточный парсинг РЕАЛЬНОЙ даты публикации (отсекаем "позавчера", "вчера", старые числа)
                date_match = re.search(
                    r'<span[^>]*class=\"(?:hidden-xs|visible-xs)[^\"]*\"[^>]*>([^<]*(?:сегодня|вчера|позавчера|\d+\.\d+\.\d+|\d+\s*минут|\d+\s*час)[^<]*)</span>',
                    content,
                    re.IGNORECASE,
                )
                raw_date_str = date_match.group(1).strip() if date_match else None
                published_at = parse_marketplace_datetime(raw_date_str)

                # Если дата не указана или не распарсилась — СТРОГО отсекаем лот
                if not published_at:
                    continue

                # 5. Извлечение фотографии
                img_match = re.search(
                    r'(?:xlink:href|src|data-src)=\"([^\"]*(?:youla\.io|image|photo|img|static)[^\"]*)\"',
                    content,
                    re.IGNORECASE,
                )
                if not img_match:
                    img_match = re.search(r'(?:xlink:href|src|data-src)=\"(https://[^\"]+)\"', content)
                image_url = img_match.group(1) if img_match else None

                raw_items.append(
                    RawItem(
                        platform=Platform.YOULA,
                        item_id=item_id,
                        title=title,
                        description="",
                        price=price,
                        url=url,
                        location=location,
                        published_at=published_at,
                        image_url=image_url,
                    )
                )
            except Exception:
                continue

        return raw_items

    async def fetch_fresh_items(self) -> List[RawItem]:
        """Сбор свежих объявлений с Юлы."""
        items = await self._fetch_via_web_api()
        if not items:
            items = await self._fetch_via_graphql()
        if not items:
            items = await self._fetch_via_rest()
        return items
