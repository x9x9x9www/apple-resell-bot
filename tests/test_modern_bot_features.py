from __future__ import annotations

import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from core.vip import VIPManager
from core.models import ParsedIPhone, Platform
from bot.dispatcher import format_lot_message, FIRE_EFFECT_ID, PARTY_EFFECT_ID
from bot.keyboards import get_item_keyboard, get_vip_keyboard, get_main_menu_keyboard


class TestModernBotFeatures(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vip_file = Path(self.temp_dir.name) / "test_vip.json"
        self.vip_mgr = VIPManager(data_file=self.vip_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_vip_manager_lifecycle(self):
        # 1. По умолчанию пользователь не VIP
        self.assertFalse(self.vip_mgr.is_vip(12345))
        self.assertIsNone(self.vip_mgr.get_vip_expiry_date(12345))

        # 2. Выдача подписки на 30 дней за 250 Stars
        self.vip_mgr.grant_vip(12345, days=30, stars_paid=250)
        self.assertTrue(self.vip_mgr.is_vip(12345))
        self.assertIsNotNone(self.vip_mgr.get_vip_expiry_date(12345))

        # 3. Персистентность при повторной инициализации
        vip_mgr_2 = VIPManager(data_file=self.vip_file)
        self.assertTrue(vip_mgr_2.is_vip(12345))

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

    def test_vip_and_main_keyboards(self):
        vip_kb = get_vip_keyboard()
        vip_buttons = [b.text for row in vip_kb.inline_keyboard for b in row]
        self.assertTrue(any("Stars" in t for t in vip_buttons))

        main_kb = get_main_menu_keyboard("Москва")
        main_buttons = [b.text for row in main_kb.inline_keyboard for b in row]
        self.assertTrue(any("VIP" in t for t in main_buttons))
        self.assertTrue(any("Mini App" in t or "Web App" in t for t in main_buttons))


if __name__ == "__main__":
    unittest.main()
