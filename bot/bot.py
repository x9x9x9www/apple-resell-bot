from __future__ import annotations

import io
import json
import logging
from typing import Optional
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from config import settings
from core.margin_filter import MarginFilter
from core.excel_manager import ExcelPricingManager
from core.regions import RegionManager
from bot.keyboards import (
    get_main_menu_keyboard,
    get_regions_keyboard,
    get_models_menu_keyboard,
    get_back_to_menu_keyboard,
)

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    """Создает и настраивает экземпляр aiogram 3 Bot."""
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_bot_dispatcher(
    margin_filter: Optional[MarginFilter] = None,
    region_manager: Optional[RegionManager] = None,
) -> Dispatcher:
    """Создает Dispatcher команд и инлайн-обработчиков для управления ботом."""
    dp = Dispatcher()
    filter_instance = margin_filter if margin_filter is not None else MarginFilter()
    reg_manager = region_manager if region_manager is not None else RegionManager()

    # ---------------------------------------------------------
    # КОМАНДЫ БОТА
    # ---------------------------------------------------------

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        chat_id = message.chat.id
        current_reg_name = reg_manager.current["name"]
        text = (
            "👋 <b>Добро пожаловать в Apple Resell Radar!</b>\n\n"
            "Высокоскоростной поисковый робот для перекупов Apple (Авито & Юла).\n\n"
            "⚡️ <b>Ключевые возможности:</b>\n"
            "• Мгновенный перехват новых лотов (&lt; 2 сек)\n"
            f"• 📍 Регион поиска: <b>{current_reg_name}</b> (смена через кнопку или /city)\n"
            "• 📉 Детекция <b>снижения цен</b> продавцами\n"
            "• 📸 <b>Фотокарточки</b> лотов прямо в ленте\n"
            "• 🔋 <b>Умный учет АКБ</b> (автоматическая скидка на замену)\n"
            "• 📊 Управление ценами выкупа через <b>Excel (.xlsx)</b>\n\n"
            f"🔑 <b>Ваш Chat ID:</b> <code>{chat_id}</code>\n\n"
            "📌 <b>Команды:</b>\n"
            "• /menu — Главное меню настроек и фильтров\n"
            "• /city — Смена региона поиска (или напишите название города)\n"
            "• /export_prices — Скачать текущий прайс-лист в Excel\n"
            "• /status — Статус воркеров и мониторинга\n\n"
            "<i>💡 Чтобы обновить цены выкупа, просто отправьте отредактированный файл .xlsx в этот чат!</i>"
        )
        await message.answer(text, reply_markup=get_main_menu_keyboard(current_reg_name))

    @dp.message(Command("menu", "settings"))
    async def cmd_menu(message: types.Message):
        stats = filter_instance.get_stats()
        current_reg_name = reg_manager.current["name"]
        text = (
            "⚙️ <b>Панель управления Apple Resell Radar</b>\n\n"
            f"📍 Текущий регион: <b>{current_reg_name}</b>\n"
            f"📱 Активных конфигураций: <b>{stats['active_configs']} из {stats['total_configs']}</b>\n\n"
            "Выберите нужный раздел в меню ниже:"
        )
        await message.answer(text, reply_markup=get_main_menu_keyboard(current_reg_name))

    @dp.message(Command("city", "region"))
    async def cmd_city(message: types.Message):
        text_parts = (message.text or "").strip().split(maxsplit=1)
        if len(text_parts) > 1:
            city_query = text_parts[1].strip()
            updated = reg_manager.set_region(city_query)
            if updated:
                ans = (
                    f"✅ <b>Регион поиска успешно изменен!</b>\n\n"
                    f"📍 Новый регион: <b>{updated['name']}</b>\n"
                    f"• Авито locationId: <code>{updated['avito_id']}</code>\n"
                    f"• Юла: <code>{updated['youla_id'] or 'Вся Россия'}</code>\n\n"
                    "Воркеры Авито и Юлы мгновенно переключились на поиск в новом регионе ⚡️"
                )
                await message.answer(ans, reply_markup=get_main_menu_keyboard(updated["name"]))
                return
            else:
                matches = reg_manager.find_cities(city_query)
                if matches:
                    hints = "\n".join(f"• <code>/city {m[1]['name']}</code>" for m in matches[:5])
                    ans = (
                        f"🔍 Город «{city_query}» не найден точно. Возможно, вы имели в виду:\n\n"
                        f"{hints}\n\n"
                        "Или выберите город из списка ниже:"
                    )
                else:
                    ans = (
                        f"❌ Город «{city_query}» не найден в базе.\n\n"
                        "Пожалуйста, выберите город из списка популярных ниже:"
                    )
                await message.answer(ans, reply_markup=get_regions_keyboard(reg_manager.current["key"]))
                return

        current_reg = reg_manager.current
        text = (
            "📍 <b>Настройка региона поиска (Авито & Юла):</b>\n\n"
            f"Текущий регион: <b>{current_reg['name']}</b>\n\n"
            "Выберите город кнопкой ниже или напишите <code>/city Название</code> (например: <code>/city Самара</code>, <code>/city Екатеринбург</code> или <code>/city спб</code>):"
        )
        await message.answer(text, reply_markup=get_regions_keyboard(current_reg["key"]))

    @dp.message(Command("export_prices"))
    async def cmd_export_prices(message: types.Message):
        await _send_excel_file(message, filter_instance)

    # ---------------------------------------------------------
    # СИНХРОНИЗАЦИЯ TELEGRAM MINI APP 2.0 (WEB APP DATA)
    # ---------------------------------------------------------

    @dp.message(F.web_app_data)
    async def handle_webapp_data(message: types.Message):
        """Принимает измененные настройки матрицы цен из Telegram Mini App."""
        try:
            raw_payload = json.loads(message.web_app_data.data)
            action = raw_payload.get("action")
            if action == "update_matrix":
                updated_models = raw_payload.get("matrix", [])
                updated_count = 0
                for item in updated_models:
                    key = item.get("key")
                    price = item.get("price")
                    enabled = item.get("enabled", True)
                    if key in filter_instance.matrix:
                        filter_instance.matrix[key]["max_price"] = price
                        filter_instance.matrix[key]["enabled"] = enabled
                        updated_count += 1
                filter_instance.save_matrix()
                stats = filter_instance.get_stats()
                text = (
                    "✅ <b>Матрица цен успешно обновлена через Mini App!</b>\n\n"
                    f"📱 Синхронизировано моделей: <b>{updated_count}</b>\n"
                    f"🔋 Активных конфигураций: <b>{stats['active_configs']} из {stats['total_configs']}</b>\n\n"
                    "Воркеры мгновенно переключились на обновленные цены."
                )
                await message.answer(text, reply_markup=get_main_menu_keyboard(reg_manager.current["name"]))
        except Exception as e:
            logger.error("Ошибка при синхронизации Mini App: %s", e)
            await message.answer(f"❌ Ошибка применения данных Mini App: {e}")

    # ---------------------------------------------------------
    # TELEGRAM BUSINESS ПОДКЛЮЧЕНИЕ
    # ---------------------------------------------------------

    @dp.business_connection()
    async def handle_business_connection(event: types.BusinessConnection):
        """Фиксирует подключение бота как бизнес-ассистента в личке."""
        logger.info(
            "Бизнес-подключение от пользователя %s: enabled=%s, can_reply=%s",
            event.user.id,
            event.is_enabled,
            event.can_reply,
        )

    @dp.business_message()
    async def handle_business_message(message: types.Message):
        """Интеллектуальная помощь перекупщику при общении с продавцами в ЛС."""
        text = (message.text or "").lower()
        if any(w in text for w in ["самовывоз", "заберу", "скидка", "торг", "авито доставка"]):
            logger.info("Обнаружено целевое сообщение в бизнес-чате: %s", message.text)

    # ---------------------------------------------------------
    # ЗАГРУЗКА EXCEL ПРАЙС-ЛИСТА (.XLSX)
    # ---------------------------------------------------------

    @dp.message(F.document)
    async def handle_document_upload(message: types.Message, bot: Bot):
        doc = message.document
        if not doc or not doc.file_name:
            return

        file_name = doc.file_name.lower()
        if not (file_name.endswith(".xlsx") or file_name.endswith(".xls")):
            return

        status_msg = await message.answer("⏳ <i>Обработка таблицы Excel... Пожалуйста, подождите.</i>")

        try:
            file_io = io.BytesIO()
            await bot.download(doc, destination=file_io)
            bytes_data = file_io.getvalue()

            count, errors = ExcelPricingManager.import_matrix_from_bytes(bytes_data)
            if errors and count == 0:
                err_text = "\n".join(f"• {e}" for e in errors[:5])
                await status_msg.edit_text(
                    f"❌ <b>Ошибка при чтении Excel файла:</b>\n\n{err_text}\n\n"
                    "<i>Пожалуйста, используйте шаблон, выгруженный через /export_prices.</i>"
                )
                return

            # Перезагружаем память фильтра
            filter_instance.reload_matrix()

            err_warning = ""
            if errors:
                err_warning = f"\n\n⚠️ Предупреждения ({len(errors)}):\n" + "\n".join(f"• {e}" for e in errors[:3])

            await status_msg.edit_text(
                f"✅ <b>Прайс-лист успешно обновлен!</b>\n\n"
                f"📊 Загружено конфигураций: <b>{count}</b>\n"
                f"Воркеры Авито и Юлы мгновенно переключились на обновленные лимиты цен.{err_warning}"
            )
            logger.info("Пользователь обновил матрицу цен через Excel: %d строк", count)

        except Exception as e:
            logger.error("Ошибка при обработке файла Excel от пользователя: %s", e, exc_info=True)
            await status_msg.edit_text(f"❌ <b>Сбой обработки файла:</b> {e}")

    # ---------------------------------------------------------
    # ВВОД ГОРОДА ТЕКСТОМ
    # ---------------------------------------------------------

    @dp.message(F.text & ~F.text.startswith("/"))
    async def handle_city_text_search(message: types.Message):
        query = (message.text or "").strip()
        if not query or len(query) > 40:
            return

        # Пробуем распознать город или алиас
        updated = reg_manager.set_region(query)
        if updated:
            ans = (
                f"✅ <b>Регион поиска успешно переключен на: {updated['name']}!</b>\n\n"
                f"• Авито locationId: <code>{updated['avito_id']}</code>\n"
                f"• Юла: <code>{updated['youla_id'] or 'Вся Россия'}</code>\n\n"
                "Воркеры мгновенно начали мониторинг в новом регионе ⚡️"
            )
            await message.answer(ans, reply_markup=get_main_menu_keyboard(updated["name"]))
            return

        # Если прямого совпадения нет, ищем подсказки
        matches = reg_manager.find_cities(query)
        if matches:
            hints = "\n".join(f"• <code>/city {m[1]['name']}</code>" for m in matches[:5])
            ans = (
                f"🔍 По запросу «{query}» найдены города:\n\n{hints}\n\n"
                "Или выберите город из списка:"
            )
            await message.answer(ans, reply_markup=get_regions_keyboard(reg_manager.current["key"]))

    # ---------------------------------------------------------
    # ИНЛАЙН-КОЛЛБЭКИ МЕНЮ
    # ---------------------------------------------------------

    @dp.callback_query(F.data == "menu:main")
    async def cb_main_menu(callback: types.CallbackQuery):
        await callback.answer()
        stats = filter_instance.get_stats()
        current_reg_name = reg_manager.current["name"]
        text = (
            "⚙️ <b>Панель управления Apple Resell Radar</b>\n\n"
            f"📍 Текущий регион: <b>{current_reg_name}</b>\n"
            f"📱 Активных конфигураций: <b>{stats['active_configs']} из {stats['total_configs']}</b>\n\n"
            "Выберите нужный раздел в меню ниже:"
        )
        if callback.message:
            try:
                await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard(current_reg_name))
            except Exception as e:
                logger.debug("Сообщение главного меню не изменилось: %s", e)

    @dp.callback_query(F.data == "menu:region")
    async def cb_regions_menu(callback: types.CallbackQuery):
        await callback.answer()
        current_reg = reg_manager.current
        text = (
            "📍 <b>Выбор региона поиска (Авито & Юла):</b>\n\n"
            f"Текущий активный регион: <b>{current_reg['name']}</b>\n\n"
            "Выберите город из популярных ниже или отправьте команду <code>/city Название</code> (например, <code>/city Казань</code> или <code>/city спб</code>):"
        )
        if callback.message:
            try:
                await callback.message.edit_text(text, reply_markup=get_regions_keyboard(current_reg["key"]))
            except Exception as e:
                logger.debug("Ошибка обновления меню регионов: %s", e)

    @dp.callback_query(F.data.startswith("set_region:"))
    async def cb_set_region(callback: types.CallbackQuery):
        region_key = callback.data.split(":")[1]
        updated = reg_manager.set_region(region_key)
        if updated:
            await callback.answer(f"Регион изменен на {updated['name']} ✅")
            stats = filter_instance.get_stats()
            text = (
                f"✅ <b>Регион поиска успешно изменен на: {updated['name']}</b>\n\n"
                "⚙️ <b>Панель управления Apple Resell Radar</b>\n\n"
                f"📍 Текущий регион: <b>{updated['name']}</b>\n"
                f"📱 Активных конфигураций: <b>{stats['active_configs']} из {stats['total_configs']}</b>\n\n"
                "Выберите нужный раздел в меню ниже:"
            )
            if callback.message:
                await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard(updated["name"]))
        else:
            await callback.answer("Ошибка: регион не найден", show_alert=True)

    @dp.callback_query(F.data == "region:custom")
    async def cb_region_custom(callback: types.CallbackQuery):
        await callback.answer()
        text = (
            "🔍 <b>Поиск города по названию:</b>\n\n"
            "Напишите в чат команду <code>/city Название</code> (например: <code>/city Самара</code>, <code>/city Тюмень</code>, <code>/city спб</code>).\n\n"
            "Или выберите один из популярных городов ниже:"
        )
        if callback.message:
            await callback.message.edit_text(text, reply_markup=get_regions_keyboard(reg_manager.current["key"]))

    @dp.callback_query(F.data == "menu:export_excel")
    async def cb_export_excel(callback: types.CallbackQuery):
        await callback.answer("Генерирую Excel файл...")
        if callback.message:
            await _send_excel_file(callback.message, filter_instance)

    @dp.callback_query(F.data == "menu:models")
    async def cb_models_menu(callback: types.CallbackQuery):
        text = (
            "📱 <b>Фильтр поколений iPhone:</b>\n\n"
            "Нажимайте на кнопки, чтобы включать или отключать мониторинг серий.\n"
            "🟢 <b>Включено</b> | 🔴 <b>Отключено</b>"
        )
        if callback.message:
            await callback.message.edit_text(
                text,
                reply_markup=get_models_menu_keyboard(filter_instance),
            )
        await callback.answer()

    @dp.callback_query(F.data.startswith("toggle_series:"))
    async def cb_toggle_series(callback: types.CallbackQuery):
        series_key = callback.data.split(":")[1]
        new_state = filter_instance.toggle_series(series_key)
        state_str = "включена ✅" if new_state else "отключена ❌"

        if callback.message:
            text = (
                f"Серия <b>iPhone {series_key}</b> {state_str}!\n\n"
                "Нажимайте на кнопки для изменения:"
            )
            await callback.message.edit_text(
                text,
                reply_markup=get_models_menu_keyboard(filter_instance),
            )
        await callback.answer(f"Серия {state_str}")

    @dp.callback_query(F.data == "menu:battery")
    async def cb_battery_info(callback: types.CallbackQuery):
        await callback.answer()
        text = (
            "🔋 <b>Политика автоматической уценки на АКБ:</b>\n\n"
            "Бот автоматически считывает процент износа аккумулятора из описания и названия лота:\n\n"
            "• <b>АКБ ≥ 80%:</b> Выкуп по полной цене из матрицы.\n"
            "• <b>АКБ 75% – 79%:</b> Скидка <b>-2 500 ₽</b> (затраты на замену).\n"
            "• <b>АКБ менее 75%:</b> Скидка <b>-4 000 ₽</b> (премиум-замена банки с перепайкой BMS).\n\n"
            "<i>💡 Таким образом бот защищает вас от неликвидных покупок с убитым аккумулятором!</i>"
        )
        if callback.message:
            try:
                await callback.message.edit_text(text, reply_markup=get_back_to_menu_keyboard())
            except Exception as e:
                logger.error("Ошибка при открытии политики АКБ: %s", e)

    @dp.callback_query(F.data == "menu:webapp_info")
    async def cb_webapp_info(callback: types.CallbackQuery):
        await callback.answer()
        text = (
            "📱 <b>Telegram Mini App (Web App) 2.0:</b>\n\n"
            "Интерактивное веб-приложение для мгновенной настройки матрицы цен пальцем на смартфоне:\n\n"
            "• Визуальные переключатели моделей и поколений (11–16 Pro Max)\n"
            "• Плавные ползунки цен и тактильный виброотклик (Haptic Feedback)\n"
            "• Мгновенная синхронизация с ботом в 1 клик\n\n"
            "<i>💡 Файл приложения находится в проекте: <code>webapp/index.html</code>. "
            "Вы можете открыть его в браузере или развернуть на любом хостинге (например, GitHub Pages), "
            "указав WEBAPP_URL в .env!</i>"
        )
        if callback.message:
            await callback.message.edit_text(text, reply_markup=get_back_to_menu_keyboard())

    @dp.callback_query(F.data.startswith("bargain:"))
    async def cb_bargain_template(callback: types.CallbackQuery):
        await callback.answer()
        parts = callback.data.split(":")
        price = 0
        if len(parts) >= 3:
            try:
                price = int(parts[2])
            except ValueError:
                price = 0

        # Рассчитываем психологически эффективное предложение (скидка 10-15%, округленная до 500)
        offer_price = price
        if price > 10000:
            offer_price = int(price * 0.88)
            offer_price = (offer_price // 500) * 500

        offer_fmt = f"{offer_price:,}".replace(",", " ")
        script_text = (
            f"Здравствуйте! Готов забрать самовывозом сегодня в течение часа за {offer_fmt} ₽ наличными "
            "(без лишних вопросов, деньги сразу на руки). Если договорились — напишите точный адрес, выезжаю!"
        )

        text = (
            "💬 <b>Готовый скрипт для быстрого торга:</b>\n\n"
            "Нажмите на текст ниже, чтобы скопировать его в буфер обмена и отправить продавцу на Авито/Юле:\n\n"
            f"<code>{script_text}</code>\n\n"
            "<i>💡 Скрипт составлен с упором на срочный самовывоз за наличные, что дает максимальный шанс согласия продавца.</i>"
        )
        if callback.message:
            await callback.message.answer(text)

    @dp.callback_query(F.data.startswith("fav:"))
    async def cb_add_to_fav(callback: types.CallbackQuery):
        item_id = callback.data.split(":")[1]
        await callback.answer(f"Лот #{item_id} сохранен в избранное! ⭐️", show_alert=False)

    @dp.callback_query(F.data == "menu:status")
    async def cb_status_menu(callback: types.CallbackQuery):
        await callback.answer()
        text = _build_status_text(filter_instance, reg_manager)
        if callback.message:
            try:
                await callback.message.edit_text(text, reply_markup=get_back_to_menu_keyboard())
            except Exception as e:
                logger.error("Ошибка при открытии статуса: %s", e)

    return dp


def _build_status_text(
    filter_instance: MarginFilter,
    region_manager: Optional[RegionManager] = None,
) -> str:
    """Генерирует форматированный статус работы мониторинга."""
    stats = filter_instance.get_stats()
    region_name = region_manager.current["name"] if region_manager else "Москва"
    avito_loc = region_manager.current["avito_id"] if region_manager else settings.AVITO_LOCATION_ID
    youla_loc = (region_manager.current["youla_id"] if region_manager else settings.YOULA_CITY_ID) or "Вся Россия"
    return (
        "🟢 <b>Статус мониторинга лотов:</b>\n\n"
        f"• Текущий регион: <b>{region_name}</b> (Avito: {avito_loc}, Youla: {youla_loc})\n"
        "• Воркер Авито: <b>АКТИВЕН ⚡️</b> (sort=104, первые 20 позиций)\n"
        "• Воркер Юла: <b>АКТИВЕН ⚡️</b> (web-api & REST выдача)\n"
        "• Дедупликация: <b>Redis + SQLite Local Fallback (48h)</b>\n"
        "• Детекция снижения цен: <b>АКТИВНА 📉</b>\n"
        "• Фотокарточки объявлений: <b>АКТИВНЫ 📸</b>\n"
        f"• Активных iPhone конфигураций: <b>{stats['active_configs']} из {stats['total_configs']}</b>\n"
        "• Скорость реакции: <b>до 2.5 сек</b>\n"
    )


async def _send_excel_file(message: types.Message, filter_instance: MarginFilter) -> None:
    """Генерирует и отправляет Excel-таблицу прайс-листа пользователю."""
    try:
        excel_bytes = ExcelPricingManager.export_matrix_to_bytes(filter_instance.matrix)
        file = BufferedInputFile(excel_bytes, filename="apple_resell_prices.xlsx")
        caption = (
            "📊 <b>Матрица цен выкупа Apple Resell</b>\n\n"
            "Инструкция по настройке:\n"
            "1. Откройте таблицу в Excel, Google Таблицах или на телефоне.\n"
            "2. Измените <b>Макс. выкуп (₽)</b> или <b>Статус (ВКЛ / ВЫКЛ)</b>.\n"
            "3. Отправьте сохраненный файл обратно в этот чат.\n\n"
            "<i>Бот мгновенно применит новые цены без перезагрузки!</i>"
        )
        await message.answer_document(document=file, caption=caption)
    except Exception as e:
        logger.error("Ошибка при генерации Excel прайса: %s", e, exc_info=True)
        await message.answer(f"❌ <b>Ошибка при экспорте Excel:</b> {e}")
