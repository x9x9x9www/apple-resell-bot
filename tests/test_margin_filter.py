from __future__ import annotations

import unittest
from datetime import datetime, timezone
from core.models import ParsedIPhone, Platform
from core.margin_filter import MarginFilter
from bot.dispatcher import format_lot_message


class TestMarginFilterAndFormatting(unittest.TestCase):
    def setUp(self):
        self.mock_matrix = {
            "iPhone 15 Pro": {
                "128": {"max_buy": 57000, "market": 71000},
                "256": {"max_buy": 64000, "market": 79000},
            }
        }
        self.margin_filter = MarginFilter(matrix=self.mock_matrix)

    def test_profitable_item(self):
        item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="998877",
            title="iPhone 15 Pro 128",
            description="АКБ 91%",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=91,
            price=51000,
            location="Москва, метро Сокол",
            url="https://www.avito.ru/item/998877",
            published_at=datetime.now(timezone.utc),
        )
        is_profitable = self.margin_filter.evaluate(item)
        self.assertTrue(is_profitable)
        self.assertEqual(item.max_buy_price, 57000)
        self.assertEqual(item.market_price, 71000)
        self.assertEqual(item.profit, 20000)

        # Проверяем форматирование
        msg = format_lot_message(item)
        self.assertIn("СВЕЖИЙ ЛОТ | Авито", msg)
        self.assertIn("iPhone 15 Pro", msg)
        self.assertIn("128 GB", msg)
        self.assertIn("91%", msg)
        self.assertIn("51 000 ₽", msg)
        self.assertIn("Ниже рынка на ~20 000 ₽", msg)
        self.assertIn("Москва, метро Сокол", msg)

    def test_unprofitable_item(self):
        item = ParsedIPhone(
            platform=Platform.YOULA,
            item_id="554433",
            title="iPhone 15 Pro 128",
            description="",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=None,
            price=62000,  # Выше лимита 57 000 ₽
            location="Москва",
            url="https://youla.ru/item/554433",
            published_at=datetime.now(timezone.utc),
        )
        is_profitable = self.margin_filter.evaluate(item)
        self.assertFalse(is_profitable)
        self.assertFalse(item.is_profitable)

    def test_battery_penalty(self):
        # 1. Хорошая батарея (85%) -> без штрафа, лимит 57 000 ₽
        item_good = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="111",
            title="iPhone 15 Pro",
            description="",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=85,
            price=56000,
            location="Москва",
            url="https://avito.ru/111",
            published_at=datetime.now(timezone.utc),
        )
        self.assertTrue(self.margin_filter.evaluate(item_good))
        self.assertEqual(item_good.battery_penalty, 0)
        self.assertEqual(item_good.max_buy_price, 57000)

        # 2. Батарея 78% -> штраф 2 500 ₽, эффективный лимит 57 000 - 2 500 = 54 500 ₽
        item_mid = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="222",
            title="iPhone 15 Pro",
            description="",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=78,
            price=55000,  # 55 000 > 54 500 -> должен быть отклонен!
            location="Москва",
            url="https://avito.ru/222",
            published_at=datetime.now(timezone.utc),
        )
        self.assertFalse(self.margin_filter.evaluate(item_mid))
        self.assertEqual(item_mid.battery_penalty, 2500)
        self.assertEqual(item_mid.max_buy_price, 54500)

        # 3. Батарея 70% -> штраф 4 000 ₽, эффективный лимит 57 000 - 4 000 = 53 000 ₽
        item_low = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="333",
            title="iPhone 15 Pro",
            description="",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=70,
            price=52000,  # 52 000 <= 53 000 -> проходит!
            location="Москва",
            url="https://avito.ru/333",
            published_at=datetime.now(timezone.utc),
        )
        self.assertTrue(self.margin_filter.evaluate(item_low))
        self.assertEqual(item_low.battery_penalty, 4000)
        self.assertEqual(item_low.max_buy_price, 53000)

    def test_disabled_model_configuration(self):
        matrix_with_disabled = {
            "iPhone 15 Pro": {
                "128": {"max_buy": 57000, "market": 71000, "enabled": False},
            }
        }
        mf = MarginFilter(matrix=matrix_with_disabled)
        item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="444",
            title="iPhone 15 Pro",
            description="",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=90,
            price=45000,
            location="Москва",
            url="https://avito.ru/444",
            published_at=datetime.now(timezone.utc),
        )
        self.assertFalse(mf.evaluate(item))
        self.assertIn("отключен", item.rejection_reason)

    def test_toggle_series(self):
        matrix = {
            "iPhone 15 Pro": {"128": {"max_buy": 57000, "market": 71000, "enabled": True}},
            "iPhone 15": {"128": {"max_buy": 45000, "market": 55000, "enabled": True}},
            "iPhone 14": {"128": {"max_buy": 35000, "market": 45000, "enabled": True}},
        }
        mf = MarginFilter(matrix=matrix)
        self.assertTrue(mf.is_series_enabled("15"))
        # Выключаем 15 серию
        new_state = mf.toggle_series("15", save=False)
        self.assertFalse(new_state)
        self.assertFalse(mf.is_series_enabled("15"))
        self.assertFalse(matrix["iPhone 15 Pro"]["128"]["enabled"])
        self.assertFalse(matrix["iPhone 15"]["128"]["enabled"])
        # 14 серия осталась включенной
        self.assertTrue(mf.is_series_enabled("14"))


if __name__ == "__main__":
    unittest.main()
