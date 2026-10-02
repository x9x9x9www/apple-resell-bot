from __future__ import annotations

import unittest
from datetime import datetime, timezone
from core.models import RawItem, Platform
from core.parser import IPhoneNLPParser


class TestIPhoneNLPParser(unittest.TestCase):
    def test_model_extraction(self):
        cases = [
            ("iPhone 15 Pro 128gb идеальный", "iPhone 15 Pro"),
            ("Айфон 14 про макс синий", "iPhone 14 Pro Max"),
            ("Apple iPhone 13 mini 256гб", "iPhone 13 mini"),
            ("Продам 12 про 128", "iPhone 12 Pro"),
            ("iPhone 16 Pro Max 256 Desert Titanium", "iPhone 16 Pro Max"),
            ("Айфон 11 64 черный", "iPhone 11"),
            ("iPhone XS Max gold", "iPhone XS Max"),
        ]
        for text, expected_model in cases:
            model = IPhoneNLPParser.extract_model(text, "")
            self.assertEqual(model, expected_model, f"Failed for text: {text}")

    def test_storage_extraction(self):
        cases = [
            ("iPhone 15 Pro 128 GB", "", 128),
            ("iPhone 14 Pro 256гб", "", 256),
            ("iPhone 13 Pro Max 1TB", "", 1024),
            ("iPhone 13 512g", "", 512),
            ("iPhone 12 64 gb", "", 64),
            ("iPhone 15 Pro", "Память устройства 256 гб, в идеале", 256),
        ]
        for title, desc, expected_storage in cases:
            storage = IPhoneNLPParser.extract_storage(title, desc)
            self.assertEqual(storage, expected_storage, f"Failed for {title} | {desc}")

    def test_battery_extraction(self):
        cases = [
            ("Состояние отличное, АКБ 88%, без ремонтов", 88),
            ("Емкость аккумулятора: 95%. Все функции работают", 95),
            ("Батарея 100, полный комплект, чек", 100),
            ("АКБ 91%. Телефон в чехле", 91),
            ("аккум 82 процента", 82),
            ("Без сколов и дефектов, родная коробка", None),  # Не указан
        ]
        for desc, expected_battery in cases:
            battery = IPhoneNLPParser.extract_battery(desc)
            self.assertEqual(battery, expected_battery, f"Failed for battery: {desc}")

    def test_blacklist_rejection(self):
        # Должны отклоняться:
        bad_cases = [
            ("Копия iPhone 15 Pro Max 1:1 Lux", "Полный комплект на андроиде"),
            ("iPhone 14 Pro Коробка оригинал", "Продам только пустую коробку от телефона"),
            ("Чехол для iPhone 13 Pro силиконовый", "Новый чехол"),
            ("iPhone 12 на запчасти", "Плата сдохла, не включается, экран разбит"),
            ("iPhone 15 Pro iCloud заблокирован", "Забыли пароль, на запчасти или байпас"),
            ("iPhone 14 Pro MDM профиль", "Корпоративный mdm лок"),
            ("iPhone 13 Pro Demo витринный", "Демо версия"),
        ]
        for title, desc in bad_cases:
            reason = IPhoneNLPParser.check_blacklist(title, desc)
            self.assertIsNotNone(reason, f"Should reject bad item: {title}")

    def test_full_pipeline_valid_item(self):
        raw = RawItem(
            platform=Platform.AVITO,
            item_id="12345678",
            title="iPhone 15 Pro 128GB Blue Titanium",
            description="Отличное состояние, АКБ 91%, без ремонтов и сколов",
            price=51000,
            url="https://www.avito.ru/item/12345678",
            location="Москва, метро Сокол",
            published_at=datetime.now(timezone.utc),
        )
        parsed = IPhoneNLPParser.parse_raw_item(raw)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.model, "iPhone 15 Pro")
        self.assertEqual(parsed.storage_gb, 128)
        self.assertEqual(parsed.battery_health, 91)
        self.assertEqual(parsed.price, 51000)

    def test_parse_marketplace_datetime(self):
        from core.parser import parse_marketplace_datetime
        now_utc = datetime.now(timezone.utc)

        # 1. Позавчера (как на скриншоте пользователя)
        dt_day_before = parse_marketplace_datetime("Позавчера в 4:17")
        self.assertIsNotNone(dt_day_before)
        age_hours = (now_utc - dt_day_before).total_seconds() / 3600
        self.assertGreater(age_hours, 30, "Позавчера должно быть старше 30 часов")

        # 2. Вчера
        dt_yesterday = parse_marketplace_datetime("Вчера в 18:20")
        self.assertIsNotNone(dt_yesterday)
        age_hours_y = (now_utc - dt_yesterday).total_seconds() / 3600
        self.assertGreater(age_hours_y, 5, "Вчера должно быть старше 5 часов")

        # 3. 5 минут назад / только что
        dt_just_now = parse_marketplace_datetime("только что")
        self.assertIsNotNone(dt_just_now)
        self.assertLess((now_utc - dt_just_now).total_seconds(), 60)

        # 4. Календарная дата
        dt_old = parse_marketplace_datetime("24.09.2026")
        self.assertIsNotNone(dt_old)
        self.assertGreater((now_utc - dt_old).total_seconds(), 86400)

        # 5. Неизвестный мусор
        dt_unknown = parse_marketplace_datetime("случайный текст")
        self.assertIsNone(dt_unknown, "Неизвестная дата должна возвращать None")


if __name__ == "__main__":
    unittest.main()
