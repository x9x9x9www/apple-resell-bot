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
        self.assertFalse(any("Шаблон торга" in t for t in button_texts))
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

        reply_kb = get_reply_keyboard(current_region="Якутск")
        self.assertIsInstance(reply_kb, ReplyKeyboardMarkup)
        self.assertTrue(reply_kb.resize_keyboard)
        self.assertTrue(reply_kb.is_persistent)

        button_texts = [b.text for row in reply_kb.keyboard for b in row]
        self.assertIn("ℹ️ Информация", button_texts)
        self.assertIn("⭐️ Избранное", button_texts)
        self.assertIn("⚡️ Бредли Перекупер", button_texts)
        self.assertNotIn("📥 Скачать/загрузить Excel", button_texts)
        # Проверяем, что бесполезная кнопка скрытия клавиатуры удалена
        self.assertNotIn("❌ Скрыть клавиатуру", button_texts)

        # Проверяем структуру: 1-я строка во всю ширину (Mini App), 2-я строка с 2 кнопками
        self.assertEqual(len(reply_kb.keyboard[0]), 1)
        self.assertEqual(len(reply_kb.keyboard[1]), 2)

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
        self.assertIn("Текущий регион:</b> Якутск", dash_text)
        self.assertIn("📡 <b>Мониторинг:</b> Авито + Юла", dash_text)

        # 2. Проверяем логику отсутствия спама (удаление старого сообщения перед отправкой нового)
        bot_mock = MagicMock()
        bot_mock.delete_message = AsyncMock(return_value=True)

        new_msg_mock = MagicMock()
        new_msg_mock.message_id = 999
        bot_mock.send_photo = AsyncMock(return_value=new_msg_mock)
        bot_mock.send_message = AsyncMock(return_value=new_msg_mock)
        bot_mock.send_animation = AsyncMock(return_value=new_msg_mock)

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
        # Проверяем, что новое функциональное сообщение отправлено с баннером (анимация или фото)
        self.assertTrue(bot_mock.send_animation.called or bot_mock.send_photo.called or bot_mock.send_message.called)
        # Проверяем, что сохранен новый ID
        self.assertEqual(_last_functional_messages[123456], 999)
        self.assertEqual(res.message_id, 999)

        # 3. Проверяем, что кнопка прямого перехода и избранного присутствуют на объявлениях
        item_kb = get_item_keyboard("https://avito.ru/item/123", item_id="123", model="iPhone 16", price=55000)
        item_buttons = [b.text for row in item_kb.inline_keyboard for b in row]
        self.assertTrue(any("Перейти к объявлению" in t for t in item_buttons))
        self.assertFalse(any("Шаблон торга" in t for t in item_buttons))
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

        # 6. Проверяем, что текст кнопки "📍 Сменить регион", "ℹ️ Информация", "😎 Матрица цен" находятся в KNOWN_BUTTON_TEXTS
        self.assertIn("📍 Сменить регион", KNOWN_BUTTON_TEXTS)
        self.assertIn("ℹ️ Информация", KNOWN_BUTTON_TEXTS)
        self.assertIn("😎 Матрица цен", KNOWN_BUTTON_TEXTS)

    def test_region_gatekeeper_blocks_moscow_when_ekb_selected(self):
        """Проверяет, что при активном Екатеринбурге лоты из Москвы и МО гарантированно отсекаются."""
        from core.regions import RegionManager
        from core.models import RawItem, Platform
        from bot.dispatcher import ItemDispatcher
        import asyncio
        from unittest.mock import AsyncMock, MagicMock

        rm = RegionManager()
        rm.set_region("ekaterinburg")
        self.assertEqual(rm.current["name"], "Екатеринбург")

        # 1. Проверяем метод валидатора RegionManager
        self.assertFalse(rm.is_item_matching_current_region("Москва", "https://youla.ru/moskva/item1"))
        self.assertFalse(rm.is_item_matching_current_region("Домодедово", "https://youla.ru/domodedovo/item2"))
        self.assertFalse(rm.is_item_matching_current_region("Подольск", "https://avito.ru/podolsk/item3"))
        self.assertFalse(rm.is_item_matching_current_region("Казань", "https://avito.ru/kazan/item4"))
        self.assertTrue(rm.is_item_matching_current_region("Екатеринбург", "https://youla.ru/ekaterinburg/item5"))
        self.assertTrue(rm.is_item_matching_current_region("в Екатеринбурге", "https://youla.ru/p/item6"))
        self.assertTrue(rm.is_item_matching_current_region("Екатеринбург, ул. Ленина", "https://avito.ru/ekaterinburg/item7"))

        # 2. Проверяем работу диспетчера
        bot_mock = AsyncMock()
        bot_mock.send_message = AsyncMock()
        bot_mock.send_photo = AsyncMock()
        queue = asyncio.Queue()

        from core.margin_filter import MarginFilter
        mf = MarginFilter()
        if "iPhone 13" not in mf.matrix:
            mf.matrix["iPhone 13"] = {"128": {"max_buy": 35000, "market": 45000, "enabled": True}}

        dispatcher = ItemDispatcher(
            bot=bot_mock,
            queue=queue,
            margin_filter=mf,
            region_manager=rm,
            target_chat_id=12345,
        )

        moscow_item = RawItem(
            platform=Platform.YOULA,
            item_id="msk_item_1",
            title="Apple iPhone 13 128 ГБ в Москве",
            description="",
            price=30000,
            url="https://youla.ru/moskva/smartfony-planshety/smartfony/apple-iphone-13-128-gb-6aa170a9",
            location="Москва",
            published_at=datetime.now(timezone.utc),
        )

        # Обрабатываем московский лот в диспетчере
        asyncio.run(dispatcher._process_single_item(moscow_item))

        # Бот НЕ должен отправить сообщение
        bot_mock.send_message.assert_not_awaited()
        bot_mock.send_photo.assert_not_awaited()

        # Екатеринбургский лот должен успешно пройти фильтры и отправиться
        ekb_item = RawItem(
            platform=Platform.YOULA,
            item_id="ekb_item_1",
            title="Apple iPhone 13 128 ГБ в Екатеринбурге",
            description="",
            price=25000,
            url="https://youla.ru/ekaterinburg/smartfony-planshety/smartfony/apple-iphone-13-128-gb-6aa170a9",
            location="в Екатеринбурге",
            published_at=datetime.now(timezone.utc),
        )

        asyncio.run(dispatcher._process_single_item(ekb_item))
        # Одно из отправлений (фото или текст) должно быть вызвано
        self.assertTrue(bot_mock.send_message.called or bot_mock.send_photo.called)

    def test_save_resell_profile_with_search_links(self):
        from core.user_profile import UserProfileManager, CustomCategory, UserModelConfig
        from core.link_stream import StreamManager
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f_prof, \
             tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f_st:
            prof_path = Path(f_prof.name)
            st_path = Path(f_st.name)

        try:
            user_mgr = UserProfileManager(storage_path=prof_path)
            st_mgr = StreamManager(file_path=st_path)

            raw_payload = {
                "action": "save_resell_profile",
                "region": "Москва",
                "categories": [
                    {
                        "id": "xiaomi",
                        "name": "Xiaomi",
                        "icon": "📱",
                        "search_link": "https://www.avito.ru/moskva/telefony/xiaomi?pmax=40000"
                    }
                ],
                "models": [
                    [
                        "Xiaomi 14",
                        256,
                        42000,
                        1,
                        "xiaomi",
                        52000,
                        "https://www.avito.ru/moskva/telefony/xiaomi-ASgBAgICAkS0wA3OqzmwwQ2I_Dc?pmax=42000"
                    ]
                ]
            }

            user_id = 999111
            profile = user_mgr.get_or_create_profile(user_id)
            for c in raw_payload["categories"]:
                c_name = str(c.get("name", "")).strip()
                c_id = str(c.get("id", "")).strip()
                c_icon = str(c.get("icon", "📱")).strip()
                c_link = str(c.get("search_link", "")).strip()
                profile.categories.append(CustomCategory(id=c_id, name=c_name, icon=c_icon, search_link=c_link))
                if c_link:
                    st_mgr.create_or_update_stream(chat_id=user_id, url=c_link)

            for item in raw_payload["models"]:
                m_name = str(item[0]).strip()
                s_val = int(item[1])
                m_buy = int(item[2])
                en = bool(item[3])
                cat = str(item[4]).strip()
                mkt = int(item[5])
                s_link = str(item[6]).strip()
                if m_name not in profile.models:
                    profile.models[m_name] = {}
                profile.models[m_name][str(s_val)] = UserModelConfig(
                    model=m_name,
                    storage=s_val,
                    enabled=en,
                    max_buy=m_buy,
                    market=mkt,
                    category=cat,
                    search_link=s_link
                )
                if en and s_link:
                    st = st_mgr.create_or_update_stream(chat_id=user_id, url=s_link)
                    if st and m_buy > 0:
                        st.pmax = m_buy

            user_mgr.save_profile(profile)

            # Reload and assert
            reloaded_prof = user_mgr.get_or_create_profile(user_id)
            self.assertEqual(len(reloaded_prof.categories), 1)
            self.assertEqual(reloaded_prof.categories[0].search_link, "https://www.avito.ru/moskva/telefony/xiaomi?pmax=40000")
            cfg = reloaded_prof.get_config("Xiaomi 14", 256)
            self.assertIsNotNone(cfg)
            self.assertEqual(cfg.search_link, "https://www.avito.ru/moskva/telefony/xiaomi-ASgBAgICAkS0wA3OqzmwwQ2I_Dc?pmax=42000")
            self.assertEqual(cfg.max_buy, 42000)

            # Check stream registered
            user_stream = st_mgr.get_stream(user_id)
            self.assertIsNotNone(user_stream)
            self.assertEqual(user_stream.pmax, 42000)
            self.assertTrue(user_stream.is_active)
        finally:
            if prof_path.exists():
                prof_path.unlink()
            if st_path.exists():
                st_path.unlink()

    def test_pause_and_resume_search(self):
        from core.user_profile import UserProfileManager, UserModelConfig
        from core.margin_filter import MarginFilter
        from core.link_stream import StreamManager
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f_prof, \
             tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f_st:
            prof_path = Path(f_prof.name)
            st_path = Path(f_st.name)

        try:
            user_mgr = UserProfileManager(storage_path=prof_path)
            st_mgr = StreamManager(file_path=st_path)
            mf = MarginFilter()
            mf.matrix = {
                "iPhone 15 Pro": {"128": {"max_buy": 65000, "market": 78000, "enabled": True}},
                "Xiaomi 14": {"256": {"max_buy": 45000, "market": 55000, "enabled": True}}
            }

            user_id = 123456
            prof = user_mgr.get_or_create_profile(user_id)
            prof.models = {
                "iPhone 15 Pro": {
                    "128": UserModelConfig(model="iPhone 15 Pro", storage=128, max_buy=65000, enabled=True)
                }
            }
            user_mgr.save_profile(prof)

            st = st_mgr.create_or_update_stream(chat_id=user_id, url="https://avito.ru/moskva/telefony/apple")
            self.assertTrue(st.is_active)

            # PAUSE: все модели и стримы отключаются
            for m_name, storages in prof.models.items():
                for s_key, cfg in storages.items():
                    cfg.enabled = False
            for m_name, storages in mf.matrix.items():
                for s_key, cfg in storages.items():
                    cfg["enabled"] = False
            st.is_active = False

            user_mgr.save_profile(prof)
            st_mgr.save()

            stats_paused = mf.get_stats()
            self.assertEqual(stats_paused["active_configs"], 0)
            self.assertFalse(st.is_active)
            self.assertFalse(prof.get_config("iPhone 15 Pro", 128).enabled)

            # RESUME: все модели и стримы включаются обратно
            for m_name, storages in prof.models.items():
                for s_key, cfg in storages.items():
                    cfg.enabled = True
            for m_name, storages in mf.matrix.items():
                for s_key, cfg in storages.items():
                    cfg["enabled"] = True
            st.is_active = True

            user_mgr.save_profile(prof)
            st_mgr.save()

            stats_resumed = mf.get_stats()
            self.assertEqual(stats_resumed["active_configs"], 2)
            self.assertTrue(st.is_active)
            self.assertTrue(prof.get_config("iPhone 15 Pro", 128).enabled)
        finally:
            if prof_path.exists():
                prof_path.unlink()
            if st_path.exists():
                st_path.unlink()

    def test_platform_filtering_in_dispatcher(self):
        import asyncio
        from unittest.mock import AsyncMock, MagicMock
        from core.models import RawItem, Platform
        from core.user_profile import UserProfileManager, UserModelConfig
        from bot.dispatcher import ItemDispatcher
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f_prof:
            prof_path = Path(f_prof.name)

        try:
            user_mgr = UserProfileManager(storage_path=prof_path)
            chat_id = 987654
            prof = user_mgr.get_or_create_profile(chat_id)
            prof.models = {
                "iPhone 13": {"128": UserModelConfig(model="iPhone 13", storage=128, max_buy=35000, market=45000, enabled=True)}
            }
            prof.platforms = "avito"
            user_mgr.save_profile(prof)

            bot_mock = AsyncMock()
            bot_mock.send_message = AsyncMock()
            bot_mock.send_photo = AsyncMock()
            queue = asyncio.Queue()

            from core.margin_filter import MarginFilter
            mf = MarginFilter()
            mf.matrix = {"iPhone 13": {"128": {"max_buy": 35000, "market": 45000, "enabled": True}}}

            dispatcher = ItemDispatcher(
                bot=bot_mock,
                queue=queue,
                margin_filter=mf,
                user_profile_manager=user_mgr,
                target_chat_id=chat_id,
            )

            youla_item = RawItem(
                platform=Platform.YOULA,
                item_id="youla_p_1",
                title="Apple iPhone 13 128 GB",
                description="",
                price=30000,
                url="https://youla.ru/item/youla_p_1",
                location="Москва",
                published_at=datetime.now(timezone.utc),
            )
            # При platforms="avito", Юла должна быть отсеяна
            asyncio.run(dispatcher._process_single_item(youla_item))
            bot_mock.send_message.assert_not_awaited()
            bot_mock.send_photo.assert_not_awaited()

            # Авито должно пройти
            avito_item = RawItem(
                platform=Platform.AVITO,
                item_id="avito_p_1",
                title="Apple iPhone 13 128 GB",
                description="Отличное состояние",
                price=31000,
                url="https://avito.ru/item/avito_p_1",
                location="Москва",
                published_at=datetime.now(timezone.utc),
            )
            asyncio.run(dispatcher._process_single_item(avito_item))
            self.assertTrue(bot_mock.send_message.called or bot_mock.send_photo.called)

            # При platforms="none" (пауза) - ни один лот не должен отправляться
            prof.platforms = "none"
            user_mgr.save_profile(prof)
            bot_mock.reset_mock()
            asyncio.run(dispatcher._process_single_item(avito_item))
            bot_mock.send_message.assert_not_awaited()
            bot_mock.send_photo.assert_not_awaited()
        finally:
            if prof_path.exists():
                prof_path.unlink()

    def test_setup_bot_commands(self):
        """Проверяет скрытие нативного меню слэш-команд Telegram."""
        import asyncio
        from unittest.mock import AsyncMock, MagicMock
        from bot.bot import setup_bot_commands

        bot_mock = MagicMock()
        bot_mock.delete_my_commands = AsyncMock(return_value=True)

        asyncio.run(setup_bot_commands(bot_mock))
        bot_mock.delete_my_commands.assert_awaited_once()

    def test_enhanced_dashboard_text_with_platform_modes(self):
        """Проверяет отображение режима площадок и статистики в расширенном дашборде."""
        from pathlib import Path
        import tempfile
        from bot.bot import _build_dashboard_text, create_bot_dispatcher
        from core.margin_filter import MarginFilter
        from core.regions import RegionManager
        from core.user_profile import UserProfileManager

        tmp_dir = tempfile.mkdtemp()
        prof_path = Path(tmp_dir) / "test_prof_dash.json"
        try:
            upm = UserProfileManager(storage_path=prof_path)
            rm = RegionManager()
            mf = MarginFilter(matrix={"iPhone 15": {"128": {"max_buy": 50000, "market": 65000, "enabled": True}}})
            
            # Регистрируем в глобальных переменных
            create_bot_dispatcher(margin_filter=mf, region_manager=rm, user_profile_manager=upm)

            # Пользователь с режимом avito
            prof = upm.get_or_create_profile(777)
            prof.platforms = "avito"
            upm.save_profile(prof)

            dash_text = _build_dashboard_text(mf, rm, chat_id=777)
            self.assertIn("Только Авито", dash_text)
            self.assertIn("Конфигураций в радаре", dash_text)
            self.assertIn("Скорость реакции:", dash_text)
        finally:
            if prof_path.exists():
                prof_path.unlink()

    def test_city_text_search_persists_user_profile(self):
        """Проверяет, что ввод города текстом в чат сохраняет город в профиле пользователя."""
        import asyncio
        from pathlib import Path
        import tempfile
        from unittest.mock import AsyncMock, MagicMock
        from bot.bot import create_bot_dispatcher
        from core.regions import RegionManager
        from core.user_profile import UserProfileManager
        from aiogram.types import Message, Chat, User, Update

        tmp_dir = tempfile.mkdtemp()
        prof_path = Path(tmp_dir) / "test_prof_city.json"
        try:
            upm = UserProfileManager(storage_path=prof_path)
            rm = RegionManager()
            dp = create_bot_dispatcher(region_manager=rm, user_profile_manager=upm)

            bot_mock = MagicMock()
            bot_mock.send_message = AsyncMock(return_value=MagicMock(message_id=101))
            bot_mock.delete_message = AsyncMock(return_value=True)

            msg = Message(
                message_id=55,
                date=datetime.now(timezone.utc),
                chat=Chat(id=888, type="private"),
                from_user=User(id=888, is_bot=False, first_name="Tester"),
                text="Якутск",
            ).as_(bot_mock)

            asyncio.run(dp.feed_update(bot_mock, Update(update_id=1, message=msg)))

            # Проверяем, что в профиле пользователя теперь Якутск
            saved_prof = upm.get_or_create_profile(888)
            self.assertEqual(saved_prof.region, "Якутск")
        finally:
            if prof_path.exists():
                prof_path.unlink()


if __name__ == "__main__":
    unittest.main()

