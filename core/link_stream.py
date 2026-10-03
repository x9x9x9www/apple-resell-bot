from __future__ import annotations

import base64
import json
import logging
import re
import urllib.parse
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any, Dict, List, Tuple

from config import settings
from core.models import Platform, RawItem
from core.regions import CITY_DATABASE, CITY_ALIASES

logger = logging.getLogger(__name__)

# Сопоставление популярных слагов категорий Авито с ID категорий для API
AVITO_CATEGORY_MAP: dict[str, str] = {
    "telefony": "84",
    "mobilnye_telefony": "84",
    "noutbuki": "99",
    "planshety": "96",
    "planshety_i_elektronnye_knigi": "96",
    "igry_pristavki_i_programmy": "97",
    "pristavki": "97",
    "nastolnye_kompyutery": "98",
    "audio_i_video": "32",
    "naushniki": "32",
    "fototehnika": "105",
    "tovary_dlya_kompyutera": "101",
    "bytovaya_tehnika": "21",
    "chasy": "69",
    "elektronika": "84",
}

AVITO_CATEGORY_TITLES: dict[str, str] = {
    "telefony": "Телефоны",
    "mobilnye_telefony": "Телефоны",
    "noutbuki": "Ноутбуки",
    "planshety": "Планшеты",
    "planshety_i_elektronnye_knigi": "Планшеты",
    "igry_pristavki_i_programmy": "Приставки",
    "pristavki": "Приставки",
    "nastolnye_kompyutery": "Компьютеры",
    "audio_i_video": "Аудио и видео",
    "naushniki": "Наушники",
    "fototehnika": "Фототехника",
    "tovary_dlya_kompyutera": "Комплектующие",
    "bytovaya_tehnika": "Бытовая техника",
    "chasy": "Часы",
    "elektronika": "Электроника",
}

DEFAULT_BLACKLIST_WORDS: list[str] = [
    "копия", "реплика", "донор", "на запчасти", "заблокирован",
    "icloud", "байпас", "bypass", "пароль", "разбит экран",
    "витринный", "восстановленный", "не работает", "муляж", "обман",
]


class SearchStream:
    """Модель пользовательского стрима мониторинга по прямой ссылке с Авито/Юлы."""

    def __init__(
        self,
        stream_id: str,
        chat_id: int,
        title: str,
        url: str,
        platform: Platform = Platform.AVITO,
        city_slug: Optional[str] = None,
        city_name: Optional[str] = None,
        location_id: Optional[str] = None,
        category_id: Optional[str] = None,
        query: Optional[str] = None,
        pmin: Optional[int] = None,
        pmax: Optional[int] = None,
        raw_params: Optional[dict[str, Any]] = None,
        is_active: bool = True,
        filter_only_photo: bool = True,
        filter_only_desc: bool = False,
        filter_exclude_reserved: bool = True,
        filter_exclude_promo: bool = True,
        blacklist_words: Optional[list[str]] = None,
        whitelist_words: Optional[list[str]] = None,
        blocked_sellers: Optional[list[str]] = None,
        lots_found: int = 0,
        created_at: Optional[str] = None,
        last_checked_at: Optional[str] = None,
    ):
        self.stream_id = stream_id or str(uuid.uuid4())[:8]
        self.chat_id = chat_id
        self.title = title
        self.url = url
        self.platform = platform if isinstance(platform, Platform) else Platform(platform)
        self.city_slug = city_slug
        self.city_name = city_name or "Москва"
        self.location_id = location_id or "637640"
        self.category_id = category_id or "84"
        self.query = query
        self.pmin = pmin
        self.pmax = pmax
        self.raw_params = raw_params or {}
        self.is_active = is_active
        self.filter_only_photo = filter_only_photo
        self.filter_only_desc = filter_only_desc
        self.filter_exclude_reserved = filter_exclude_reserved
        self.filter_exclude_promo = filter_exclude_promo
        self.blacklist_words = blacklist_words if blacklist_words is not None else list(DEFAULT_BLACKLIST_WORDS)
        self.whitelist_words = whitelist_words if whitelist_words is not None else []
        self.blocked_sellers = blocked_sellers if blocked_sellers is not None else []
        self.lots_found = lots_found
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.last_checked_at = last_checked_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "stream_id": self.stream_id,
            "chat_id": self.chat_id,
            "title": self.title,
            "url": self.url,
            "platform": self.platform.value,
            "city_slug": self.city_slug,
            "city_name": self.city_name,
            "location_id": self.location_id,
            "category_id": self.category_id,
            "query": self.query,
            "pmin": self.pmin,
            "pmax": self.pmax,
            "raw_params": self.raw_params,
            "is_active": self.is_active,
            "filter_only_photo": self.filter_only_photo,
            "filter_only_desc": self.filter_only_desc,
            "filter_exclude_reserved": self.filter_exclude_reserved,
            "filter_exclude_promo": self.filter_exclude_promo,
            "blacklist_words": self.blacklist_words,
            "whitelist_words": self.whitelist_words,
            "blocked_sellers": self.blocked_sellers,
            "lots_found": self.lots_found,
            "created_at": self.created_at,
            "last_checked_at": self.last_checked_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SearchStream:
        platform = Platform.AVITO if data.get("platform") == Platform.AVITO.value else Platform.YOULA
        return cls(
            stream_id=data.get("stream_id", ""),
            chat_id=data.get("chat_id", 0),
            title=data.get("title", "Поиск"),
            url=data.get("url", ""),
            platform=platform,
            city_slug=data.get("city_slug"),
            city_name=data.get("city_name"),
            location_id=data.get("location_id"),
            category_id=data.get("category_id"),
            query=data.get("query"),
            pmin=data.get("pmin"),
            pmax=data.get("pmax"),
            raw_params=data.get("raw_params", {}),
            is_active=data.get("is_active", True),
            filter_only_photo=data.get("filter_only_photo", True),
            filter_only_desc=data.get("filter_only_desc", False),
            filter_exclude_reserved=data.get("filter_exclude_reserved", True),
            filter_exclude_promo=data.get("filter_exclude_promo", True),
            blacklist_words=data.get("blacklist_words"),
            whitelist_words=data.get("whitelist_words"),
            blocked_sellers=data.get("blocked_sellers"),
            lots_found=data.get("lots_found", 0),
            created_at=data.get("created_at"),
            last_checked_at=data.get("last_checked_at"),
        )


def extract_prices_from_query(query_params: dict[str, list[str]], clean_url: str) -> tuple[Optional[int], Optional[int]]:
    """
    Универсальное извлечение цен из всех возможных форматов Авито и Юлы:
    1. Прямые параметры (pmin, pmax, price_min, price_max, priceMin, priceMax, price_from, price_to)
    2. Параметр диапазона (price=30000-33000)
    3. Закодированный base64-фильтр Авито `f` (например, embedded JSON {"from": 30000, "to": 33000})
    4. Числовые ценовые диапазоны в URL пути (ot-30000-do-33000-rubley, do-33000-rubley)
    """
    pmin = None
    pmax = None

    # 1. Прямые параметры в строке запроса
    for k_min in ("pmin", "price_min", "priceMin", "price_from", "params[price][from]", "params[price][min]"):
        if k_min in query_params:
            try:
                pmin = int(query_params[k_min][0])
                break
            except (ValueError, IndexError):
                pass

    for k_max in ("pmax", "price_max", "priceMax", "price_to", "params[price][to]", "params[price][max]"):
        if k_max in query_params:
            try:
                pmax = int(query_params[k_max][0])
                break
            except (ValueError, IndexError):
                pass

    # 2. Параметр вида price=30000-33000
    if "price" in query_params:
        pv = query_params["price"][0]
        pm = re.match(r"^(\d+)?-(\d+)?$", pv)
        if pm:
            if pm.group(1):
                pmin = int(pm.group(1))
            if pm.group(2):
                pmax = int(pm.group(2))

    # 3. Фильтры Авито в параметре `f` (base64 Protobuf с embedded JSON)
    if (pmin is None and pmax is None) and "f" in query_params:
        f_val = query_params["f"][0]
        parts = re.split(r"[.~]", f_val)
        for p in parts:
            clean = p.replace("-", "+").replace("_", "/")
            pad = clean + "=" * (-len(clean) % 4)
            try:
                dec = base64.b64decode(pad)
                for m in re.finditer(rb"\{[^{}]*\}", dec):
                    try:
                        obj = json.loads(m.group(0).decode("utf-8"))
                        f_v = obj.get("from")
                        t_v = obj.get("to")
                        # Цены гаджетов обычно больше 100-500 руб (в отличие от процентов АКБ 50-100)
                        if (t_v and t_v > 100) or (f_v and f_v >= 500):
                            if f_v is not None:
                                pmin = int(f_v)
                            if t_v is not None:
                                pmax = int(t_v)
                    except Exception:
                        pass
            except Exception:
                pass

    # 4. Путь URL (например: /do-33000-rubley или /ot-30000-do-33000-rubley)
    if pmin is None and pmax is None:
        path_m = re.search(r"(?:ot-(\d+))?(?:-)?(?:do-(\d+))?-rubley", clean_url)
        if path_m:
            if path_m.group(1):
                pmin = int(path_m.group(1))
            if path_m.group(2):
                pmax = int(path_m.group(2))

    return pmin, pmax


def parse_search_url(raw_url: str) -> Optional[dict[str, Any]]:
    """
    Интеллектуальный разбор ссылки поиска с Авито или Юлы.
    Извлекает город, категорию, цены, поисковый запрос и параметры фильтров.
    """
    clean_url = raw_url.strip()
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url

    try:
        parsed = urllib.parse.urlparse(clean_url)
    except Exception:
        return None

    netloc = parsed.netloc.lower()
    is_avito = "avito.ru" in netloc
    is_youla = "youla.ru" in netloc

    if not (is_avito or is_youla):
        return None

    segments = [s for s in parsed.path.split("/") if s]
    query_params = urllib.parse.parse_qs(parsed.query)

    # 1. ПАРСИНГ АВИТО
    if is_avito:
        city_slug = segments[0] if len(segments) > 0 else "moskva"
        city_name = "Москва"
        location_id = "637640"

        # Сопоставляем город
        if city_slug in CITY_DATABASE:
            cdata = CITY_DATABASE[city_slug]
            city_name = cdata["name"]
            location_id = cdata["avito_id"]
        elif city_slug in CITY_ALIASES:
            ckey = CITY_ALIASES[city_slug]
            cdata = CITY_DATABASE.get(ckey, {})
            city_name = cdata.get("name", "Москва")
            location_id = cdata.get("avito_id", "637640")

        # Категория
        cat_slug = segments[1] if len(segments) > 1 else ""
        category_id = AVITO_CATEGORY_MAP.get(cat_slug, "84")

        # Цены
        pmin, pmax = extract_prices_from_query(query_params, clean_url)

        # Текст запроса
        q_text = query_params.get("q", [""])[0].strip() or None
        if not q_text and len(segments) > 2:
            last_seg = segments[-1].split("-")[0]
            if last_seg and last_seg not in AVITO_CATEGORY_MAP:
                q_text = last_seg.replace("_", " ").title()

        # Формируем плоский словарь параметров для вызова api/9/items
        raw_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        # Гарантируем сортировку по дате
        raw_params["sort"] = raw_params.get("s", "104")

        # Человекочитаемый заголовок
        cat_title = AVITO_CATEGORY_TITLES.get(cat_slug, cat_slug.replace("_", " ").capitalize() if cat_slug else "Электроника")
        price_info = ""
        if pmin and pmax:
            price_info = f" ({pmin:,}–{pmax:,} ₽)".replace(",", " ")
        elif pmax:
            price_info = f" (до {pmax:,} ₽)".replace(",", " ")
        elif pmin:
            price_info = f" (от {pmin:,} ₽)".replace(",", " ")

        q_info = f" «{q_text}»" if q_text else ""
        title = f"Авито: {cat_title}{q_info} в {city_name}{price_info}"

        return {
            "platform": Platform.AVITO,
            "title": title,
            "url": clean_url,
            "city_slug": city_slug,
            "city_name": city_name,
            "location_id": location_id,
            "category_id": category_id,
            "query": q_text,
            "pmin": pmin,
            "pmax": pmax,
            "raw_params": raw_params,
        }

    # 2. ПАРСИНГ ЮЛЫ
    else:
        city_slug = segments[0] if len(segments) > 0 else "moskva"
        city_name = "Москва"
        youla_id = "576d06124994ee94589d8194"
        found_data = None
        if city_slug in CITY_DATABASE:
            found_data = CITY_DATABASE[city_slug]
        elif city_slug in CITY_ALIASES:
            ckey = CITY_ALIASES[city_slug]
            found_data = CITY_DATABASE.get(ckey)
        else:
            for cdata in CITY_DATABASE.values():
                if cdata.get("youla_slug") == city_slug:
                    found_data = cdata
                    break

        if found_data:
            city_name = found_data["name"]
            youla_id = found_data.get("youla_id", youla_id)

        # Цены
        pmin, pmax = extract_prices_from_query(query_params, clean_url)

        q_text = query_params.get("q", [""])[0].strip() or None
        raw_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

        price_info = ""
        if pmin and pmax:
            price_info = f" ({pmin:,}–{pmax:,} ₽)".replace(",", " ")
        elif pmax:
            price_info = f" (до {pmax:,} ₽)".replace(",", " ")
        elif pmin:
            price_info = f" (от {pmin:,} ₽)".replace(",", " ")

        title = f"Юла: {q_text or 'Свежие лоты'} в {city_name}{price_info}"
        return {
            "platform": Platform.YOULA,
            "title": title,
            "url": clean_url,
            "city_slug": city_slug,
            "city_name": city_name,
            "location_id": youla_id,
            "category_id": "smartfony",
            "query": q_text,
            "pmin": pmin,
            "pmax": pmax,
            "raw_params": raw_params,
        }


class StreamManager:
    """Менеджер пользовательских стримов мониторинга по ссылкам."""

    def __init__(self, file_path: Optional[Path | str] = None):
        self.file_path = Path(file_path) if file_path else (settings.BASE_DIR / "search_streams.json")
        self._streams: dict[int, SearchStream] = {}  # chat_id -> SearchStream
        self.load()

    def load(self) -> None:
        """Загружает сохраненные стримы из файла."""
        if not self.file_path.exists():
            return
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._streams = {}
            needs_save = False
            for cid_str, sdata in data.items():
                try:
                    cid = int(cid_str)
                    stream = SearchStream.from_dict(sdata)
                    # Если у сохраненного стрима не были определены цены, пробуем обновить из url
                    if (stream.pmin is None and stream.pmax is None) and stream.url:
                        re_parsed = parse_search_url(stream.url)
                        if re_parsed and (re_parsed.get("pmin") is not None or re_parsed.get("pmax") is not None):
                            stream.pmin = re_parsed.get("pmin")
                            stream.pmax = re_parsed.get("pmax")
                            stream.title = re_parsed.get("title", stream.title)
                            needs_save = True
                    self._streams[cid] = stream
                except Exception as ex:
                    logger.debug("Ошибка разбора стрима %s: %s", cid_str, ex)
            if needs_save:
                self.save()
            logger.info("Загружено активных пользовательских стримов: %d", len(self._streams))
        except Exception as e:
            logger.error("Ошибка загрузки search_streams.json: %s", e)

    def save(self) -> None:
        """Сохраняет текущие стримы в JSON файл."""
        try:
            out = {str(cid): s.to_dict() for cid, s in self._streams.items()}
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
            logger.debug("search_streams.json успешно сохранен.")
        except Exception as e:
            logger.error("Ошибка сохранения search_streams.json: %s", e)

    def create_or_update_stream(self, chat_id: int, url: str) -> Optional[SearchStream]:
        """Создает новый или обновляет существующий стрим по ссылке."""
        parsed_data = parse_search_url(url)
        if not parsed_data:
            return None

        existing = self._streams.get(chat_id)
        if existing:
            existing.title = parsed_data["title"]
            existing.url = parsed_data["url"]
            existing.platform = parsed_data["platform"]
            existing.city_slug = parsed_data["city_slug"]
            existing.city_name = parsed_data["city_name"]
            existing.location_id = parsed_data["location_id"]
            existing.category_id = parsed_data["category_id"]
            existing.query = parsed_data["query"]
            existing.pmin = parsed_data["pmin"]
            existing.pmax = parsed_data["pmax"]
            existing.raw_params = parsed_data["raw_params"]
            existing.is_active = True
            stream = existing
        else:
            stream = SearchStream(
                stream_id=str(uuid.uuid4())[:8],
                chat_id=chat_id,
                title=parsed_data["title"],
                url=parsed_data["url"],
                platform=parsed_data["platform"],
                city_slug=parsed_data["city_slug"],
                city_name=parsed_data["city_name"],
                location_id=parsed_data["location_id"],
                category_id=parsed_data["category_id"],
                query=parsed_data["query"],
                pmin=parsed_data["pmin"],
                pmax=parsed_data["pmax"],
                raw_params=parsed_data["raw_params"],
                is_active=True,
            )
            self._streams[chat_id] = stream

        self.save()
        return stream

    def get_stream(self, chat_id: int) -> Optional[SearchStream]:
        return self._streams.get(chat_id)

    def get_all_streams(self) -> list[SearchStream]:
        return list(self._streams.values())

    def get_all_active_streams(self) -> list[SearchStream]:
        return [s for s in self._streams.values() if s.is_active]

    def toggle_active(self, chat_id: int) -> Optional[bool]:
        stream = self._streams.get(chat_id)
        if not stream:
            return None
        stream.is_active = not stream.is_active
        self.save()
        return stream.is_active

    def toggle_filter(self, chat_id: int, filter_key: str) -> Optional[bool]:
        stream = self._streams.get(chat_id)
        if not stream:
            return None
        if hasattr(stream, filter_key):
            current_val = getattr(stream, filter_key)
            new_val = not current_val
            setattr(stream, filter_key, new_val)
            self.save()
            return new_val
        return None

    def add_blacklist_word(self, chat_id: int, word: str) -> bool:
        stream = self._streams.get(chat_id)
        if not stream:
            return False
        w = word.strip().lower()
        if w and w not in stream.blacklist_words:
            stream.blacklist_words.append(w)
            self.save()
            return True
        return False

    def remove_blacklist_word(self, chat_id: int, word: str) -> bool:
        stream = self._streams.get(chat_id)
        if not stream:
            return False
        w = word.strip().lower()
        if w in stream.blacklist_words:
            stream.blacklist_words.remove(w)
            self.save()
            return True
        return False

    def delete_stream(self, chat_id: int) -> bool:
        if chat_id in self._streams:
            del self._streams[chat_id]
            self.save()
            return True
        return False

    def increment_lots_found(self, chat_id: int) -> None:
        stream = self._streams.get(chat_id)
        if stream:
            stream.lots_found += 1
            stream.last_checked_at = datetime.now(timezone.utc).isoformat()
            self.save()

    def evaluate_item_for_stream(self, stream: SearchStream, item: RawItem) -> tuple[bool, Optional[str]]:
        """
        Проверяет лот на соответствие фильтрам конкретного стрима:
        - Фото / Описание
        - Бронь (is_reserved)
        - Промо (is_promoted)
        - Черный список стоп-слов
        - Белый список обязательных слов
        - Ценовой диапазон
        """
        # 1. Фото
        if stream.filter_only_photo and not item.image_url:
            return False, "Нет фотографии"

        # 2. Описание
        if stream.filter_only_desc and not (item.description and item.description.strip()):
            return False, "Пустое описание"

        # 3. Бронь
        if stream.filter_exclude_reserved and item.is_reserved:
            return False, "Товар уже забронирован (Авито Доставка)"

        # 4. Промо / реклама
        if stream.filter_exclude_promo and item.is_promoted:
            return False, "Рекламное / продвигаемое объявление"

        # 5. Ценовые рамки
        if stream.pmax and item.price > stream.pmax:
            return False, f"Цена {item.price} ₽ выше лимита ссылки {stream.pmax} ₽"
        if stream.pmin and item.price < stream.pmin:
            return False, f"Цена {item.price} ₽ ниже минимума {stream.pmin} ₽"

        combined_text = f"{item.title} {item.description}".lower()

        # 6. Черный список стоп-слов
        for bw in stream.blacklist_words:
            if bw and bw in combined_text:
                return False, f"Стоп-слово: '{bw}'"

        # 7. Белый список слов
        if stream.whitelist_words:
            has_white = any(ww in combined_text for ww in stream.whitelist_words if ww)
            if not has_white:
                return False, "Не содержит слов из белого списка"

        return True, None
