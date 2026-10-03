from __future__ import annotations

import unittest
from datetime import datetime, timezone

from core.models import ParsedIPhone, Platform
from bot.dispatcher import format_lot_message, FIRE_EFFECT_ID, PARTY_EFFECT_ID
from bot.keyboards import get_item_keyboard, get_main_menu_keyboard


class TestModernBotFeatures(unittest.TestCase):
    def test_expandable_blockquote_in_formatting(self):
        item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="item_desc_1",
            title="iPhone 15 Pro",
            description="Идеальное состояние, чек и коробка, носился в чехле.",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=92,
            price=54000,
            location="Москва, Арбат",
            url="https://avito.ru/item/1",
            published_at=datetime.now(timezone.utc),
            profit=11000,
        )
        msg = format_lot_message(item)
        self.assertIn("<blockquote expandable>", msg)
        self.assertIn("</blockquote>", msg)
        self.assertIn("Идеальное состояние", msg)

    def test_item_keyboard_with_bargain_and_fav(self):
        kb = get_item_keyboard("https://avito.ru/123", item_id="123", model="iPhone 14", price=45000)
        buttons = [b for row in kb.inline_keyboard for b in row]
        button_texts = [b.text for b in buttons]

        self.assertTrue(any("Перейти к объявлению" in t for t in button_texts))
        self.assertTrue(any("Шаблон торга" in t for t in button_texts))
        self.assertTrue(any("В избранное" in t for t in button_texts))

    def test_custom_model_extraction(self):
        from core.parser import IPhoneNLPParser, RawItem
        title = "Продам iPad Pro 11 256GB Space Gray в идеале"
        desc = "Полный комплект, куплен год назад."

        # Без кастомных моделей iPad не распознается как iPhone
        self.assertIsNone(IPhoneNLPParser.extract_model(title, desc))

        # С кастомными моделями из матрицы распознается четко
        custom_models = {"iPad Pro 11", "AirPods Max"}
        extracted = IPhoneNLPParser.extract_model(title, desc, custom_models=custom_models)
        self.assertEqual(extracted, "iPad Pro 11")

        # Проверяем полный parse_raw_item
        raw = RawItem(
            platform=Platform.AVITO,
            item_id="ipad_123",
            title=title,
            description=desc,
            price=59000,
            location="Москва",
            url="https://avito.ru/ipad",
            published_at=datetime.now(timezone.utc),
        )
        parsed = IPhoneNLPParser.parse_raw_item(raw, custom_models=custom_models)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.model, "iPad Pro 11")
        self.assertEqual(parsed.storage_gb, 256)

    def test_custom_model_matrix_evaluation(self):
        from core.margin_filter import MarginFilter
        matrix = {
            "iPad Pro 11": {
                "256": {"max_buy": 65000, "market": 80000, "enabled": True}
            }
        }
        mf = MarginFilter(matrix=matrix)

        # Выгодный лот
        profitable_item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="ipad_prof",
            title="iPad Pro 11",
            description="",
            model="iPad Pro 11",
            storage_gb=256,
            battery_health=None,
            price=60000,
            location="Москва",
            url="https://avito.ru/1",
            published_at=datetime.now(timezone.utc),
        )
        self.assertTrue(mf.evaluate(profitable_item))
        self.assertEqual(profitable_item.profit, 20000)

        # Невыгодный лот (выше порога выкупа)
        unprofitable_item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="ipad_unprof",
            title="iPad Pro 11",
            description="",
            model="iPad Pro 11",
            storage_gb=256,
            battery_health=None,
            price=72000,
            location="Москва",
            url="https://avito.ru/2",
            published_at=datetime.now(timezone.utc),
        )
        self.assertFalse(mf.evaluate(unprofitable_item))

    def test_custom_series_toggle(self):
        from core.margin_filter import MarginFilter
        matrix = {
            "iPad Pro 11": {
                "256": {"max_buy": 65000, "market": 80000, "enabled": True}
            },
            "AirPods Max": {
                "64": {"max_buy": 35000, "market": 45000, "enabled": True}
            }
        }
        mf = MarginFilter(matrix=matrix)
        self.assertTrue(mf.is_series_enabled("custom"))

    def test_main_keyboard_features(self):
        main_kb = get_main_menu_keyboard("Москва")
        main_buttons = [b.text for row in main_kb.inline_keyboard for b in row]
        # Проверяем наличие кнопки Mini App
        self.assertTrue(any("Mini App" in t or "Web App" in t for t in main_buttons))
        # Проверяем, что кнопки VIP нет
        self.assertFalse(any("VIP" in t for t in main_buttons))

    def test_webapp_sync_payload_processing(self):
        from core.margin_filter import MarginFilter
        mf = MarginFilter(matrix={})

        payload = {
            "action": "sync_matrix",
            "matrix": [
                {
                    "model": "iPhone 16 Pro Max",
                    "storage": 256,
                    "price": 108000,
                    "market": 128000,
                    "enabled": True,
                },
                {
                    "model": "iPhone 16 Plus",
                    "storage": 128,
                    "price": 75000,
                    "market": 88000,
                    "enabled": True,
                },
                {
                    "model": "AirPods Max",
                    "storage": 64,
                    "price": 38000,
                    "market": 48000,
                    "enabled": True,
                }
            ]
        }

        # Имитируем логику обновления матрицы как в handle_webapp_data
        for item in payload["matrix"]:
            model = item["model"].strip()
            storage = str(item["storage"])
            price = int(item["price"])
            market = int(item["market"])
            enabled = bool(item["enabled"])

            if model not in mf.matrix:
                mf.matrix[model] = {}
            mf.matrix[model][storage] = {
                "max_buy": price,
                "market": market,
                "enabled": enabled,
            }

        stats = mf.get_stats()
        self.assertEqual(stats["total_models"], 3)
        self.assertEqual(stats["total_configs"], 3)
        self.assertEqual(stats["active_configs"], 3)
        self.assertEqual(mf.matrix["AirPods Max"]["64"]["max_buy"], 38000)
        self.assertEqual(mf.matrix["iPhone 16 Plus"]["128"]["market"], 88000)


if __name__ == "__main__":
    unittest.main()
