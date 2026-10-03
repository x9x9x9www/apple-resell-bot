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

    async def test_semantic_crossplatform_duplicate(self):
        from core.models import ParsedIPhone, Platform
        from datetime import datetime, timezone

        dedup = RedisDeduplicator(redis_url="redis://invalid-host:9999/0", ttl_hours=1, db_path=":memory:")
        await dedup.connect()

        item_avito = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="avito_123",
            title="iPhone 15 Pro 128gb синий в идеале",
            description="АКБ 91% без сколов",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=91,
            price=52000,
            location="Москва, метро Сокол",
            url="https://avito.ru/123",
            published_at=datetime.now(timezone.utc),
            image_url="https://80.img.avito.st/image/1/1.5eX_S7a6eY-photo1.jpg",
        )

        # Первый лот с Авито — уникальный
        is_dup, reason = await dedup.check_and_mark_semantic_duplicate(item_avito)
        self.assertFalse(is_dup)

        # Тот же продавец выложил тот же телефон на Юлу с другим ID и другим названием
        item_youla = ParsedIPhone(
            platform=Platform.YOULA,
            item_id="youla_999",
            title="Продам Айфон 15 Pro 128 gb синий в идеале!",
            description="АКБ 91% без сколов",
            model="iPhone 15 Pro",
            storage_gb=128,
            battery_health=91,
            price=52000,
            location="Москва, метро Сокол",
            url="https://youla.ru/999",
            published_at=datetime.now(timezone.utc),
            image_url="https://cache3.youla.io/files/images/photo2.jpg",
        )

        # Должен быть распознан как дубликат (кросспостинг)
        is_dup_2, reason_2 = await dedup.check_and_mark_semantic_duplicate(item_youla)
        self.assertTrue(is_dup_2, "Кросспостинг должен отсекаться")
        self.assertIn("кросспостинг", reason_2.lower())

        await dedup.close()

    async def test_semantic_photo_duplicate(self):
        from core.models import ParsedIPhone, Platform
        from datetime import datetime, timezone

        dedup = RedisDeduplicator(redis_url="redis://invalid-host:9999/0", ttl_hours=1, db_path=":memory:")
        await dedup.connect()

        item1 = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="item_1",
            title="iPhone 14 128",
            description="",
            model="iPhone 14",
            storage_gb=128,
            battery_health=85,
            price=40000,
            location="Москва",
            url="https://avito.ru/1",
            published_at=datetime.now(timezone.utc),
            image_url="https://80.img.avito.st/image/1/1.UniquePhotoHash123.jpg",
        )
        is_dup, _ = await dedup.check_and_mark_semantic_duplicate(item1)
        self.assertFalse(is_dup)

        # Перевыкладка с новым ID, но той же фотографией
        item2 = ParsedIPhone(
            platform=Platform.AVITO,
            item_id="item_2",
            title="Срочно iPhone 14",
            description="Другой текст",
            model="iPhone 14",
            storage_gb=128,
            battery_health=85,
            price=39500,
            location="Москва",
            url="https://avito.ru/2",
            published_at=datetime.now(timezone.utc),
            image_url="https://80.img.avito.st/image/1/1.UniquePhotoHash123.jpg",
        )
        is_dup2, reason2 = await dedup.check_and_mark_semantic_duplicate(item2)
        self.assertTrue(is_dup2)
        self.assertIn("фотографии", reason2.lower())

        await dedup.close()

    async def test_micro_price_drop_filtered(self):
        dedup = RedisDeduplicator(redis_url="redis://invalid-host:9999/0", ttl_hours=1, db_path=":memory:", min_price_drop=500)
        await dedup.connect()

        # Стартовая цена 50 000
        await dedup.check_and_update("Авито", "item_micro", 50000)

        # Снижение всего на 50 ₽ (50000 -> 49950) -> отсекается, не считается price drop
        is_new, is_drop, _ = await dedup.check_and_update("Авито", "item_micro", 49950)
        self.assertFalse(is_new)
        self.assertFalse(is_drop, "Микро-снижение цены (< 500 руб) не должно спамить")

        # Существенное снижение на 1 000 ₽ (50000 -> 49000) -> подтвержденный price drop
        is_new2, is_drop2, old_p = await dedup.check_and_update("Авито", "item_micro", 49000)
        self.assertFalse(is_new2)
        self.assertTrue(is_drop2)
        self.assertEqual(old_p, 50000)

        await dedup.close()

    async def test_persistent_storage_across_restarts(self):
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_db = f.name

        try:
            # Запуск 1: сохраняем лот
            dedup1 = RedisDeduplicator(redis_url="redis://invalid-host:9999/0", ttl_hours=1, db_path=temp_db)
            await dedup1.connect()
            is_new = await dedup1.is_new_and_mark("Авито", "persisted_123", 50000)
            self.assertTrue(is_new)
            await dedup1.close()

            # "Перезапуск бота": создаем абсолютно новый экземпляр
            dedup2 = RedisDeduplicator(redis_url="redis://invalid-host:9999/0", ttl_hours=1, db_path=temp_db)
            await dedup2.connect()

            # Лот должен сразу определяться как дубликат из постоянного хранилища
            is_new_after_restart = await dedup2.is_new_and_mark("Авито", "persisted_123", 50000)
            self.assertFalse(is_new_after_restart, "После перезапуска лот должен оставаться дубликатом")
            await dedup2.close()
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)


if __name__ == "__main__":
    unittest.main()
