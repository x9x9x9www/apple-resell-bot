from __future__ import annotations

import unittest
from datetime import datetime, timezone
from core.models import ParsedIPhone, Platform
from bot.dispatcher import format_lot_message


class TestFormatting(unittest.TestCase):
    def test_format_fresh_lot(self):
        item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="10101",
            title="iPhone 15 Pro",
            description="",
            model="iPhone 15 Pro",
            storage_gb=256,
            battery_health=94,
            price=60000,
            location="Москва, метро Тверская",
            url="https://avito.ru/item/10101",
            published_at=datetime.now(timezone.utc),
            profit=15000,
            image_url="https://img.avito.st/image/1",
        )
        msg = format_lot_message(item)
        self.assertIn("⚡️ <b>СВЕЖИЙ ЛОТ | Авито</b>", msg)
        self.assertIn("iPhone 15 Pro", msg)
        self.assertIn("256 GB", msg)
        self.assertIn("94%", msg)
        self.assertIn("60 000 ₽", msg)
        self.assertIn("Ниже рынка на ~15 000 ₽", msg)
        self.assertIn("Москва, метро Тверская", msg)

    def test_format_price_drop(self):
        item = ParsedIPhone(
            platform=Platform.YOULA,
            item_id="20202",
            title="iPhone 14 Pro Max 128",
            description="",
            model="iPhone 14 Pro Max",
            storage_gb=128,
            battery_health=88,
            price=48000,
            old_price=55000,
            is_price_drop=True,
            location="Москва, метро Динамо",
            url="https://youla.ru/item/20202",
            published_at=datetime.now(timezone.utc),
            profit=12000,
        )
        msg = format_lot_message(item)
        self.assertIn("📉 <b>СНИЖЕНИЕ ЦЕНЫ | Юла</b>", msg)
        self.assertIn("Скидка -7 000 ₽!", msg)
        self.assertIn("<s>55 000 ₽</s> ➔ <b>48 000 ₽</b>", msg)
        self.assertIn("Ниже рынка на ~12 000 ₽", msg)

    def test_format_battery_penalty_notice(self):
        item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="30303",
            title="iPhone 13 128",
            description="",
            model="iPhone 13",
            storage_gb=128,
            battery_health=74,
            battery_penalty=4000,
            price=25000,
            location="Москва",
            url="https://avito.ru/item/30303",
            published_at=datetime.now(timezone.utc),
        )
        msg = format_lot_message(item)
        self.assertIn("74%", msg)
        self.assertIn("Уценка на замену: -4 000 ₽", msg)


if __name__ == "__main__":
    unittest.main()
