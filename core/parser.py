from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Any
from core.models import RawItem, ParsedIPhone, Platform


# =====================================================================
# Регулярные выражения для фильтрации мусора, копий и брака (Blacklist)
# =====================================================================

RE_REPLICAS = re.compile(
    r"\b(копи[яиеюей]|реплик[аеуои]|дубликат|1\s*:\s*1|lux|люкс|как оригинал|под оригинал|"
    r"аналог|тайвань|копия iphone|копия samsung|фейк|fake)\b",
    re.IGNORECASE,
)

RE_ACCESSORIES_AND_PARTS = re.compile(
    r"^(?:чехол|чехлы|бампер|коробк[аеуои]|коробка от|только коробка|box|стекло|защитное стекло|"
    r"аккумулятор для|дисплей для|экран для|запчасти|на запчасти|под восстановление|донор|"
    r"материнская плата|плата|корпус от|шлейф|камера для)\b|"
    r"\b(на запчасти|под восстановление|на донор|только коробка|пустая коробка|коробка оригинал|"
    r"запчасти для|не включается|после воды|утопленник|труп|плата сдохла|нет сети)\b",
    re.IGNORECASE,
)

RE_LOCKS = re.compile(
    r"\b(icloud|айклауд|заблокирован|парол[ьяе]|mdm|мдм|демо|demo|байпас|bypass|"
    r"r-?sim|р-?сим|не звонит|lost|кирпич|на замке|frp|frp lock|google lock)\b",
    re.IGNORECASE,
)

# =====================================================================
# Таблица нормализации моделей гаджетов (MacBook, Samsung, Pixel, iPad, iPhone, Consoles)
# =====================================================================

MODEL_PATTERNS: list[tuple[re.Pattern, str]] = [
    # MacBook Pro
    (re.compile(r"\b(?:macbook|макбук)\s*pro\s*16\b", re.IGNORECASE), "MacBook Pro 16"),
    (re.compile(r"\b(?:macbook|макбук)\s*pro\s*14\b", re.IGNORECASE), "MacBook Pro 14"),
    (re.compile(r"\b(?:macbook|макбук)\s*pro\s*13\b", re.IGNORECASE), "MacBook Pro 13"),
    (re.compile(r"\b(?:macbook|макбук)\s*pro\b", re.IGNORECASE), "MacBook Pro 14"),

    # MacBook Air
    (re.compile(r"\b(?:macbook|макбук)\s*air\s*15\b", re.IGNORECASE), "MacBook Air 15"),
    (re.compile(r"\b(?:macbook|макбук)\s*air\s*(?:13\s*)?(?:m3|м3)\b", re.IGNORECASE), "MacBook Air M3 13"),
    (re.compile(r"\b(?:macbook|макбук)\s*air\s*(?:13\s*)?(?:m2|м2)\b", re.IGNORECASE), "MacBook Air M2 13"),
    (re.compile(r"\b(?:macbook|макбук)\s*air\s*(?:13\s*)?(?:m1|м1)\b", re.IGNORECASE), "MacBook Air M1"),
    (re.compile(r"\b(?:macbook|макбук)\s*air\b", re.IGNORECASE), "MacBook Air M1"),

    # Samsung Galaxy S24
    (re.compile(r"\b(?:samsung|galaxy|самсунг)?\s*(?:s|с)\s*24\s*ultra\b", re.IGNORECASE), "Samsung Galaxy S24 Ultra"),
    (re.compile(r"\b(?:samsung|galaxy|самсунг)?\s*(?:s|с)\s*24\s*(?:\+|plus|плюс)\b", re.IGNORECASE), "Samsung Galaxy S24+"),
    (re.compile(r"\b(?:samsung|galaxy|самсунг)\s*(?:s|с)\s*24\b", re.IGNORECASE), "Samsung Galaxy S24"),

    # Samsung Galaxy S23
    (re.compile(r"\b(?:samsung|galaxy|самсунг)?\s*(?:s|с)\s*23\s*ultra\b", re.IGNORECASE), "Samsung Galaxy S23 Ultra"),
    (re.compile(r"\b(?:samsung|galaxy|самсунг)?\s*(?:s|с)\s*23\s*(?:\+|plus|плюс)\b", re.IGNORECASE), "Samsung Galaxy S23+"),
    (re.compile(r"\b(?:samsung|galaxy|самсунг)\s*(?:s|с)\s*23\b", re.IGNORECASE), "Samsung Galaxy S23"),

    # Samsung Galaxy S22
    (re.compile(r"\b(?:samsung|galaxy|самсунг)?\s*(?:s|с)\s*22\s*ultra\b", re.IGNORECASE), "Samsung Galaxy S22 Ultra"),
    (re.compile(r"\b(?:samsung|galaxy|самсунг)\s*(?:s|с)\s*22\b", re.IGNORECASE), "Samsung Galaxy S22"),

    # Samsung Galaxy Fold / Flip
    (re.compile(r"\b(?:galaxy|samsung|самсунг)?\s*z\s*fold\s*6\b", re.IGNORECASE), "Samsung Galaxy Z Fold 6"),
    (re.compile(r"\b(?:galaxy|samsung|самсунг)?\s*z\s*fold\s*5\b", re.IGNORECASE), "Samsung Galaxy Z Fold 5"),
    (re.compile(r"\b(?:galaxy|samsung|самсунг)?\s*z\s*flip\s*6\b", re.IGNORECASE), "Samsung Galaxy Z Flip 6"),
    (re.compile(r"\b(?:galaxy|samsung|самсунг)?\s*z\s*flip\s*5\b", re.IGNORECASE), "Samsung Galaxy Z Flip 5"),

    # Google Pixel 9
    (re.compile(r"\b(?:google|гугл)?\s*pixel\s*9\s*pro\s*xl\b", re.IGNORECASE), "Google Pixel 9 Pro XL"),
    (re.compile(r"\b(?:google|гугл)?\s*pixel\s*9\s*pro\b", re.IGNORECASE), "Google Pixel 9 Pro"),
    (re.compile(r"\b(?:google|гугл)?\s*pixel\s*9\b", re.IGNORECASE), "Google Pixel 9"),

    # Google Pixel 8
    (re.compile(r"\b(?:google|гугл)?\s*pixel\s*8\s*pro\b", re.IGNORECASE), "Google Pixel 8 Pro"),
    (re.compile(r"\b(?:google|гугл)?\s*pixel\s*8a\b", re.IGNORECASE), "Google Pixel 8a"),
    (re.compile(r"\b(?:google|гугл)?\s*pixel\s*8\b", re.IGNORECASE), "Google Pixel 8"),

    # Google Pixel 7
    (re.compile(r"\b(?:google|гугл)?\s*pixel\s*7\s*pro\b", re.IGNORECASE), "Google Pixel 7 Pro"),
    (re.compile(r"\b(?:google|гугл)?\s*pixel\s*7a\b", re.IGNORECASE), "Google Pixel 7a"),
    (re.compile(r"\b(?:google|гугл)?\s*pixel\s*7\b", re.IGNORECASE), "Google Pixel 7"),

    # iPad
    (re.compile(r"\b(?:ipad|айпад)\s*pro\s*13\b", re.IGNORECASE), "iPad Pro 13"),
    (re.compile(r"\b(?:ipad|айпад)\s*pro\s*12\.?9\b", re.IGNORECASE), "iPad Pro 12.9"),
    (re.compile(r"\b(?:ipad|айпад)\s*pro\s*11\b", re.IGNORECASE), "iPad Pro 11"),
    (re.compile(r"\b(?:ipad|айпад)\s*air\s*5\b", re.IGNORECASE), "iPad Air 5"),
    (re.compile(r"\b(?:ipad|айпад)\s*air\s*4\b", re.IGNORECASE), "iPad Air 4"),
    (re.compile(r"\b(?:ipad|айпад)\s*air\b", re.IGNORECASE), "iPad Air 5"),
    (re.compile(r"\b(?:ipad|айпад)\s*mini\s*6\b", re.IGNORECASE), "iPad mini 6"),
    (re.compile(r"\b(?:ipad|айпад)\s*10\b", re.IGNORECASE), "iPad 10"),
    (re.compile(r"\b(?:ipad|айпад)\s*9\b", re.IGNORECASE), "iPad 9"),

    # Consoles & Headphones
    (re.compile(r"\b(?:playstation|плейстейшен|сони\s*пл[еэ]йстейшн)?\s*5\s*slim\b", re.IGNORECASE), "PlayStation 5 Slim"),
    (re.compile(r"\b(?:ps5|playstation\s*5|сони\s*пс5)\b", re.IGNORECASE), "PlayStation 5"),
    (re.compile(r"\bsteam\s*deck\s*oled\b", re.IGNORECASE), "Steam Deck OLED"),
    (re.compile(r"\bsteam\s*deck\b", re.IGNORECASE), "Steam Deck"),
    (re.compile(r"\bairpods\s*max\b", re.IGNORECASE), "AirPods Max"),

    # iPhone 16
    (re.compile(r"\b(?:iphone|айфон)?\s*16\s*(?:pro\s*max|про\s*макс|промакс)\b", re.IGNORECASE), "iPhone 16 Pro Max"),
    (re.compile(r"\b(?:iphone|айфон)?\s*16\s*(?:pro|про)\b", re.IGNORECASE), "iPhone 16 Pro"),
    (re.compile(r"\b(?:iphone|айфон)?\s*16\s*(?:plus|плюс)\b", re.IGNORECASE), "iPhone 16 Plus"),
    (re.compile(r"\b(?:iphone|айфон)\s*16\b", re.IGNORECASE), "iPhone 16"),

    # iPhone 15
    (re.compile(r"\b(?:iphone|айфон)?\s*15\s*(?:pro\s*max|про\s*макс|промакс)\b", re.IGNORECASE), "iPhone 15 Pro Max"),
    (re.compile(r"\b(?:iphone|айфон)?\s*15\s*(?:pro|про)\b", re.IGNORECASE), "iPhone 15 Pro"),
    (re.compile(r"\b(?:iphone|айфон)?\s*15\s*(?:plus|плюс)\b", re.IGNORECASE), "iPhone 15 Plus"),
    (re.compile(r"\b(?:iphone|айфон)\s*15\b", re.IGNORECASE), "iPhone 15"),

    # iPhone 14
    (re.compile(r"\b(?:iphone|айфон)?\s*14\s*(?:pro\s*max|про\s*макс|промакс)\b", re.IGNORECASE), "iPhone 14 Pro Max"),
    (re.compile(r"\b(?:iphone|айфон)?\s*14\s*(?:pro|про)\b", re.IGNORECASE), "iPhone 14 Pro"),
    (re.compile(r"\b(?:iphone|айфон)?\s*14\s*(?:plus|плюс)\b", re.IGNORECASE), "iPhone 14 Plus"),
    (re.compile(r"\b(?:iphone|айфон)\s*14\b", re.IGNORECASE), "iPhone 14"),

    # iPhone 13
    (re.compile(r"\b(?:iphone|айфон)?\s*13\s*(?:pro\s*max|про\s*макс|промакс)\b", re.IGNORECASE), "iPhone 13 Pro Max"),
    (re.compile(r"\b(?:iphone|айфон)?\s*13\s*(?:pro|про)\b", re.IGNORECASE), "iPhone 13 Pro"),
    (re.compile(r"\b(?:iphone|айфон)?\s*13\s*(?:mini|мини|миник)\b", re.IGNORECASE), "iPhone 13 mini"),
    (re.compile(r"\b(?:iphone|айфон)\s*13\b", re.IGNORECASE), "iPhone 13"),

    # iPhone 12
    (re.compile(r"\b(?:iphone|айфон)?\s*12\s*(?:pro\s*max|про\s*макс|промакс)\b", re.IGNORECASE), "iPhone 12 Pro Max"),
    (re.compile(r"\b(?:iphone|айфон)?\s*12\s*(?:pro|про)\b", re.IGNORECASE), "iPhone 12 Pro"),
    (re.compile(r"\b(?:iphone|айфон)?\s*12\s*(?:mini|мини|миник)\b", re.IGNORECASE), "iPhone 12 mini"),
    (re.compile(r"\b(?:iphone|айфон)\s*12\b", re.IGNORECASE), "iPhone 12"),

    # iPhone 11
    (re.compile(r"\b(?:iphone|айфон)?\s*11\s*(?:pro\s*max|про\s*макс|промакс)\b", re.IGNORECASE), "iPhone 11 Pro Max"),
    (re.compile(r"\b(?:iphone|айфон)?\s*11\s*(?:pro|про)\b", re.IGNORECASE), "iPhone 11 Pro"),
    (re.compile(r"\b(?:iphone|айфон)\s*11\b", re.IGNORECASE), "iPhone 11"),

    # iPhone X / XS / XR
    (re.compile(r"\b(?:iphone|айфон)?\s*(?:xs\s*max|хс\s*макс)\b", re.IGNORECASE), "iPhone XS Max"),
    (re.compile(r"\b(?:iphone|айфон)?\s*(?:xs|хс)\b", re.IGNORECASE), "iPhone XS"),
    (re.compile(r"\b(?:iphone|айфон)?\s*(?:xr|хр)\b", re.IGNORECASE), "iPhone XR"),
    (re.compile(r"\b(?:iphone|айфон)\s*(?:x|10|х)\b", re.IGNORECASE), "iPhone X"),

    # iPhone SE
    (re.compile(r"\b(?:iphone|айфон)?\s*se\s*(?:2022|3|3-го|3го)\b", re.IGNORECASE), "iPhone SE 2022"),
    (re.compile(r"\b(?:iphone|айфон)\s*se\b", re.IGNORECASE), "iPhone SE"),
]

# Память: 64, 128, 256, 512, 1024 (1TB)
RE_STORAGE_GB = re.compile(
    r"(?:\b|\s)(64|128|256|512)\s*(?:gb|гб|g|г)\b",
    re.IGNORECASE,
)
RE_STORAGE_TB = re.compile(
    r"(?:\b|\s)(1|2)\s*(?:tb|тб|терабайт)\b",
    re.IGNORECASE,
)
RE_STORAGE_SLASH = re.compile(
    r"\b[468]\s*/\s*(64|128|256|512|1024)\b",
    re.IGNORECASE,
)
# Резервный поиск числа памяти в связке с моделью (например: "iPhone 15 Pro 128 Blue")
RE_STANDALONE_STORAGE = re.compile(
    r"\b(?:128|256|512)\b"
)

# RAM и SSD форматы (например: 16/512, 8/256, 16gb ram)
RE_RAM_SSD_SLASH = re.compile(
    r"\b(8|16|18|24|32|36|48|64)\s*/\s*(128|256|512|1024|1|2)\s*(?:gb|tb|гб|тб)?\b",
    re.IGNORECASE,
)
RE_RAM_EXPLICIT = re.compile(
    r"\b(8|16|18|24|32|36|48|64)\s*(?:gb|гб|g|г)?\s*(?:ram|озу|оперативк[аи]|памят[ьи])\b",
    re.IGNORECASE,
)

# АКБ: 50% - 100%
RE_BATTERY_1 = re.compile(
    r"(?:акб|аккум(?:улятор)?|батаре[яеию]|состояние\s*(?:акб|батареи|аккумулятора)?|емкост[ьи]|health|battery)\s*(?:аккумулятора|батареи)?\s*[:=-]?\s*([5-9][0-9]|100)\s*%?",
    re.IGNORECASE,
)
RE_BATTERY_2 = re.compile(
    r"\b([5-9][0-9]|100)\s*%\s*(?:акб|батаре[яеию]|емкост[ьи]|аккум)",
    re.IGNORECASE,
)
RE_BATTERY_SIMPLE = re.compile(
    r"\bакб\s*([5-9][0-9]|100)\b",
    re.IGNORECASE,
)



def detect_category(model_name: str) -> str:
    """Определяет категорию устройства по его названию."""
    ml = model_name.lower()
    if "macbook" in ml or "mac" in ml:
        return "macbook"
    elif "samsung" in ml or "galaxy" in ml:
        return "samsung"
    elif "pixel" in ml:
        return "pixel"
    elif "ipad" in ml:
        return "ipad"
    elif any(k in ml for k in ["playstation", "ps5", "steam deck", "xbox"]):
        return "consoles"
    elif "watch" in ml:
        return "watch"
    elif "iphone" in ml:
        return "iphone"
    return "other"


class IPhoneNLPParser:
    """Быстрый regex-парсер характеристик гаджетов для нулевой задержки."""

    @classmethod
    def check_blacklist(cls, title: str, description: str) -> Optional[str]:
        """
        Проверяет объявление на признаки подделок, коробок, запчастей или блокировок.
        Возвращает причину отклонения, либо None, если лот чистый.
        """
        full_text = f"{title} {description}"

        if RE_REPLICAS.search(full_text):
            return "Обнаружена копия / реплика"

        if RE_ACCESSORIES_AND_PARTS.search(title):
            return "Не устройство (коробка, чехол, запчасти, битый лот)"

        if RE_ACCESSORIES_AND_PARTS.search(description):
            return "Не устройство / на запчасти"

        if RE_LOCKS.search(full_text):
            return "Заблокированное устройство (iCloud / MDM / Demo / R-Sim)"

        return None

    @classmethod
    def extract_model(
        cls,
        title: str,
        description: str,
        custom_models: Optional[Any] = None,
    ) -> Optional[str]:
        """Определяет модель iPhone или кастомную модель по нормализованному шаблону."""
        # 0. Проверяем пользовательские модели из матрицы
        if custom_models:
            for custom_m in sorted(custom_models, key=len, reverse=True):
                if not custom_m or not isinstance(custom_m, str):
                    continue
                esc = re.escape(custom_m)
                if re.search(rf"\b{esc}\b", title, re.IGNORECASE) or re.search(rf"\b{esc}\b", description[:200], re.IGNORECASE):
                    return custom_m

        # 1. Сначала ищем в заголовке
        for pattern, model_name in MODEL_PATTERNS:
            if pattern.search(title):
                return model_name

        # 2. Если в заголовке нет, ищем в первых 200 символах описания
        desc_start = description[:200]
        for pattern, model_name in MODEL_PATTERNS:
            if pattern.search(desc_start):
                return model_name

        return None

    @classmethod
    def extract_storage(cls, title: str, description: str) -> Optional[int]:
        """Извлекает объем накопителя в GB (64, 128, 256, 512, 1024, 2048)."""
        combined = f"{title} {description[:300]}"

        # 0. RAM/SSD slash формат (например, 16/512, 8/256, 16/1TB)
        slash_ssd = RE_RAM_SSD_SLASH.search(combined)
        if slash_ssd:
            val_str = slash_ssd.group(2)
            if val_str in ("1", "1024"):
                return 1024
            elif val_str in ("2", "2048"):
                return 2048
            return int(val_str)

        # 1. 1TB / 2TB
        tb_match = RE_STORAGE_TB.search(combined)
        if tb_match:
            tb_val = int(tb_match.group(1))
            return tb_val * 1024

        # 2. X/128, X/256 (RAM/ROM)
        slash_match = RE_STORAGE_SLASH.search(combined)
        if slash_match:
            return int(slash_match.group(1))

        # 3. 128gb / 256гб / 512g
        gb_match = RE_STORAGE_GB.search(combined)
        if gb_match:
            return int(gb_match.group(1))

        # 4. Число памяти рядом в заголовке
        standalone_matches = RE_STANDALONE_STORAGE.findall(title)
        if standalone_matches:
            return int(standalone_matches[0])

        return None

    @classmethod
    def extract_ram(cls, title: str, description: str) -> Optional[int]:
        """Извлекает объем RAM (ОЗУ) в GB (8, 16, 18, 24, 32, 64) для ноутбуков и ПК."""
        combined = f"{title} {description[:300]}"
        slash_m = RE_RAM_SSD_SLASH.search(combined)
        if slash_m:
            return int(slash_m.group(1))

        ram_m = RE_RAM_EXPLICIT.search(combined)
        if ram_m:
            return int(ram_m.group(1))

        return None

    @classmethod
    def extract_battery(cls, description: str, title: str = "") -> Optional[int]:
        """Извлекает процент оставшейся емкости АКБ (50..100%)."""
        text = f"{title} {description}"

        match = RE_BATTERY_1.search(text)
        if match:
            return int(match.group(1))

        match2 = RE_BATTERY_2.search(text)
        if match2:
            return int(match2.group(1))

        match3 = RE_BATTERY_SIMPLE.search(text)
        if match3:
            return int(match3.group(1))

        return None

    @classmethod
    def parse_raw_item(
        cls,
        raw: RawItem,
        custom_models: Optional[Any] = None,
    ) -> Optional[ParsedIPhone]:
        """
        Полный конвейер извлечения:
        1. Проверка черного списка (копии, запчасти, блокировки).
        2. Извлечение модели.
        3. Определение категории устройства.
        4. Извлечение объема памяти (ROM/SSD) и оперативной памяти (RAM).
        5. Извлечение АКБ.
        """
        # Фильтр мусора
        reject_reason = cls.check_blacklist(raw.title, raw.description)
        if reject_reason:
            return None

        # Модель
        model = cls.extract_model(raw.title, raw.description, custom_models=custom_models)
        if not model:
            return None

        # Категория устройства
        category = detect_category(model)

        # RAM (для ноутбуков)
        ram = cls.extract_ram(raw.title, raw.description)

        # Память (ROM/SSD)
        storage = cls.extract_storage(raw.title, raw.description)
        if not storage:
            ml = model.lower()
            if "macbook" in ml:
                storage = 256
            elif "playstation" in ml or "ps5" in ml:
                storage = 825
            elif "steam deck" in ml:
                storage = 512
            elif any(s in model for s in ["13", "14", "15", "16", "23", "24", "8", "9"]):
                storage = 128
            else:
                storage = 64

        # Батарея
        battery = cls.extract_battery(raw.description, raw.title)

        return ParsedIPhone(
            platform=raw.platform,
            item_id=raw.item_id,
            title=raw.title,
            description=raw.description,
            category=category,
            model=model,
            storage_gb=storage,
            ram_gb=ram,
            battery_health=battery,
            price=raw.price,
            old_price=raw.old_price,
            is_price_drop=raw.is_price_drop,
            location=raw.location,
            url=raw.url,
            image_url=raw.image_url,
            published_at=raw.published_at,
        )


MSK_TIMEZONE = timezone(timedelta(hours=3))

MONTH_MAP = {
    "янв": 1, "фев": 2, "мар": 3, "апр": 4, "май": 5, "мая": 5,
    "июн": 6, "июл": 7, "авг": 8, "сен": 9, "окт": 10, "ноя": 11, "дек": 12,
}


def parse_marketplace_datetime(raw_val: Any) -> Optional[datetime]:
    """
    Высокоточный парсер даты публикации объявлений с Авито и Юлы.
    Корректно обрабатывает русскоязычные маркеры:
    - 'сегодня в 14:30' (сравнение с текущим московским временем)
    - 'вчера в 18:20' (отклоняется: возраст >= 24ч)
    - 'позавчера в 4:17' (отклоняется: возраст >= 48ч)
    - '25.09.2026' или '25 сентября' (отклоняется: старая дата)
    - 'X минут назад', 'X часов назад', 'только что'
    - Unix timestamp (в секундах или миллисекундах)

    ВАЖНО: При неизвестной/неопределенной дате возвращает None,
    а не текущее время, исключая ложный пропуск старых лотов и рекомендаций!
    """
    if not raw_val:
        return None

    now_msk = datetime.now(MSK_TIMEZONE)

    # 1. Unix timestamp
    if isinstance(raw_val, (int, float)):
        ts = raw_val / 1000.0 if raw_val > 1e11 else float(raw_val)
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    if not isinstance(raw_val, str):
        return None

    text = raw_val.strip().lower()

    # 2. 'только что' / 'секунд назад'
    if "только что" in text or "секунд назад" in text:
        return now_msk.astimezone(timezone.utc)

    # 3. 'X минут назад'
    m_min = re.search(r"(\d+)\s*(?:мин|минут)", text)
    if m_min:
        mins = int(m_min.group(1))
        return (now_msk - timedelta(minutes=mins)).astimezone(timezone.utc)

    # 4. 'X часов назад'
    m_hour = re.search(r"(\d+)\s*(?:час|часа|часов)", text)
    if m_hour:
        hours = int(m_hour.group(1))
        return (now_msk - timedelta(hours=hours)).astimezone(timezone.utc)

    # 5. 'сегодня / вчера / позавчера в HH:MM'
    m_day = re.search(r"(сегодня|вчера|позавчера)\s+в\s+(\d{1,2}):(\d{2})", text)
    if m_day:
        day_word = m_day.group(1)
        hour = int(m_day.group(2))
        minute = int(m_day.group(3))

        offset_days = 0
        if day_word == "вчера":
            offset_days = 1
        elif day_word == "позавчера":
            offset_days = 2

        dt = (now_msk - timedelta(days=offset_days)).replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )
        # Если расхождение часов в пределах 2 минут
        if dt > now_msk:
            dt = now_msk
        return dt.astimezone(timezone.utc)

    # 6. 'DD.MM.YYYY'
    m_full_date = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", text)
    if m_full_date:
        d, m, y = int(m_full_date.group(1)), int(m_full_date.group(2)), int(m_full_date.group(3))
        dt = datetime(y, m, d, 0, 0, 0, tzinfo=MSK_TIMEZONE)
        return dt.astimezone(timezone.utc)

    # 7. 'DD месяца'
    m_month = re.search(r"(\d{1,2})\s+([а-я]{3,8})", text)
    if m_month:
        day = int(m_month.group(1))
        month_str = m_month.group(2)[:3]
        month = MONTH_MAP.get(month_str)
        if month:
            year = now_msk.year
            dt = datetime(year, month, day, 0, 0, 0, tzinfo=MSK_TIMEZONE)
            if dt > now_msk:
                dt = dt.replace(year=year - 1)
            return dt.astimezone(timezone.utc)

    return None


# Алиас для нового мульти-категорийного контекста
GadgetNLPParser = IPhoneNLPParser

