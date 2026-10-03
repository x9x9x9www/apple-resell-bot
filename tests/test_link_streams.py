from __future__ import annotations

import asyncio
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from core.models import Platform, RawItem, ParsedGadget
from core.link_stream import (
    SearchStream,
    StreamManager,
    parse_search_url,
)
from bot.dispatcher import format_lot_message, ItemDispatcher
from bot.keyboards import get_stream_control_keyboard, get_stream_filters_keyboard


class TestLinkStreamSystem(unittest.TestCase):
    def test_parse_search_url_avito(self):
        url = "https://www.avito.ru/moskva/telefony/apple-ASgBAgICAUSTAcYOtA0?pmin=25000&pmax=65000&s=104&q=iphone+14"
        parsed = parse_search_url(url)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["platform"], Platform.AVITO)
        self.assertEqual(parsed["city_slug"], "moskva")
        self.assertEqual(parsed["city_name"], "Москва")
        self.assertEqual(parsed["pmin"], 25000)
        self.assertEqual(parsed["pmax"], 65000)
        self.assertEqual(parsed["category_id"], "84")
        self.assertIn("iphone", parsed["title"].lower())

    def test_parse_search_url_avito_f_param_pricing(self):
        # Реальная ссылка пользователя из мобильного браузера с фильтром цен в f
        url = "https://www.avito.ru/moskva_i_mo/telefony/mobilnye_telefony/apple-ASgBAgICAkS0wA3OqzmwwQ2I_Dc?f=ASgBAQECAkS0wA3OqzmwwQ2I_DcDQLLADaTGsYwV1qHtEZKf7RGSoO0R2I7lEM6O5RDMjuUQ8r3IAe69yAHsvcgB5uANNPbBXPrBXPjBXOjrDjT~_dsC_P3bAvr92wICRcaaDBl7ImZyb20iOjMwMDAwLCJ0byI6MzMwMDB94pUSFHsiZnJvbSI6NzksInRvIjoxMDB9"
        parsed = parse_search_url(url)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["pmin"], 30000)
        self.assertEqual(parsed["pmax"], 33000)
        self.assertIn("30 000–33 000 ₽", parsed["title"])

    def test_parse_search_url_ekb_and_categories(self):
        url = "https://www.avito.ru/ekaterinburg/noutbuki?pmax=90000&q=macbook+pro"
        parsed = parse_search_url(url)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["city_slug"], "ekaterinburg")
        self.assertEqual(parsed["city_name"], "Екатеринбург")
        self.assertEqual(parsed["category_id"], "99")
        self.assertEqual(parsed["pmax"], 90000)

    def test_parse_search_url_youla(self):
        url = "https://youla.ru/sankt-peterburg/smartfony-planshety?q=iphone+13"
        parsed = parse_search_url(url)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["platform"], Platform.YOULA)
        self.assertEqual(parsed["city_slug"], "sankt-peterburg")
        self.assertEqual(parsed["city_name"], "Санкт-Петербург")
        self.assertEqual(parsed["query"], "iphone 13")

    def test_stream_manager_lifecycle_and_persistence(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            sm = StreamManager(file_path=tmp_path)
            chat_id = -1001234567890
            url = "https://www.avito.ru/moskva/telefony?pmax=50000&q=iphone"

            stream = sm.create_or_update_stream(chat_id, url)
            self.assertIsNotNone(stream)
            self.assertEqual(stream.chat_id, chat_id)
            self.assertEqual(stream.pmax, 50000)
            self.assertTrue(stream.is_active)

            # Переключение активности
            active = sm.toggle_active(chat_id)
            self.assertFalse(active)
            active = sm.toggle_active(chat_id)
            self.assertTrue(active)

            # Переключение фильтров
            prev_photo = stream.filter_only_photo
            new_photo = sm.toggle_filter(chat_id, "filter_only_photo")
            self.assertEqual(new_photo, not prev_photo)

            # Стоп-слова
            added = sm.add_blacklist_word(chat_id, "тестовый_спам")
            self.assertTrue(added)
            self.assertIn("тестовый_спам", stream.blacklist_words)

            removed = sm.remove_blacklist_word(chat_id, "тестовый_спам")
            self.assertTrue(removed)
            self.assertNotIn("тестовый_спам", stream.blacklist_words)

            # Счётчик найденных лотов
            sm.increment_lots_found(chat_id)
            self.assertEqual(stream.lots_found, 1)

            # Проверка загрузки из файла в новый экземпляр
            sm2 = StreamManager(file_path=tmp_path)
            loaded_stream = sm2.get_stream(chat_id)
            self.assertIsNotNone(loaded_stream)
            self.assertEqual(loaded_stream.lots_found, 1)
            self.assertEqual(loaded_stream.pmax, 50000)

            # Удаление
            del_ok = sm2.delete_stream(chat_id)
            self.assertTrue(del_ok)
            self.assertIsNone(sm2.get_stream(chat_id))
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_evaluate_item_filters(self):
        sm = StreamManager(file_path=Path("/tmp/dummy_streams.json"))
        stream = SearchStream(
            stream_id="test1",
            chat_id=123,
            title="Тест",
            url="https://avito.ru",
            pmin=10000,
            pmax=60000,
            filter_only_photo=True,
            filter_only_desc=True,
            filter_exclude_reserved=True,
            filter_exclude_promo=True,
            blacklist_words=["копия", "реплика", "донор"],
        )

        valid_item = RawItem(
            platform=Platform.AVITO,
            item_id="111",
            title="iPhone 13 128GB идеальный",
            description="Оригинал, не вскрывался, чек есть",
            price=42000,
            url="https://avito.ru/111",
            location="Москва",
            published_at=datetime.now(timezone.utc),
            image_url="https://avito.st/img1.jpg",
            is_reserved=False,
            is_promoted=False,
        )
        ok, reason = sm.evaluate_item_for_stream(stream, valid_item)
        self.assertTrue(ok)
        self.assertIsNone(reason)

        # 1. Отсев без фото
        no_photo_item = RawItem(
            platform=Platform.AVITO,
            item_id="112",
            title="iPhone 13 128GB",
            description="Хорошее состояние",
            price=40000,
            url="https://avito.ru/112",
            location="Москва",
            published_at=datetime.now(timezone.utc),
            image_url=None,
        )
        ok, reason = sm.evaluate_item_for_stream(stream, no_photo_item)
        self.assertFalse(ok)
        self.assertIn("фото", reason.lower())

        # 2. Отсев по брони/резерву (Авито Доставка)
        reserved_item = RawItem(
            platform=Platform.AVITO,
            item_id="113",
            title="iPhone 13 128GB",
            description="Оригинал",
            price=41000,
            url="https://avito.ru/113",
            location="Москва",
            published_at=datetime.now(timezone.utc),
            image_url="https://avito.st/img.jpg",
            is_reserved=True,
        )
        ok, reason = sm.evaluate_item_for_stream(stream, reserved_item)
        self.assertFalse(ok)
        self.assertIn("забронирован", reason.lower())

        # 3. Отсев по платному промо
        promo_item = RawItem(
            platform=Platform.AVITO,
            item_id="114",
            title="iPhone 13 128GB",
            description="Оригинал",
            price=41000,
            url="https://avito.ru/114",
            location="Москва",
            published_at=datetime.now(timezone.utc),
            image_url="https://avito.st/img.jpg",
            is_promoted=True,
        )
        ok, reason = sm.evaluate_item_for_stream(stream, promo_item)
        self.assertFalse(ok)
        self.assertIn("рекламное", reason.lower())

        # 4. Отсев по стоп-словам
        fake_item = RawItem(
            platform=Platform.AVITO,
            item_id="115",
            title="iPhone 13 128GB качественная копия",
            description="1 в 1 как оригинал",
            price=15000,
            url="https://avito.ru/115",
            location="Москва",
            published_at=datetime.now(timezone.utc),
            image_url="https://avito.st/img.jpg",
        )
        ok, reason = sm.evaluate_item_for_stream(stream, fake_item)
        self.assertFalse(ok)
        self.assertIn("копия", reason.lower())

        # 5. Отсев по цене выше лимита
        expensive_item = RawItem(
            platform=Platform.AVITO,
            item_id="116",
            title="iPhone 13 128GB",
            description="Оригинал",
            price=75000,
            url="https://avito.ru/116",
            location="Москва",
            published_at=datetime.now(timezone.utc),
            image_url="https://avito.st/img.jpg",
        )
        ok, reason = sm.evaluate_item_for_stream(stream, expensive_item)
        self.assertFalse(ok)
        self.assertIn("выше лимита", reason.lower())

    def test_formatted_lot_message_seller_and_reserve(self):
        gadget = ParsedGadget(
            platform=Platform.AVITO,
            item_id="999",
            title="iPhone 14 Pro 128GB Space Black",
            description="В идеале, полный комплект",
            price=62000,
            url="https://www.avito.ru/999",
            location="Москва",
            published_at=datetime.now(timezone.utc),
            model="iPhone 14 Pro",
            storage_gb=128,
            battery_health=94,
            profit=10000,
            seller_name="Константин",
            seller_rating=4.9,
            seller_reviews_count=32,
            is_reserved=True,
        )
        msg = format_lot_message(gadget)
        self.assertIn("Константин", msg)
        self.assertIn("4.9", msg)
        self.assertIn("32 отзывов", msg)
        self.assertIn("Товар зарезервирован!", msg)

    def test_stream_keyboards_generation(self):
        stream = SearchStream(
            stream_id="kb_test",
            chat_id=-100998877,
            title="Тестовый поиск",
            url="https://avito.ru",
            filter_only_photo=True,
            filter_exclude_reserved=True,
            filter_exclude_promo=False,
            filter_only_desc=False,
        )
        control_kb = get_stream_control_keyboard(stream)
        self.assertIsNotNone(control_kb)
        buttons_text = [btn.text for row in control_kb.inline_keyboard for btn in row]
        self.assertTrue(any("Приостановить" in b for b in buttons_text))
        self.assertTrue(any("Фильтры" in b for b in buttons_text))
        self.assertTrue(any("Стоп-слова" in b for b in buttons_text))
        self.assertTrue(any("Отключить" in b for b in buttons_text))

        filters_kb = get_stream_filters_keyboard(stream)
        self.assertIsNotNone(filters_kb)
        filter_texts = [btn.text for row in filters_kb.inline_keyboard for btn in row]
        self.assertTrue(any("Только с фото: ✅" in b for b in filter_texts))
        self.assertTrue(any("Без брони (резерва): ✅" in b for b in filter_texts))
        self.assertTrue(any("Без рекламы/промо: ❌" in b for b in filter_texts))


if __name__ == "__main__":
    unittest.main()
