from __future__ import annotations

import unittest
import tempfile
from pathlib import Path

from core.regions import RegionManager, CITY_DATABASE, CITY_ALIASES, POPULAR_REGIONS


class TestRegionManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "test_regions.json"
        self.manager = RegionManager(config_file=self.config_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_region(self):
        current = self.manager.current
        self.assertIn("name", current)
        self.assertIn("avito_id", current)
        self.assertIn("youla_id", current)
        self.assertEqual(current["name"], "Москва")

    def test_set_region_by_key(self):
        res = self.manager.set_region("spb")
        self.assertIsNotNone(res)
        self.assertEqual(res["name"], "Санкт-Петербург")
        self.assertEqual(res["avito_id"], "653240")
        self.assertEqual(self.manager.current["key"], "spb")

    def test_set_region_by_alias(self):
        aliases_to_test = [
            ("питер", "Санкт-Петербург"),
            ("мск", "Москва"),
            ("екб", "Екатеринбург"),
            ("крд", "Краснодар"),
            ("россия", "Вся Россия"),
        ]
        for query, expected_name in aliases_to_test:
            res = self.manager.set_region(query)
            self.assertIsNotNone(res, f"Не удалось найти регион по алиасу: {query}")
            self.assertEqual(res["name"], expected_name)

    def test_set_region_by_russian_name(self):
        res = self.manager.set_region("Казань")
        self.assertIsNotNone(res)
        self.assertEqual(res["name"], "Казань")
        self.assertEqual(res["avito_id"], "632660")

        res_sochi = self.manager.set_region("сочи")
        self.assertIsNotNone(res_sochi)
        self.assertEqual(res_sochi["name"], "Сочи")

    def test_unknown_region(self):
        res = self.manager.set_region("НьюЙорк12345")
        self.assertIsNone(res)
        # Регион не должен измениться
        self.assertNotEqual(self.manager.current["name"], "НьюЙорк12345")

    def test_listeners_notification(self):
        notified = []

        def listener(reg: dict[str, str]):
            notified.append(reg)

        self.manager.add_listener(listener)
        self.manager.set_region("novosibirsk")

        self.assertEqual(len(notified), 1)
        self.assertEqual(notified[0]["name"], "Новосибирск")
        self.assertEqual(notified[0]["avito_id"], "645470")

    def test_persistence_across_instances(self):
        self.manager.set_region("samara")
        self.assertEqual(self.manager.current["name"], "Самара")

        # Создаем второй экземпляр, читающий тот же файл
        manager2 = RegionManager(config_file=self.config_path)
        self.assertEqual(manager2.current["name"], "Самара")
        self.assertEqual(manager2.current["avito_id"], "651080")

    def test_find_cities(self):
        matches = self.manager.find_cities("ниж")
        names = [m[1]["name"] for m in matches]
        self.assertTrue(any("Нижний Новгород" in n for n in names))

    def test_popular_regions_presence(self):
        for key, label in POPULAR_REGIONS:
            self.assertIn(key, CITY_DATABASE, f"Популярный регион {key} отсутствует в базе данных")


if __name__ == "__main__":
    unittest.main()
