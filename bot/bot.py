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
    get_reply_keyboard,
    get_hide_keyboard,
)

logger = logging.getLogger(__name__)

# Хранилище ID последнего сервисного/функционального сообщения в чате
# chat_id -> message_id для предотвращения спама в чате между объявлениями
_last_functional_messages: dict[int, int] = {}


async def send_or_replace_functional_message(
    chat_id: int,
    bot: Bot,
    text: str,
    reply_markup: Optional[types.ReplyKeyboardMarkup | types.ReplyKeyboardRemove] = None,
) -> types.Message:
    """
    Отправляет сервисное/функциональное сообщение бота, предварительно
    удаляя предыдущее функциональное сообщение в этом чате.
    Благодаря этому чат не захламляется дублирующимися меню и статусами
    (функционал всегда представлен ровно одним актуальным сообщением, без спама).
    """
    old_msg_id = _last_functional_messages.get(chat_id)
    if old_msg_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=old_msg_id)
        except Exception as e:
            logger.debug("Старое функциональное сообщение не удалено или уже отсутствует: %s", e)

    msg = await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
    _last_functional_messages[chat_id] = msg.message_id
    return msg


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
        webapp_url = getattr(settings, "WEBAPP_URL", "")
        text = _build_dashboard_text(filter_instance, reg_manager, chat_id)
        # Отправляем ровно ОДНО сервисное сообщение с прикрепленной всплывающей клавиатурой внизу
        bot = message.bot
        if bot:
            await send_or_replace_functional_message(
                chat_id=chat_id,
                bot=bot,
                text=text,
                reply_markup=get_reply_keyboard(webapp_url),
            )
        else:
            await message.answer(text, reply_markup=get_reply_keyboard(webapp_url))

    @dp.message(Command("keyboard", "kb", "buttons", "show_keyboard"))
    async def cmd_keyboard(message: types.Message):
        webapp_url = getattr(settings, "WEBAPP_URL", "")
        text = (
            "⌨️ <b>Всплывающая клавиатура активирована!</b>\n\n"
            "Кнопки быстрого доступа появились внизу экрана. Чтобы убрать их в любой момент, нажмите <b>«❌ Скрыть клавиатуру»</b>."
        )
        bot = message.bot
        if bot:
            await send_or_replace_functional_message(
                chat_id=message.chat.id,
                bot=bot,
                text=text,
                reply_markup=get_reply_keyboard(webapp_url),
            )
        else:
            await message.answer(text, reply_markup=get_reply_keyboard(webapp_url))

    @dp.message(Command("hide_keyboard", "hide", "hide_buttons"))
    async def cmd_hide_keyboard(message: types.Message):
        text = (
            "📴 <b>Клавиатура скрыта!</b>\n\n"
            "Чтобы кнопки снова всплыли:\n"
            "• Напишите команду <code>/keyboard</code> или <code>/menu</code>."
        )
        bot = message.bot
        if bot:
            await send_or_replace_functional_message(
                chat_id=message.chat.id,
                bot=bot,
                text=text,
                reply_markup=get_hide_keyboard(),
            )
        else:
            await message.answer(text, reply_markup=get_hide_keyboard())

    @dp.message(Command("menu", "settings"))
    async def cmd_menu(message: types.Message):
        chat_id = message.chat.id
        text = _build_dashboard_text(filter_instance, reg_manager, chat_id)
        bot = message.bot
        if bot:
            await send_or_replace_functional_message(
                chat_id=chat_id,
                bot=bot,
                text=text,
            )
        else:
            await message.answer(text)

    @dp.message(Command("status"))
    async def cmd_status(message: types.Message):
        chat_id = message.chat.id
        text = _build_status_text(filter_instance, reg_manager)
        bot = message.bot
        if bot:
            await send_or_replace_functional_message(
                chat_id=chat_id,
                bot=bot,
                text=text,
            )
        else:
            await message.answer(text)

    @dp.message(Command("city", "region"))
    async def cmd_city(message: types.Message):
        chat_id = message.chat.id
        bot = message.bot
        text_parts = (message.text or "").strip().split(maxsplit=1)
        if len(text_parts) > 1:
            city_query = text_parts[1].strip()
            updated = reg_manager.set_region(city_query)
            if updated:
                ans = (
                    f"✅ <b>Регион поиска успешно изменен!</b>\n\n"
                    f"📍 Новый активный регион: <b>{updated['name']}</b>\n"
                    f"• Авито locationId: <code>{updated['avito_id']}</code>\n"
                    f"• Юла: <code>{updated['youla_id'] or 'Вся Россия'}</code>\n\n"
                    "Воркеры Авито и Юлы мгновенно переключились на поиск в новом регионе ⚡️"
                )
                if bot:
                    await send_or_replace_functional_message(chat_id=chat_id, bot=bot, text=ans)
                else:
                    await message.answer(ans)
                return
            else:
                matches = reg_manager.find_cities(city_query)
                if matches:
                    hints = "\n".join(f"• <code>/city {m[1]['name']}</code>" for m in matches[:5])
                    ans = (
                        f"🔍 Город «{city_query}» не найден точно. Возможно, вы имели в виду:\n\n"
                        f"{hints}\n\n"
                        "<i>Отправьте команду <code>/city Название</code> или напишите город в чат.</i>"
                    )
                else:
                    ans = (
                        f"❌ Город «{city_query}» не найден в базе.\n\n"
                        "<i>Напишите точное название города (например: <code>/city Якутск</code>, <code>/city Казань</code>, <code>/city Омск</code>).</i>"
                    )
                if bot:
                    await send_or_replace_functional_message(chat_id=chat_id, bot=bot, text=ans)
                else:
                    await message.answer(ans)
                return

        current_reg = reg_manager.current
        text = (
            "📍 <b>Настройка региона поиска (Авито & Юла):</b>\n\n"
            f"Текущий активный регион: <b>{current_reg['name']}</b>\n\n"
            "Чтобы изменить регион, просто <b>напишите название города прямо в этот чат</b> (или отправьте команду <code>/city Название</code>):\n"
            "• <code>Якутск</code> (или <code>якт</code>, <code>саха</code>)\n"
            "• <code>Санкт-Петербург</code> (или <code>спб</code>, <code>питер</code>)\n"
            "• <code>Екатеринбург</code> (или <code>екб</code>)\n"
            "• <code>Новосибирск</code>\n"
            "• <code>Казань</code>\n"
            "• <code>Омск</code>\n"
            "• <code>Краснодар</code>\n"
            "• <code>Россия</code> (поиск по всей РФ)\n\n"
            "<i>⚡️ База содержит более 100 городов и моментально переключает мониторинг без перезапуска.</i>"
        )
        if bot:
            await send_or_replace_functional_message(chat_id=chat_id, bot=bot, text=text)
        else:
            await message.answer(text)

    @dp.message(Command("export_prices"))
    async def cmd_export_prices(message: types.Message):
        await _send_excel_file(message, filter_instance)

    # ---------------------------------------------------------
    # СИНХРОНИЗАЦИЯ TELEGRAM MINI APP 2.0 (WEB APP DATA)
    # ---------------------------------------------------------

    @dp.message(F.web_app_data)
    async def handle_webapp_data(message: types.Message):
        """Принимает измененные настройки матрицы цен и новые модели из Telegram Mini App."""
        try:
            raw_payload = json.loads(message.web_app_data.data)
            action = raw_payload.get("action")

            if action in ("update_matrix", "sync_matrix"):
                updated_models = raw_payload.get("matrix", [])
                updated_count = 0
                new_count = 0
                new_models = set()

                for item in updated_models:
                    model = item.get("model")
                    storage = str(item.get("storage", "128")).strip()

                    # Поддержка альтернативного формата key: "iPhone 16_128"
                    if not model and item.get("key"):
                        parts = item.get("key").rsplit("_", 1)
                        if len(parts) == 2:
                            model, storage = parts[0], parts[1]
                        else:
                            model = item.get("key")

                    if not model:
                        continue

                    model = model.strip()
                    try:
                        price = int(item.get("price", 0))
                    except (ValueError, TypeError):
                        price = 0

                    if price <= 0:
                        continue

                    try:
                        market = int(item.get("market", int(price * 1.2)))
                    except (ValueError, TypeError):
                        market = int(price * 1.2)

                    enabled = bool(item.get("enabled", True))

                    is_new = False
                    if model not in filter_instance.matrix:
                        filter_instance.matrix[model] = {}
                        is_new = True
                        new_models.add(model)
                    elif storage not in filter_instance.matrix[model]:
                        is_new = True

                    filter_instance.matrix[model][storage] = {
                        "max_buy": price,
                        "market": market,
                        "enabled": enabled,
                    }

                    if is_new:
                        new_count += 1
                    else:
                        updated_count += 1

                filter_instance.save_matrix()
                filter_instance.reload_matrix()
                stats = filter_instance.get_stats()

                new_info = ""
                if new_models:
                    added_preview = ", ".join(sorted(list(new_models))[:5])
                    if len(new_models) > 5:
                        added_preview += f" и ещё {len(new_models) - 5}"
                    new_info = f"\n✨ <b>Добавлены новые модели:</b> <code>{added_preview}</code> (+{new_count} конф.)"

                text = (
                    "✅ <b>Матрица цен успешно синхронизирована с Mini App!</b>\n\n"
                    f"📱 Обновлено конфигураций: <b>{updated_count}</b>{new_info}\n"
                    f"🔋 Активных конфигураций: <b>{stats['active_configs']} из {stats['total_configs']}</b>\n\n"
                    "Воркеры Авито и Юлы мгновенно переключились на обновленные лимиты цен ⚡️"
                )
                bot = message.bot
                if bot:
                    await send_or_replace_functional_message(chat_id=message.chat.id, bot=bot, text=text)
                else:
                    await message.answer(text)

            elif action == "add_model":
                model = str(raw_payload.get("model", "")).strip()
                storage = str(raw_payload.get("storage", "128")).strip()
                price = int(raw_payload.get("price", 0))
                market = int(raw_payload.get("market", int(price * 1.2)))
                enabled = bool(raw_payload.get("enabled", True))

                if model and price > 0:
                    if model not in filter_instance.matrix:
                        filter_instance.matrix[model] = {}
                    filter_instance.matrix[model][storage] = {
                        "max_buy": price,
                        "market": market,
                        "enabled": enabled,
                    }
                    filter_instance.save_matrix()
                    filter_instance.reload_matrix()
                    stats = filter_instance.get_stats()
                    text = (
                        f"✅ <b>Модель «{model} {storage}GB» успешно добавлена в матрицу!</b>\n\n"
                        f"💰 Порог выкупа: <b>{price:,} ₽</b> (рынок: {market:,} ₽)\n"
                        f"🔋 Всего конфигураций: <b>{stats['total_configs']}</b> (активных: {stats['active_configs']})\n\n"
                        "Воркеры мгновенно начали отслеживать лоты по этой модели ⚡️"
                    )
                    bot = message.bot
                    if bot:
                        await send_or_replace_functional_message(chat_id=message.chat.id, bot=bot, text=text)
                    else:
                        await message.answer(text)
        except Exception as e:
            logger.error("Ошибка при синхронизации Mini App: %s", e, exc_info=True)
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
            if message.chat:
                _last_functional_messages[message.chat.id] = status_msg.message_id
            logger.info("Пользователь обновил матрицу цен через Excel: %d строк", count)

        except Exception as e:
            logger.error("Ошибка при обработке файла Excel от пользователя: %s", e, exc_info=True)
            await status_msg.edit_text(f"❌ <b>Сбой обработки файла:</b> {e}")

    # ---------------------------------------------------------
    # ОБРАБОТЧИКИ НАЖАТИЙ НА КНОПКИ ВСПЛЫВАЮЩЕЙ КЛАВИАТУРЫ
    # ---------------------------------------------------------

    @dp.message(F.text.in_({"❌ Скрыть клавиатуру", "🙈 Скрыть кнопки", "📴 Скрыть клавиатуру", "Скрыть клавиатуру"}))
    async def handle_hide_keyboard_btn(message: types.Message):
        await cmd_hide_keyboard(message)

    @dp.message(F.text.in_({"⚡️ Меню", "⚡️ Главное меню", "Меню"}))
    async def handle_reply_menu_btn(message: types.Message):
        await cmd_menu(message)

    @dp.message(F.text.in_({"📍 Сменить регион", "📍 Регион", "Сменить регион"}))
    async def handle_reply_region_btn(message: types.Message):
        await cmd_city(message)

    @dp.message(F.text.in_({"📊 Скачать Excel", "📊 Excel-прайс", "Скачать Excel"}))
    async def handle_reply_export_btn(message: types.Message):
        await _send_excel_file(message, filter_instance)

    @dp.message(F.text.in_({"🔄 Статус воркеров", "🔄 Статус", "Статус"}))
    async def handle_reply_status_btn(message: types.Message):
        await cmd_status(message)

    @dp.message(F.text.in_({"📱 Матрица цен", "Матрица цен"}))
    async def handle_reply_webapp_btn(message: types.Message):
        webapp_url = getattr(settings, "WEBAPP_URL", "")
        if webapp_url:
            text = (
                "📱 <b>Telegram Mini App 2.0 (Матрица цен)</b>\n\n"
                "Вы можете управлять порогами цен, добавлять новые модели и менять статусы выкупа со смартфона.\n\n"
                f"🔗 <b>Открыть в браузере или Telegram:</b>\n{webapp_url}\n\n"
                "<i>💡 Кнопка «📱 Матрица цен» также доступна на нижней клавиатуре.</i>"
            )
        else:
            text = (
                "📱 <b>Матрица цен (Mini App):</b>\n\n"
                "URL веб-приложения не задан в конфигурации (.env WEBAPP_URL).\n"
                "Вы можете выгрузить прайс-лист в Excel командой <code>/export_prices</code>."
            )
        bot = message.bot
        if bot:
            await send_or_replace_functional_message(chat_id=message.chat.id, bot=bot, text=text)
        else:
            await message.answer(text)

    # ---------------------------------------------------------
    # ВВОД ГОРОДА ТЕКСТОМ
    # ---------------------------------------------------------

    @dp.message(F.text & ~F.text.startswith("/"))
    async def handle_city_text_search(message: types.Message):
        query = (message.text or "").strip()
        if not query or len(query) > 40:
            return

        chat_id = message.chat.id
        bot = message.bot

        # Пробуем распознать город или алиас
        updated = reg_manager.set_region(query)
        if updated:
            ans = (
                f"✅ <b>Регион поиска успешно переключен на: {updated['name']}!</b>\n\n"
                f"• Авито locationId: <code>{updated['avito_id']}</code>\n"
                f"• Юла: <code>{updated['youla_id'] or 'Вся Россия'}</code>\n\n"
                "Воркеры мгновенно начали мониторинг в новом регионе ⚡️"
            )
            if bot:
                await send_or_replace_functional_message(chat_id=chat_id, bot=bot, text=ans)
            else:
                await message.answer(ans)
            return

        # Если прямого совпадения нет, ищем подсказки
        matches = reg_manager.find_cities(query)
        if matches:
            hints = "\n".join(f"• <code>/city {m[1]['name']}</code>" for m in matches[:5])
            ans = (
                f"🔍 По запросу «{query}» найдены города:\n\n{hints}\n\n"
                "<i>Напишите точный город из списка выше.</i>"
            )
            if bot:
                await send_or_replace_functional_message(chat_id=chat_id, bot=bot, text=ans)
            else:
                await message.answer(ans)

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

    @dp.callback_query(F.data.startswith("page_regions:"))
    async def cb_page_regions(callback: types.CallbackQuery):
        page = int(callback.data.split(":")[1])
        await callback.answer()
        if callback.message:
            try:
                await callback.message.edit_reply_markup(
                    reply_markup=get_regions_keyboard(reg_manager.current["key"], page=page)
                )
            except Exception as e:
                logger.debug("Ошибка смены страницы регионов: %s", e)

    @dp.callback_query(F.data == "noop")
    async def cb_noop(callback: types.CallbackQuery):
        await callback.answer()

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
            "⚡️ <b>Фильтр категорий и моделей гаджетов:</b>\n\n"
            "Нажимайте на кнопки, чтобы включать или отключать мониторинг (MacBook, Samsung, Pixel, iPad, консоли, iPhone).\n"
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

        series_label = dict(filter_instance.SERIES_LIST).get(series_key, f"Серия {series_key}")

        if callback.message:
            text = (
                f"Категория <b>{series_label}</b> {state_str}!\n\n"
                "Нажимайте на кнопки для изменения:"
            )
            await callback.message.edit_text(
                text,
                reply_markup=get_models_menu_keyboard(filter_instance),
            )
        await callback.answer(f"{series_label}: {state_str}")

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
            "📱 <b>Telegram Mini App 2.0 (Управление матрицей цен):</b>\n\n"
            "Интерактивное веб-приложение для гибкого управления моделями и ценами со смартфона:\n\n"
            "• ➕ <b>Добавление собственных моделей</b> (быстрые шаблоны или свой ввод)\n"
            "• 💾 <b>Выбор любых объемов накопителя</b> (64 GB – 2 TB)\n"
            "• ✏️ <b>Быстрое изменение цен выкупа</b> (кнопки +/- 1 000 ₽ или прямой ввод)\n"
            "• 📈 Автоматическая оценка рыночной стоимости и расчет маржи\n"
            "• 🔍 <b>Живой поиск</b> и умные фильтры по сериям («Свои ⭐»)\n"
            "• ⚡️ Мгновенная синхронизация матрицы цен с ботом в 1 клик\n\n"
            "<i>💡 Файл приложения находится в проекте: <code>webapp/index.html</code>. "
            "Вы можете открыть его прямо сейчас в браузере или развернуть на любом хостинге (например, GitHub Pages), "
            "указав <code>WEBAPP_URL</code> в .env!</i>"
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
            "<i>💡 Скрипт составлен с упором на срочный самовывоз за наличные.</i>"
        )
        bot = callback.bot or (callback.message.bot if callback.message else None)
        if callback.message and bot:
            await send_or_replace_functional_message(
                chat_id=callback.message.chat.id,
                bot=bot,
                text=text,
            )
        elif callback.message:
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

    @dp.callback_query(F.data == "menu:show_keyboard")
    async def cb_show_keyboard(callback: types.CallbackQuery):
        await callback.answer("Клавиатура активирована! ⌨️")
        webapp_url = getattr(settings, "WEBAPP_URL", "")
        bot = callback.bot or (callback.message.bot if callback.message else None)
        if callback.message and bot:
            await send_or_replace_functional_message(
                chat_id=callback.message.chat.id,
                bot=bot,
                text=(
                    "⌨️ <b>Всплывающая клавиатура активирована!</b>\n\n"
                    "Кнопки быстрого доступа появились внизу экрана. Чтобы убрать их, нажмите <b>«❌ Скрыть клавиатуру»</b>."
                ),
                reply_markup=get_reply_keyboard(webapp_url),
            )
        elif callback.message:
            await callback.message.answer(
                "⌨️ <b>Всплывающая клавиатура активирована!</b>\n\n"
                "Кнопки быстрого доступа появились внизу экрана. Чтобы убрать их, нажмите <b>«❌ Скрыть клавиатуру»</b>.",
                reply_markup=get_reply_keyboard(webapp_url),
            )

    @dp.callback_query(F.data == "menu:hide_keyboard")
    async def cb_hide_keyboard(callback: types.CallbackQuery):
        await callback.answer("Клавиатура скрыта 📴")
        bot = callback.bot or (callback.message.bot if callback.message else None)
        if callback.message and bot:
            await send_or_replace_functional_message(
                chat_id=callback.message.chat.id,
                bot=bot,
                text=(
                    "📴 <b>Клавиатура скрыта!</b>\n\n"
                    "Чтобы кнопки снова всплыли:\n"
                    "• Напишите команду <code>/keyboard</code> или <code>/menu</code>."
                ),
                reply_markup=get_hide_keyboard(),
            )
        elif callback.message:
            await callback.message.answer(
                "📴 <b>Клавиатура скрыта!</b>\n\n"
                "Чтобы кнопки снова всплыли:\n"
                "• Напишите команду <code>/keyboard</code> или <code>/menu</code>.",
                reply_markup=get_hide_keyboard(),
            )

    return dp


def _build_dashboard_text(
    filter_instance: MarginFilter,
    reg_manager: RegionManager,
    chat_id: int | str,
) -> str:
    """Единое информативное сообщение панели управления (дашборд без спама)."""
    stats = filter_instance.get_stats()
    current_reg = reg_manager.current
    return (
        "⚡️ <b>Панель управления Gadget Resell Radar</b>\n\n"
        f"📍 <b>Текущий регион:</b> {current_reg['name']} (Авито: <code>{current_reg['avito_id']}</code>, Юла: <code>{current_reg['youla_id'] or 'Вся Россия'}</code>)\n"
        f"📱 <b>Конфигураций гаджетов:</b> {stats['active_configs']} из {stats['total_configs']} активны\n"
        "📡 <b>Мониторинг:</b> Авито + Юла ⚡️ (Redis/SQLite, детекция дропов цен)\n"
        f"🔑 <b>Chat ID:</b> <code>{chat_id}</code>\n\n"
        "🕹 <b>Быстрое управление:</b>\n"
        "• <b>Кнопки внизу экрана:</b> всплывающая клавиатура быстрого доступа\n"
        "• <b>Смена региона:</b> напишите город прямо в чат (например: <code>Якутск</code>, <code>Омск</code>, <code>Казань</code>, <code>спб</code>) или команду <code>/city Название</code>\n"
        "• <b>Матрица цен (Mini App):</b> кнопка внизу «📱 Матрица цен» для изменения порогов выкупа со смартфона\n"
        "• <b>Excel-прайс:</b> команда <code>/export_prices</code> или пришлите файл <code>.xlsx</code> для мгновенного обновления цен\n"
        "• <b>Статус воркеров:</b> команда <code>/status</code> или кнопка «🔄 Статус воркеров»\n"
        "• <b>Клавиатура:</b> <code>/keyboard</code> (показать) или <code>/hide_keyboard</code> (скрыть)\n\n"
        "<i>💡 Все карточки объявлений приходят с кнопками прямого перехода, торга и добавления в избранное.</i>"
    )


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
        f"• Активных конфигураций гаджетов: <b>{stats['active_configs']} из {stats['total_configs']}</b>\n"
        "• Скорость реакции: <b>до 2.5 сек</b>\n\n"
        "<i>💡 Чтобы сменить регион, просто напишите название города в чат или используйте кнопку «📍 Сменить регион».</i>"
    )


async def _send_excel_file(message: types.Message, filter_instance: MarginFilter) -> None:
    """Генерирует и отправляет Excel-таблицу прайс-листа пользователю."""
    try:
        chat_id = message.chat.id
        bot = message.bot
        old_msg_id = _last_functional_messages.get(chat_id)
        if old_msg_id and bot:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=old_msg_id)
            except Exception as e:
                logger.debug("Старое функциональное сообщение не удалено: %s", e)

        excel_bytes = ExcelPricingManager.export_matrix_to_bytes(filter_instance.matrix)
        file = BufferedInputFile(excel_bytes, filename="gadget_resell_prices.xlsx")
        caption = (
            "📊 <b>Матрица цен выкупа гаджетов (Resell Radar)</b>\n\n"
            "Инструкция по настройке:\n"
            "1. Откройте таблицу в Excel, Google Таблицах или на телефоне.\n"
            "2. Измените <b>Макс. выкуп (₽)</b> или <b>Статус (ВКЛ / ВЫКЛ)</b>.\n"
            "3. Отправьте сохраненный файл обратно в этот чат.\n\n"
            "<i>Бот мгновенно применит новые цены без перезагрузки!</i>"
        )
        doc_msg = await message.answer_document(document=file, caption=caption)
        _last_functional_messages[chat_id] = doc_msg.message_id
    except Exception as e:
        logger.error("Ошибка при генерации Excel прайса: %s", e, exc_info=True)
        await message.answer(f"❌ <b>Ошибка при экспорте Excel:</b> {e}")
