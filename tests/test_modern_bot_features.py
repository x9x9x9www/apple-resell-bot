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
        title = "Продам Nothing Phone 2 256GB White в идеале"
        desc = "Полный комплект, куплен месяц назад."

        # Без кастомных моделей редкий гаджет не распознается
        self.assertIsNone(IPhoneNLPParser.extract_model(title, desc))

        # С кастомными моделями из матрицы распознается четко
        custom_models = {"Nothing Phone 2", "Dyson Airwrap"}
        extracted = IPhoneNLPParser.extract_model(title, desc, custom_models=custom_models)
        self.assertEqual(extracted, "Nothing Phone 2")

        # Проверяем полный parse_raw_item
        raw = RawItem(
            platform=Platform.AVITO,
            item_id="nothing_123",
            title=title,
            description=desc,
            price=39000,
            location="Москва",
            url="https://avito.ru/nothing",
            published_at=datetime.now(timezone.utc),
        )
        parsed = IPhoneNLPParser.parse_raw_item(raw, custom_models=custom_models)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.model, "Nothing Phone 2")
        self.assertEqual(parsed.storage_gb, 256)
        self.assertEqual(parsed.category, "other")

    def test_macbook_multi_spec_parsing(self):
        from core.parser import IPhoneNLPParser, RawItem
        raw = RawItem(
            platform=Platform.AVITO,
            item_id="mb_1",
            title="MacBook Air M1 16/512 Space Gray",
            description="Состояние отличное, 16gb оперативки, 512 ssd, акб 94%",
            price=48000,
            location="Москва",
            url="https://avito.ru/mb1",
            published_at=datetime.now(timezone.utc),
        )
        parsed = IPhoneNLPParser.parse_raw_item(raw)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.model, "MacBook Air M1")
        self.assertEqual(parsed.category, "macbook")
        self.assertEqual(parsed.ram_gb, 16)
        self.assertEqual(parsed.storage_gb, 512)
        self.assertEqual(parsed.battery_health, 94)

        msg = format_lot_message(parsed)
        self.assertIn("💻", msg)
        self.assertIn("16 GB", msg)
        self.assertIn("512 GB SSD", msg)

    def test_samsung_galaxy_parsing(self):
        from core.parser import IPhoneNLPParser, RawItem
        raw = RawItem(
            platform=Platform.AVITO,
            item_id="sam_1",
            title="Samsung Galaxy S24 Ultra 256GB Black",
            description="Полный комплект, идеал, не вскрывался",
            price=68000,
            location="Москва",
            url="https://avito.ru/sam1",
            published_at=datetime.now(timezone.utc),
        )
        parsed = IPhoneNLPParser.parse_raw_item(raw)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.model, "Samsung Galaxy S24 Ultra")
        self.assertEqual(parsed.category, "samsung")
        self.assertEqual(parsed.storage_gb, 256)

        msg = format_lot_message(parsed)
        self.assertIn("📱", msg)
        self.assertIn("Samsung Galaxy S24 Ultra", msg)

    def test_google_pixel_parsing(self):
        from core.parser import IPhoneNLPParser, RawItem
        raw = RawItem(
            platform=Platform.AVITO,
            item_id="pix_1",
            title="Google Pixel 8 Pro 128GB Hazel",
            description="Европеец, чистый андроид, в чехле",
            price=44000,
            location="Москва",
            url="https://avito.ru/pix1",
            published_at=datetime.now(timezone.utc),
        )
        parsed = IPhoneNLPParser.parse_raw_item(raw)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.model, "Google Pixel 8 Pro")
        self.assertEqual(parsed.category, "pixel")
        self.assertEqual(parsed.storage_gb, 128)

    def test_playstation_console_parsing(self):
        from core.parser import IPhoneNLPParser, RawItem
        raw = RawItem(
            platform=Platform.AVITO,
            item_id="ps_1",
            title="Sony PlayStation 5 с дисководом 825GB",
            description="2 ревизия, 2 геймпада в комплекте",
            price=35000,
            location="Москва",
            url="https://avito.ru/ps1",
            published_at=datetime.now(timezone.utc),
        )
        parsed = IPhoneNLPParser.parse_raw_item(raw)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.model, "PlayStation 5")
        self.assertEqual(parsed.category, "consoles")
        self.assertEqual(parsed.storage_gb, 825)

        msg = format_lot_message(parsed)
        self.assertIn("🎮", msg)

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

    def test_reply_keyboard_and_hide_keyboard(self):
        from bot.keyboards import get_reply_keyboard, get_hide_keyboard
        from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

        reply_kb = get_reply_keyboard(webapp_url="https://x9x9x9www.github.io/apple-resell-bot/")
        self.assertIsInstance(reply_kb, ReplyKeyboardMarkup)
        self.assertTrue(reply_kb.resize_keyboard)
        self.assertTrue(reply_kb.is_persistent)

        button_texts = [b.text for row in reply_kb.keyboard for b in row]
        self.assertIn("⚡️ Меню", button_texts)
        self.assertIn("📱 Матрица цен", button_texts)
        self.assertIn("📍 Сменить регион", button_texts)
        self.assertIn("📊 Скачать Excel", button_texts)
        self.assertIn("🔄 Статус воркеров", button_texts)
        self.assertIn("❌ Скрыть клавиатуру", button_texts)

        # Проверяем наличие WebAppInfo на кнопке матрицы цен
        webapp_buttons = [b for row in reply_kb.keyboard for b in row if b.web_app is not None]
        self.assertEqual(len(webapp_buttons), 1)
        self.assertEqual(webapp_buttons[0].web_app.url, "https://x9x9x9www.github.io/apple-resell-bot/")

        # Проверяем убирание клавиатуры
        hide_kb = get_hide_keyboard()
        self.assertIsInstance(hide_kb, ReplyKeyboardRemove)

        # Проверяем кнопки показа/скрытия в инлайн меню
        main_kb = get_main_menu_keyboard("Москва")
        main_texts = [b.text for row in main_kb.inline_keyboard for b in row]
        self.assertTrue(any("Показать кнопки" in t for t in main_texts))
        self.assertTrue(any("Скрыть кнопки" in t for t in main_texts))

    def test_single_functional_message_without_spam(self):
        import asyncio
        from unittest.mock import AsyncMock, MagicMock
        from bot.bot import (
            _build_dashboard_text,
            _build_status_text,
            _last_functional_messages,
            send_or_replace_functional_message,
        )
        from core.margin_filter import MarginFilter
        from core.regions import RegionManager

        mf = MarginFilter(matrix={"iPhone 16": {"128": {"max_buy": 60000, "market": 75000, "enabled": True}}})
        rm = RegionManager()
        rm.set_region("yakutsk")

        # 1. Проверяем информативность единого дашборда
        dash_text = _build_dashboard_text(mf, rm, chat_id=123456)
        self.assertIn("Панель управления Gadget Resell Radar", dash_text)
        self.assertIn("Якутск", dash_text)
        self.assertIn("123456", dash_text)
        self.assertIn("Все карточки объявлений приходят с кнопками прямого перехода, торга и добавления в избранное", dash_text)

        # 2. Проверяем логику отсутствия спама (удаление старого сообщения перед отправкой нового)
        bot_mock = MagicMock()
        bot_mock.delete_message = AsyncMock(return_value=True)

        new_msg_mock = MagicMock()
        new_msg_mock.message_id = 999
        bot_mock.send_message = AsyncMock(return_value=new_msg_mock)

        # Симулируем наличие старого сообщения с ID 888
        _last_functional_messages[123456] = 888

        # Запускаем send_or_replace_functional_message
        res = asyncio.run(
            send_or_replace_functional_message(
                chat_id=123456,
                bot=bot_mock,
                text="Тестовый дашборд",
            )
        )

        # Проверяем, что старое сообщение было удалено
        bot_mock.delete_message.assert_awaited_once_with(chat_id=123456, message_id=888)
        # Проверяем, что новое сообщение отправлено
        bot_mock.send_message.assert_awaited_once()
        # Проверяем, что сохранен новый ID
        self.assertEqual(_last_functional_messages[123456], 999)
        self.assertEqual(res.message_id, 999)

        # 3. Проверяем, что кнопки действий присутствуют на объявлениях
        item_kb = get_item_keyboard("https://avito.ru/item/123", item_id="123", model="iPhone 16", price=55000)
        item_buttons = [b.text for row in item_kb.inline_keyboard for b in row]
        self.assertTrue(any("Перейти к объявлению" in t for t in item_buttons))
        self.assertTrue(any("Шаблон торга" in t for t in item_buttons))
        self.assertTrue(any("В избранное" in t for t in item_buttons))

        # 4. Проверяем удаление сообщений пользователя (отсутствие спама от пользователя)
        user_msg_mock = MagicMock()
        user_msg_mock.text = "Казань"
        user_msg_mock.delete = AsyncMock(return_value=True)
        from bot.bot import cleanup_user_message, KNOWN_BUTTON_TEXTS
        asyncio.run(cleanup_user_message(user_msg_mock))
        user_msg_mock.delete.assert_awaited_once()

        # 5. Проверяем, что /start никогда не удаляется (чтобы Telegram не сбрасывал сессию в «Начать»)
        start_msg_mock = MagicMock()
        start_msg_mock.text = "/start"
        start_msg_mock.delete = AsyncMock(return_value=True)
        asyncio.run(cleanup_user_message(start_msg_mock))
        start_msg_mock.delete.assert_not_awaited()

        # 6. Проверяем, что текст кнопки "📍 Сменить регион" находится в KNOWN_BUTTON_TEXTS
        self.assertIn("📍 Сменить регион", KNOWN_BUTTON_TEXTS)


if __name__ == "__main__":
    unittest.main()

