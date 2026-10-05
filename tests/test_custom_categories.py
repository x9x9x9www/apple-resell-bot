import unittest
from core.user_profile import CustomCategory, UserModelConfig, UserResellProfile
from core.parser import IPhoneNLPParser
from core.models import RawItem, Platform
from bot.bot import register_worker_query_listener, broadcast_worker_query


class TestCustomCategoriesAndQueries(unittest.TestCase):
    def test_custom_category_profile(self):
        cat = CustomCategory(id="xiaomi", name="Xiaomi", icon="📱")
        self.assertEqual(cat.id, "xiaomi")
        self.assertEqual(cat.name, "Xiaomi")

        prof = UserResellProfile(
            user_id=123,
            categories=[cat],
            models={
                "Xiaomi 14 Ultra": {
                    "256": UserModelConfig(
                        model="Xiaomi 14 Ultra",
                        storage=256,
                        max_buy=55000,
                        market=68000,
                        category="xiaomi",
                        enabled=True
                    )
                }
            }
        )
        self.assertEqual(len(prof.categories), 1)
        self.assertEqual(prof.categories[0].name, "Xiaomi")
        cfg = prof.get_config("Xiaomi 14 Ultra", 256)
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg.category, "xiaomi")
        self.assertEqual(cfg.max_buy, 55000)

    def test_broadcast_worker_query(self):
        captured = []
        register_worker_query_listener(lambda q: captured.append(q))
        broadcast_worker_query("Dyson Airwrap")
        broadcast_worker_query("Xiaomi")
        self.assertIn("Dyson Airwrap", captured)
        self.assertIn("Xiaomi", captured)

    def test_parser_with_custom_category_model(self):
        matrix_keys = {"Xiaomi 14 Ultra", "iPhone 15 Pro"}
        raw = RawItem(
            item_id="avito_999",
            platform=Platform.AVITO,
            title="Xiaomi 14 Ultra 16/512GB идеальный",
            description="Продам флагман Xiaomi 14 Ultra в отличном состоянии, полный комплект",
            price=49000,
            url="https://avito.ru/item/999"
        )
        parsed = IPhoneNLPParser.parse_raw_item(raw, custom_models=matrix_keys)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.model, "Xiaomi 14 Ultra")
        self.assertEqual(parsed.storage_gb, 512)


if __name__ == "__main__":
    unittest.main()
