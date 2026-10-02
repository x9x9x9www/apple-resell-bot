from __future__ import annotations

import unittest
import asyncio
from core.deduplicator import RedisDeduplicator


class TestRedisDeduplicator(unittest.IsolatedAsyncioTestCase):
    async def test_in_memory_deduplication(self):
        # Тестируем логику дедупликации (с Fallback на in-memory)
        dedup = RedisDeduplicator(redis_url="redis://invalid-host:9999/0", ttl_hours=1)
        await dedup.connect()

        # Первый раз лот с ID 12345 должен быть новым
        is_new_1 = await dedup.is_new_and_mark("Авито", "12345")
        self.assertTrue(is_new_1, "Первое появление лота должно возвращать True")

        # Второй раз тот же ID должен определяться как дубликат
        is_new_2 = await dedup.is_new_and_mark("Авито", "12345")
        self.assertFalse(is_new_2, "Повторный лот должен возвращать False")

        # Тот же ID, но на другой площадке (Юла) должен считаться новым
        is_new_3 = await dedup.is_new_and_mark("Юла", "12345")
        self.assertTrue(is_new_3, "Один и тот же ID на разных площадках уникален")

        await dedup.close()

    async def test_price_drop_detection(self):
        dedup = RedisDeduplicator(redis_url="redis://invalid-host:9999/0", ttl_hours=1)
        await dedup.connect()

        # 1. Первый раз: новый лот по цене 60 000 ₽
        is_new, is_drop, old_price = await dedup.check_and_update("Авито", "item_777", 60000)
        self.assertTrue(is_new)
        self.assertFalse(is_drop)
        self.assertIsNone(old_price)

        # 2. Повторная проверка без изменения цены
        is_new, is_drop, old_price = await dedup.check_and_update("Авито", "item_777", 60000)
        self.assertFalse(is_new)
        self.assertFalse(is_drop)
        self.assertEqual(old_price, 60000)

        # 3. Продавец снизил цену до 52 000 ₽ -> Детекция снижения цены!
        is_new, is_drop, old_price = await dedup.check_and_update("Авито", "item_777", 52000)
        self.assertFalse(is_new)
        self.assertTrue(is_drop)
        self.assertEqual(old_price, 60000)

        # 4. Продавец поднял цену обратно до 55 000 ₽ -> не считается снижением
        is_new, is_drop, old_price = await dedup.check_and_update("Авито", "item_777", 55000)
        self.assertFalse(is_new)
        self.assertFalse(is_drop)
        self.assertEqual(old_price, 52000)

        await dedup.close()


if __name__ == "__main__":
    unittest.main()
