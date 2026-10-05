from __future__ import annotations

import unittest
from datetime import datetime, timezone

from core.models import ParsedIPhone, Platform
from core.user_profile import (
    UserProfileManager,
    UserResellProfile,
    UserConditionRules,
    UserModelConfig,
)


class TestUserProfile(unittest.TestCase):
    def setUp(self):
        self.rules = UserConditionRules(
            battery_threshold=80,
            battery_discount=3000,
            allow_defects=False,
            defect_discount=8000,
            ignore_no_face_id=True,
            ignore_mdm_rsim=True,
        )
        self.profile = UserResellProfile(
            user_id=12345678,
            target_margin=5000,
            condition_rules=self.rules,
            models={
                "iPhone 15 Pro": {
                    "128": UserModelConfig(
                        model="iPhone 15 Pro",
                        storage=128,
                        enabled=True,
                        min_price=40000,
                        max_buy=65000,
                        market=72000,
                    )
                }
            }
        )
        self.manager = UserProfileManager()

    def test_evaluate_item_clean_deal(self):
        item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="clean_1",
            title="iPhone 15 Pro 128",
            description="Отличное состояние, полный комплект, аккумулятор 92%",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=92,
            price=62000,
            location="Москва",
            url="https://avito.ru/1",
            published_at=datetime.now(timezone.utc),
        )
        is_ok, reason, breakdown = self.manager.evaluate_item(self.profile, item)
        self.assertTrue(is_ok)
        self.assertIsNone(reason)
        self.assertEqual(item.max_buy_price, 65000)
        self.assertEqual(item.market_price, 72000)
        self.assertEqual(item.profit, 10000)
        self.assertEqual(breakdown["applied_battery_discount"], 0)

    def test_evaluate_item_worn_battery_applies_discount(self):
        item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="bat_1",
            title="iPhone 15 Pro 128",
            description="Оригинал, не вскрывался, АКБ 76%",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=76,  # Ниже 80%
            price=63000,
            location="Москва",
            url="https://avito.ru/2",
            published_at=datetime.now(timezone.utc),
        )
        # Лимит был 65000, скидка на АКБ 3000 -> эффективный лимит 62000.
        # Цена 63000 > 62000 -> должно быть отклонено!
        is_ok, reason, breakdown = self.manager.evaluate_item(self.profile, item)
        self.assertFalse(is_ok)
        self.assertIn("выше вашего лимита 62 000 ₽", reason)
        self.assertEqual(breakdown["applied_battery_discount"], 3000)

        # Но если цена 61000 <= 62000 -> должно пройти!
        item.price = 61000
        is_ok2, reason2, breakdown2 = self.manager.evaluate_item(self.profile, item)
        self.assertTrue(is_ok2)
        self.assertEqual(item.max_buy_price, 62000)

    def test_evaluate_item_defect_rejected_when_not_allowed(self):
        item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="def_1",
            title="iPhone 15 Pro 128",
            description="Трещина на заднем стекле, в остальном идеал",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=88,
            has_defects=True,
            defect_reasons=["трещина"],
            price=50000,
            location="Москва",
            url="https://avito.ru/3",
            published_at=datetime.now(timezone.utc),
        )
        is_ok, reason, _ = self.manager.evaluate_item(self.profile, item)
        self.assertFalse(is_ok)
        self.assertIn("лоты под ремонт выключены", reason)

    def test_evaluate_item_defect_discount_when_allowed(self):
        # Разрешаем дефекты с уценкой 8 000 руб
        self.profile.condition_rules.allow_defects = True
        self.profile.condition_rules.defect_discount = 8000

        item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="def_2",
            title="iPhone 15 Pro 128",
            description="Трещина на заднем стекле",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=88,
            has_defects=True,
            defect_reasons=["трещина"],
            price=55000,
            location="Москва",
            url="https://avito.ru/4",
            published_at=datetime.now(timezone.utc),
        )
        # Лимит 65000 - 8000 = 57000. Цена 55000 <= 57000 -> проходит!
        is_ok, reason, breakdown = self.manager.evaluate_item(self.profile, item)
        self.assertTrue(is_ok)
        self.assertEqual(item.max_buy_price, 57000)
        self.assertEqual(breakdown["applied_defect_discount"], 8000)

    def test_evaluate_item_min_price_junk_filter(self):
        # Цена 15 000 < min_price 40 000 (запчасти/хлам)
        item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="junk_1",
            title="iPhone 15 Pro 128",
            description="Коробка и чехол",
            model="iPhone 15 Pro",
            storage_gb=128,
            price=15000,
            location="Москва",
            url="https://avito.ru/5",
            published_at=datetime.now(timezone.utc),
        )
        is_ok, reason, _ = self.manager.evaluate_item(self.profile, item)
        self.assertFalse(is_ok)
        self.assertIn("ниже минимального порога 40 000 ₽", reason)

    def test_evaluate_item_no_face_id_filter(self):
        item = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="noface_1",
            title="iPhone 15 Pro 128",
            description="Без Face ID, в остальном рабочий",
            model="iPhone 15 Pro",
            storage_gb=128,
            has_no_face_id=True,
            price=45000,
            location="Москва",
            url="https://avito.ru/6",
            published_at=datetime.now(timezone.utc),
        )
        is_ok, reason, _ = self.manager.evaluate_item(self.profile, item)
        self.assertFalse(is_ok)
        self.assertIn("не работает Face ID", reason)

    def test_apply_global_margin(self):
        # Рынок 72 000. Применяем маржу 10 000
        self.profile.apply_global_margin(10000)
        cfg = self.profile.get_config("iPhone 15 Pro", 128)
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg.max_buy, 62000)
        self.assertEqual(self.profile.target_margin, 10000)

    def test_save_and_reload_profile(self):
        import tempfile
        from pathlib import Path
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = Path(f.name)

        try:
            mgr = UserProfileManager(storage_path=tmp_path)
            prof = mgr.get_or_create_profile(999888)
            prof.target_margin = 8500
            prof.condition_rules.battery_discount = 4500
            mgr.save_profile(prof)

            # Перезагружаем менеджер из того же файла
            mgr2 = UserProfileManager(storage_path=tmp_path)
            prof2 = mgr2.get_or_create_profile(999888)
            self.assertEqual(prof2.target_margin, 8500)
            self.assertEqual(prof2.condition_rules.battery_discount, 4500)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()

