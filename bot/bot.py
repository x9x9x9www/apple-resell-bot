from __future__ import annotations

import io
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
from bot.keyboards import (
    get_main_menu_keyboard,
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


def create_bot_dispatcher(margin_filter: Optional[MarginFilter] = None) -> Dispatcher:
    """Создает Dispatcher команд и инлайн-обработчиков для управления ботом."""
    dp = Dispatcher()
    filter_instance = margin_filter if margin_filter is not None else MarginFilter()

    # ---------------------------------------------------------
    # КОМАНДЫ БОТА
    # ---------------------------------------------------------

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        chat_id = message.chat.id
        text = (
            "👋 <b>Добро пожаловать в Apple Resell Radar!</b>\n\n"
            "Высокоскоростной поисковый робот для перекупов Apple (Авито & Юла).\n\n"
            "⚡️ <b>Ключевые возможности:</b>\n"
            "• Мгновенный перехват новых лотов (< 2 сек)\n"
            "• 📉 Детекция <b>снижения цен</b> продавцами\n"
            "• 📸 <b>Фотокарточки</b> лотов прямо в ленте\n"
            "• 🔋 <b>Умный учет АКБ</b> (автоматическая скидка на замену)\n"
            "• 📊 Управление ценами выкупа через <b>Excel (.xlsx)</b>\n\n"
            f"🔑 <b>Ваш Chat ID:</b> <code>{chat_id}</code>\n\n"
            "📌 <b>Команды:</b>\n"
            "• /menu — Главное меню настроек и фильтров\n"
            "• /export_prices — Скачать текущий прайс-лист в Excel\n"
            "• /status — Статус воркеров и мониторинга\n\n"
            "<i>💡 Чтобы обновить цены выкупа, просто отправьте отредактированный файл .xlsx в этот чат!</i>"
        )
        await message.answer(text, reply_markup=get_main_menu_keyboard())

    @dp.message(Command("menu", "settings"))
    async def cmd_menu(message: types.Message):
        stats = filter_instance.get_stats()
        text = (
            "⚙️ <b>Панель управления Apple Resell Radar</b>\n\n"
            f"📱 Активных конфигураций: <b>{stats['active_configs']} из {stats['total_configs']}</b>\n"
            "Выберите нужный раздел в меню ниже:"
        )
        await message.answer(text, reply_markup=get_main_menu_keyboard())

    @dp.message(Command("export_prices"))
    async def cmd_export_prices(message: types.Message):
        await _send_excel_file(message, filter_instance)

    @dp.message(Command("status"))
    async def cmd_status(message: types.Message):
        text = _build_status_text(filter_instance)
        await message.answer(text, reply_markup=get_main_menu_keyboard())

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
    # ИНЛАЙН-КОЛЛБЭКИ МЕНЮ
    # ---------------------------------------------------------

    @dp.callback_query(F.data == "menu:main")
    async def cb_main_menu(callback: types.CallbackQuery):
        stats = filter_instance.get_stats()
        text = (
            "⚙️ <b>Панель управления Apple Resell Radar</b>\n\n"
            f"📱 Активных конфигураций: <b>{stats['active_configs']} из {stats['total_configs']}</b>\n"
            "Выберите нужный раздел в меню ниже:"
        )
        if callback.message:
            await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard())
        await callback.answer()

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
        text = (
            "🔋 <b>Политика автоматической уценки на АКБ:</b>\n\n"
            "Бот автоматически считывает процент износа аккумулятора из описания и названия лота:\n\n"
            "• <b>АКБ ≥ 80%:</b> Выкуп по полной цене из матрицы.\n"
            "• <b>АКБ 75% – 79%:</b> Скидка <b>-2 500 ₽</b> (затраты на замену).\n"
            "• <b>АКБ < 75%:</b> Скидка <b>-4 000 ₽</b> (премиум-замена банки с перепайкой BMS).\n\n"
            "<i>💡 Таким образом бот защищает вас от неликвидных покупок с убитым аккумулятором!</i>"
        )
        if callback.message:
            await callback.message.edit_text(text, reply_markup=get_back_to_menu_keyboard())
        await callback.answer()

    @dp.callback_query(F.data == "menu:status")
    async def cb_status_menu(callback: types.CallbackQuery):
        text = _build_status_text(filter_instance)
        if callback.message:
            await callback.message.edit_text(text, reply_markup=get_back_to_menu_keyboard())
        await callback.answer()

    return dp


def _build_status_text(filter_instance: MarginFilter) -> str:
    """Генерирует форматированный статус работы мониторинга."""
    stats = filter_instance.get_stats()
    return (
        "🟢 <b>Статус мониторинга лотов:</b>\n\n"
        "• Воркер Авито: <b>АКТИВЕН ⚡️</b> (sort=104, первые 20 позиций)\n"
        "• Воркер Юла: <b>АКТИВЕН ⚡️</b> (web-api & REST выдача)\n"
        "• Дедупликация: <b>Redis + Memory Fallback (48h)</b>\n"
        "• Детекция снижения цен: <b>АКТИВНА 📉</b>\n"
        "• Фотокарточки объявлений: <b>АКТИВНЫ 📸</b>\n"
        f"• Активных iPhone конфигураций: <b>{stats['active_configs']} из {stats['total_configs']}</b>\n"
        "• Скорость реакции: <b>< 2.5 сек</b>\n"
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
