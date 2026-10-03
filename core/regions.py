from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Callable
from config import settings

logger = logging.getLogger(__name__)

POPULAR_REGIONS: list[tuple[str, str]] = [
    ("moskva", "Москва и МО"),
    ("spb", "Санкт-Петербург и ЛО"),
    ("krasnodar", "Краснодар"),
    ("ekaterinburg", "Екатеринбург"),
    ("kazan", "Казань"),
    ("novosibirsk", "Новосибирск"),
    ("rostov", "Ростов-на-Дону"),
    ("nn", "Нижний Новгород"),
    ("samara", "Самара"),
    ("sochi", "Сочи"),
    ("ufa", "Уфа"),
    ("voronezh", "Воронеж"),
    ("all_russia", "🇷🇺 Вся Россия"),
]

CITY_DATABASE: dict[str, dict[str, str]] = {
    "moskva": {"name": "Москва", "avito_id": "637640", "youla_id": "576d06124994ee94589d8194", "youla_slug": "moskva"},
    "spb": {"name": "Санкт-Петербург", "avito_id": "653240", "youla_id": "576d06124994ee94589d8195", "youla_slug": "sankt-peterburg"},
    "krasnodar": {"name": "Краснодар", "avito_id": "635290", "youla_id": "576d06134994ee94589d81a4", "youla_slug": "krasnodar"},
    "ekaterinburg": {"name": "Екатеринбург", "avito_id": "652000", "youla_id": "576d06124994ee94589d8198", "youla_slug": "ekaterinburg"},
    "kazan": {"name": "Казань", "avito_id": "632660", "youla_id": "576d06134994ee94589d81a0", "youla_slug": "kazan"},
    "novosibirsk": {"name": "Новосибирск", "avito_id": "645470", "youla_id": "576d06124994ee94589d8196", "youla_slug": "novosibirsk"},
    "rostov": {"name": "Ростов-на-Дону", "avito_id": "649930", "youla_id": "576d06134994ee94589d81a2", "youla_slug": "rostov-na-donu"},
    "nn": {"name": "Нижний Новгород", "avito_id": "642460", "youla_id": "576d06124994ee94589d8197", "youla_slug": "nizhniy-novgorod"},
    "samara": {"name": "Самара", "avito_id": "651080", "youla_id": "576d06134994ee94589d8199", "youla_slug": "samara"},
    "sochi": {"name": "Сочи", "avito_id": "635840", "youla_id": "576d06134994ee94589d81af", "youla_slug": "sochi"},
    "ufa": {"name": "Уфа", "avito_id": "623950", "youla_id": "576d06134994ee94589d81a1", "youla_slug": "ufa"},
    "voronezh": {"name": "Воронеж", "avito_id": "628860", "youla_id": "576d06134994ee94589d81a6", "youla_slug": "voronezh"},
    "chelyabinsk": {"name": "Челябинск", "avito_id": "657410", "youla_id": "576d06124994ee94589d819b", "youla_slug": "chelyabinsk"},
    "krasnoyarsk": {"name": "Красноярск", "avito_id": "636400", "youla_id": "576d06134994ee94589d81a3", "youla_slug": "krasnoyarsk"},
    "perm": {"name": "Пермь", "avito_id": "647000", "youla_id": "576d06134994ee94589d81a5", "youla_slug": "perm"},
    "volgograd": {"name": "Волгоград", "avito_id": "627340", "youla_id": "576d06134994ee94589d81a7", "youla_slug": "volgograd"},
    "saratov": {"name": "Саратов", "avito_id": "651870", "youla_id": "576d06134994ee94589d81a8", "youla_slug": "saratov"},
    "tyumen": {"name": "Тюмень", "avito_id": "655930", "youla_id": "576d06134994ee94589d81a9", "youla_slug": "tyumen"},
    "tolyatti": {"name": "Тольятти", "avito_id": "651470", "youla_id": "576d06134994ee94589d81aa", "youla_slug": "tolyatti"},
    "izhevsk": {"name": "Ижевск", "avito_id": "654520", "youla_id": "576d06134994ee94589d81ab", "youla_slug": "izhevsk"},
    "barnaul": {"name": "Барнаул", "avito_id": "621860", "youla_id": "576d06134994ee94589d81ac", "youla_slug": "barnaul"},
    "irkutsk": {"name": "Иркутск", "avito_id": "631620", "youla_id": "576d06134994ee94589d81ae", "youla_slug": "irkutsk"},
    "khabarovsk": {"name": "Хабаровск", "avito_id": "656640", "youla_id": "576d06134994ee94589d81b0", "youla_slug": "khabarovsk"},
    "yaroslavl": {"name": "Ярославль", "avito_id": "660230", "youla_id": "576d06134994ee94589d81b1", "youla_slug": "yaroslavl"},
    "vladivostok": {"name": "Владивосток", "avito_id": "648140", "youla_id": "576d06134994ee94589d81b2", "youla_slug": "vladivostok"},
    "tomsk": {"name": "Томск", "avito_id": "655290", "youla_id": "576d06134994ee94589d81b4", "youla_slug": "tomsk"},
    "orenburg": {"name": "Оренбург", "avito_id": "646090", "youla_id": "576d06134994ee94589d81b5", "youla_slug": "orenburg"},
    "kemerovo": {"name": "Кемерово", "avito_id": "633460", "youla_id": "576d06134994ee94589d81b6", "youla_slug": "kemerovo"},
    "ryazan": {"name": "Рязань", "avito_id": "650630", "youla_id": "576d06134994ee94589d81b8", "youla_slug": "ryazan"},
    "naberezhnye_chelny": {"name": "Набережные Челны", "avito_id": "632890", "youla_id": "576d06134994ee94589d81b9", "youla_slug": "naberezhnye-chelny"},
    "astrakhan": {"name": "Астрахань", "avito_id": "623340", "youla_id": "576d06134994ee94589d81ba", "youla_slug": "astrakhan"},
    "penza": {"name": "Пенза", "avito_id": "646690", "youla_id": "576d06134994ee94589d81bb", "youla_slug": "penza"},
    "kirov": {"name": "Киров", "avito_id": "634030", "youla_id": "576d06134994ee94589d81bc", "youla_slug": "kirov"},
    "lipetsk": {"name": "Липецк", "avito_id": "637040", "youla_id": "576d06134994ee94589d81bd", "youla_slug": "lipetsk"},
    "cheboksary": {"name": "Чебоксары", "avito_id": "658930", "youla_id": "576d06134994ee94589d81be", "youla_slug": "cheboksary"},
    "kaliningrad": {"name": "Калининград", "avito_id": "633030", "youla_id": "576d06134994ee94589d81bf", "youla_slug": "kaliningrad"},
    "tula": {"name": "Тула", "avito_id": "655680", "youla_id": "576d06134994ee94589d81c0", "youla_slug": "tula"},
    "kursk": {"name": "Курск", "avito_id": "636730", "youla_id": "576d06134994ee94589d81c1", "youla_slug": "kursk"},
    "stavropol": {"name": "Ставрополь", "avito_id": "653990", "youla_id": "576d06134994ee94589d81c2", "youla_slug": "stavropol"},
    "ulyanovsk": {"name": "Ульяновск", "avito_id": "656240", "youla_id": "576d06134994ee94589d81ad", "youla_slug": "ulyanovsk"},
    "tver": {"name": "Тверь", "avito_id": "654920", "youla_id": "576d06134994ee94589d81c4", "youla_slug": "tver"},
    "magnitogorsk": {"name": "Магнитогорск", "avito_id": "657660", "youla_id": "576d06134994ee94589d81c5", "youla_slug": "magnitogorsk"},
    "ivanovo": {"name": "Иваново", "avito_id": "630800", "youla_id": "576d06134994ee94589d81c6", "youla_slug": "ivanovo"},
    "bryansk": {"name": "Брянск", "avito_id": "624410", "youla_id": "576d06134994ee94589d81c7", "youla_slug": "bryansk"},
    "belgorod": {"name": "Белгород", "avito_id": "624140", "youla_id": "576d06134994ee94589d81c8", "youla_slug": "belgorod"},
    "surgut": {"name": "Сургут", "avito_id": "658090", "youla_id": "576d06134994ee94589d81c9", "youla_slug": "surgut"},
    "vladimir": {"name": "Владимир", "avito_id": "626780", "youla_id": "576d06134994ee94589d81ca", "youla_slug": "vladimir"},
    "all_russia": {"name": "Вся Россия", "avito_id": "621540", "youla_id": "", "youla_slug": "rossiya"},
}

# Пользовательские синонимы для быстрого распознавания
CITY_ALIASES: dict[str, str] = {
    "мск": "moskva",
    "москва": "moskva",
    "мо": "moskva",
    "московская": "moskva",
    "спб": "spb",
    "питер": "spb",
    "петербург": "spb",
    "санкт-петербург": "spb",
    "санкт петербург": "spb",
    "ленинград": "spb",
    "екб": "ekaterinburg",
    "екатеринбург": "ekaterinburg",
    "нн": "nn",
    "нижний": "nn",
    "нижний новгород": "nn",
    "ростов": "rostov",
    "ростов-на-дону": "rostov",
    "ростов на дону": "rostov",
    "рнд": "rostov",
    "краснодар": "krasnodar",
    "крд": "krasnodar",
    "новосиб": "novosibirsk",
    "новосибирск": "novosibirsk",
    "россия": "all_russia",
    "вся россия": "all_russia",
    "рф": "all_russia",
}


class RegionManager:
    """
    Менеджер переключения региона поиска на Авито и Юле.
    Позволяет изменять целевой город прямо через интерфейс Telegram-бота.
    """

    def __init__(self, config_file: Optional[Path | str] = None):
        self.config_file = Path(config_file) if config_file else (settings.BASE_DIR / "region_settings.json")
        self._listeners: list[Callable[[dict[str, str]], None]] = []
        self._current_region: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        """Загрузка сохраненного региона из файла или fallback на .env."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "name" in data and "avito_id" in data:
                        return data
            except Exception as e:
                logger.warning("Не удалось прочитать %s: %s", self.config_file, e)

        # Дефолт из настроек (Москва)
        return {
            "key": "moskva",
            "name": "Москва",
            "avito_id": settings.AVITO_LOCATION_ID,
            "youla_id": settings.YOULA_CITY_ID,
            "youla_slug": "moskva",
        }

    def _save(self) -> None:
        """Сохранение региона на диск."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._current_region, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("Ошибка сохранения региона в %s: %s", self.config_file, e)

    @property
    def current(self) -> dict[str, str]:
        """Текущий активный регион."""
        return self._current_region

    def add_listener(self, callback: Callable[[dict[str, str]], None]) -> None:
        """Регистрация слушателя (например, воркера) для мгновенного обновления локации."""
        self._listeners.append(callback)

    def set_region(self, city_key_or_name: str) -> Optional[dict[str, str]]:
        """
        Устанавливает новый регион поиска по ключу или названию.
        Мгновенно уведомляет всех зарегистрированных воркеров.
        """
        normalized_query = city_key_or_name.lower().strip()

        # 1. Проверка по алиасам (мск, спб, питер...)
        if normalized_query in CITY_ALIASES:
            key = CITY_ALIASES[normalized_query]
            city_data = CITY_DATABASE[key]
        # 2. Прямой ключ
        elif normalized_query in CITY_DATABASE:
            key = normalized_query
            city_data = CITY_DATABASE[key]
        else:
            # 3. Поиск по имени города
            matches = self.find_cities(normalized_query)
            if not matches:
                return None
            key, city_data = matches[0]

        self._current_region = {
            "key": key,
            "name": city_data["name"],
            "avito_id": city_data["avito_id"],
            "youla_id": city_data["youla_id"],
            "youla_slug": city_data.get("youla_slug", "moskva"),
        }
        self._save()

        # Уведомляем воркеры
        for listener in self._listeners:
            try:
                listener(self._current_region)
            except Exception as e:
                logger.error("Ошибка уведомления слушателя региона: %s", e)

        logger.info("Регион поиска успешно изменен на: %s", self._current_region["name"])
        return self._current_region

    def find_cities(self, query: str) -> list[tuple[str, dict[str, str]]]:
        """Поиск городов по частичному совпадению названия."""
        q = query.lower().strip()
        if not q:
            return []

        # Сначала проверяем точное совпадение алиаса
        if q in CITY_ALIASES:
            key = CITY_ALIASES[q]
            return [(key, CITY_DATABASE[key])]

        results: list[tuple[str, dict[str, str]]] = []
        for key, data in CITY_DATABASE.items():
            name = data["name"].lower()
            if q == name or name.startswith(q) or q in name:
                results.append((key, data))

        return results
