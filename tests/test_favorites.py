from __future__ import annotations

import os
import tempfile
import unittest
from core.favorites import FavoritesManager


class TestFavoritesManager(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.manager = FavoritesManager(file_path=self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_add_and_get_favorite(self):
        user_id = 12345
        lot = {
            "item_id": "lot101",
            "model": "iPhone 15 Pro",
            "price": 65000,
            "url": "https://avito.ru/101",
            "platform": "Авито",
            "location": "Якутск",
        }
        res = self.manager.add_favorite(user_id, lot)
        self.assertTrue(res)
        self.assertTrue(self.manager.is_favorite(user_id, "lot101"))

        # Повторное добавление должно вернуть False (дубликат не создается)
        res_dup = self.manager.add_favorite(user_id, lot)
        self.assertFalse(res_dup)

        favs = self.manager.get_favorites(user_id)
        self.assertEqual(len(favs), 1)
        self.assertEqual(favs[0]["model"], "iPhone 15 Pro")
        self.assertEqual(favs[0]["price"], 65000)

    def test_remove_favorite(self):
        user_id = 999
        lot = {
            "item_id": "lot202",
            "model": "Samsung S23 Ultra",
            "price": 42000,
            "url": "https://youla.ru/202",
            "platform": "Юла",
        }
        self.manager.add_favorite(user_id, lot)
        self.assertTrue(self.manager.is_favorite(user_id, "lot202"))

        deleted = self.manager.remove_favorite(user_id, "lot202")
        self.assertTrue(deleted)
        self.assertFalse(self.manager.is_favorite(user_id, "lot202"))
        self.assertEqual(len(self.manager.get_favorites(user_id)), 0)

    def test_clear_favorites(self):
        user_id = 777
        for i in range(3):
            self.manager.add_favorite(
                user_id,
                {"item_id": f"lot_{i}", "model": f"Device {i}", "price": 10000 * (i + 1), "url": "https://avito.ru"},
            )
        self.assertEqual(len(self.manager.get_favorites(user_id)), 3)

        count = self.manager.clear_favorites(user_id)
        self.assertEqual(count, 3)
        self.assertEqual(len(self.manager.get_favorites(user_id)), 0)

    def test_lot_caching(self):
        class MockItem:
            item_id = "cache_303"
            model = "Pixel 8 Pro"
            price = 50000
            url = "https://avito.ru/303"
            platform = "Авито"
            location = "Москва"

        self.manager.cache_dispatched_lot(MockItem())
        cached = self.manager.get_cached_lot("cache_303")
        self.assertIsNotNone(cached)
        self.assertEqual(cached["model"], "Pixel 8 Pro")
        self.assertEqual(cached["price"], 50000)


if __name__ == "__main__":
    unittest.main()
