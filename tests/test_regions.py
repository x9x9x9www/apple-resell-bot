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

    def test_yakutsk_region_support(self):
        # 1. По ключу
        res_key = self.manager.set_region("yakutsk")
        self.assertIsNotNone(res_key)
        self.assertEqual(res_key["name"], "Якутск")
        self.assertEqual(res_key["avito_id"], "655840")
        self.assertEqual(res_key["youla_slug"], "yakutsk")

        # 2. По русскому названию
        res_ru = self.manager.set_region("якутск")
        self.assertIsNotNone(res_ru)
        self.assertEqual(res_ru["name"], "Якутск")

        # 3. По алиасам (якт, саха)
        res_ykt = self.manager.set_region("якт")
        self.assertIsNotNone(res_ykt)
        self.assertEqual(res_ykt["name"], "Якутск")

        res_sakha = self.manager.set_region("саха")
        self.assertIsNotNone(res_sakha)
        self.assertEqual(res_sakha["name"], "Якутск")

    def test_expanded_cities_support(self):
        cities = [
            ("Омск", "645830"),
            ("Улан-Удэ", "625600"),
            ("Чита", "661950"),
            ("Благовещенск", "622260"),
            ("Южно-Сахалинск", "652430"),
            ("Норильск", "636540"),
            ("Мурманск", "641320"),
            ("Севастополь", "652550"),
        ]
        for city_name, avito_id in cities:
            res = self.manager.set_region(city_name)
            self.assertIsNotNone(res, f"Город {city_name} не найден")
            self.assertEqual(res["name"], city_name)
            self.assertEqual(res["avito_id"], avito_id)

    def test_regions_pagination(self):
        from bot.keyboards import get_regions_keyboard
        kb_page0 = get_regions_keyboard("moskva", page=0, per_page=12)
        texts_p0 = [b.text for row in kb_page0.inline_keyboard for b in row]
        self.assertTrue(any("Вперёд" in t for t in texts_p0))
        self.assertTrue(any("Якутск" in t for t in texts_p0))

        kb_page1 = get_regions_keyboard("moskva", page=1, per_page=12)
        texts_p1 = [b.text for row in kb_page1.inline_keyboard for b in row]
        self.assertTrue(any("Назад" in t for t in texts_p1))


if __name__ == "__main__":
    unittest.main()

