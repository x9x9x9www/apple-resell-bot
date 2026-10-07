from __future__ import annotations

import io
import json
import logging
import os
import re
import time
from typing import Optional
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    BufferedInputFile,
    FSInputFile,
    LinkPreviewOptions,
    MenuButtonWebApp,
    MenuButtonDefault,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import settings
from core.margin_filter import MarginFilter
from core.excel_manager import ExcelPricingManager
from core.regions import RegionManager
from core.link_stream import StreamManager, SearchStream, parse_search_url
from core.user_profile import (
    UserProfileManager,
    UserResellProfile,
    UserConditionRules,
    UserModelConfig,
    CustomCategory,
)
from core.favorites import favorites_manager
from bot.keyboards import (
    get_main_menu_keyboard,
    get_regions_keyboard,
    get_models_menu_keyboard,
    get_back_to_menu_keyboard,
    get_reply_keyboard,
    get_hide_keyboard,
    get_stream_control_keyboard,
    get_stream_filters_keyboard,
    get_item_keyboard,
    get_favorites_keyboard,
)

logger = logging.getLogger(__name__)

# Хранилище ID последнего сервисного/функционального сообщения в чате
# chat_id -> message_id для предотвращения спама в чате между объявлениями
_last_functional_messages: dict[int, int] = {}
# Пользователи, явно скрывшие клавиатуру кнопкой или /hide_keyboard
_keyboard_hidden_users: dict[int, bool] = {}
# Ссылка на активный экземпляр RegionManager для динамических кнопок
_active_region_manager: Optional[RegionManager] = None
# Время последней выгрузки Excel для защиты от многократных случайных нажатий
_last_excel_send_time: dict[int, float] = {}
# Хранилище ID последнего сообщения с избранным в чате
_last_favorites_messages: dict[int, int] = {}

# Слушатели для динамического добавления поисковых запросов в парсеры Авито/Юлы
_worker_query_listeners: list[Callable[[str], None]] = []


def register_worker_query_listener(callback: Callable[[str], None]) -> None:
    """Регистрирует колбэк для добавления кастомных запросов в воркеры парсинга."""
    _worker_query_listeners.append(callback)


def broadcast_worker_query(query: str) -> None:
    """Уведомляет воркеры о новом поисковом запросе (модели или бренде)."""
    clean_q = query.strip()
    if not clean_q:
        return
    for cb in _worker_query_listeners:
        try:
            cb(clean_q)
        except Exception as e:
            logger.debug("Ошибка в query listener: %s", e)

# Тексты кнопок всплывающей клавиатуры, которые нельзя воспринимать как названия городов
KNOWN_BUTTON_TEXTS = {
    "ℹ️ Информация", "ℹ️ Инфо", "Информация", "О боте",
    "⭐️ Избранное", "Избранное",
    "⚡️ Меню", "⚡️ Главное меню", "Меню",
    "📥 Скачать/загрузить Excel", "Скачать/загрузить Excel", "📥/📤 Скачать/загрузить Excel",
    "📊 Скачать Excel", "📊 Excel-прайс", "Скачать Excel",
    "ПЕРЕКУПЕР", "😎 ПЕРЕКУПЕР", "📱 ПЕРЕКУПЕР",
    "📍 Сменить регион", "📍 Регион", "Сменить регион",
    "🔄 Статус воркеров", "🔄 Статус", "Статус",
    "📱 Матрица цен", "Матрица цен", "😎 Матрица цен",
    "🔗 Мониторинг по ссылке", "🔗 Поиск по ссылке", "Поиск по ссылке",
    "❌ Скрыть клавиатуру", "🙈 Скрыть кнопки", "📴 Скрыть клавиатуру", "Скрыть клавиатуру",
}


async def cleanup_user_message(message: types.Message) -> None:
    """Удаляет входящее служебное сообщение пользователя, чтобы не спамить в чате."""
    # НИКОГДА не удаляем команду /start! В клиентах Telegram удаление /start
    # сбрасывает сессию чата и возвращает гигантскую кнопку «Начать» вместо клавиатуры.
    raw_text = (message.text or "").strip().lower()
    if raw_text.startswith("/start"):
        return

    try:
        await message.delete()
    except Exception as e:
        logger.debug("Не удалось удалить сообщение пользователя: %s", e)


from pathlib import Path

BANNER_FILE_PATH = Path(__file__).resolve().parent.parent / "assets" / "banner.jpg"


async def send_or_replace_functional_message(
    chat_id: int,
    bot: Bot,
    text: str,
    reply_markup: Optional[types.ReplyKeyboardMarkup | types.ReplyKeyboardRemove | types.InlineKeyboardMarkup] = None,
    photo: Optional[str | FSInputFile] = None,
    link_preview_options: Optional[LinkPreviewOptions] = None,
    with_banner: bool = True,
) -> types.Message:
    """
    Отправляет сервисное/функциональное сообщение бота с баннером 'ПЕРЕКУПЕР', предварительно
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

    # Если reply_markup не передан явно:
    # всегда прикрепляем всплывающую клавиатуру с актуальным текущим регионом
    if reply_markup is None:
        if _keyboard_hidden_users.get(chat_id, False):
            reply_markup = get_hide_keyboard()
        else:
            current_reg_name = _active_region_manager.current["name"] if _active_region_manager else "Москва"
            reply_markup = get_reply_keyboard(current_region=current_reg_name)

    # Прикрепляем баннер 'ПЕРЕКУПЕР' на всех служебных/функциональных сообщениях бота
    if photo is None and with_banner and BANNER_FILE_PATH.exists():
        photo = FSInputFile(str(BANNER_FILE_PATH))

    if photo:
        photo_obj = FSInputFile(photo) if isinstance(photo, str) else photo
        try:
            msg = await bot.send_photo(
                chat_id=chat_id,
                photo=photo_obj,
                caption=text,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
        except Exception as photo_err:
            logger.warning("Не удалось отправить фото баннера (%s): %s. Отправка текстом...", photo, photo_err)
            msg = await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup,
                link_preview_options=link_preview_options,
            )
    else:
        msg = await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            reply_markup=reply_markup,
            link_preview_options=link_preview_options,
        )
    _last_functional_messages[chat_id] = msg.message_id
    return msg


async def send_rich_message(
    chat_id: int,
    bot: Bot,
    text: str,
    reply_markup: Optional[types.ReplyKeyboardMarkup | types.ReplyKeyboardRemove | types.InlineKeyboardMarkup] = None,
    article_url: Optional[str] = None,
) -> types.Message:
    """
    Отправляет главное меню / сервисное сообщение с гарантированным показом баннера 'ПЕРЕКУПЕР'.
    """
    return await send_or_replace_functional_message(
        chat_id=chat_id,
        bot=bot,
        text=text,
        reply_markup=reply_markup,
        with_banner=True,
    )


async def _show_city_selection_guide(message: types.Message, reg_manager: RegionManager) -> None:
    """Отображает лаконичную инструкцию по выбору города без кнопочного спама."""
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
    bot = message.bot
    if bot:
        await send_or_replace_functional_message(chat_id=message.chat.id, bot=bot, text=text)
    else:
        await message.answer(text)


def create_bot() -> Bot:
    """Создает и настраивает экземпляр aiogram 3 Bot."""
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_bot_dispatcher(
    margin_filter: Optional[MarginFilter] = None,
    region_manager: Optional[RegionManager] = None,
    stream_manager: Optional[StreamManager] = None,
    user_profile_manager: Optional[UserProfileManager] = None,
) -> Dispatcher:
    """Создает Dispatcher команд и инлайн-обработчиков для управления ботом."""
    dp = Dispatcher()
    filter_instance = margin_filter if margin_filter is not None else MarginFilter()
    reg_manager = region_manager if region_manager is not None else RegionManager()
    stream_mgr = stream_manager if stream_manager is not None else StreamManager()
    user_profile_mgr = user_profile_manager if user_profile_manager is not None else UserProfileManager()

    global _active_region_manager
    _active_region_manager = reg_manager

    # ---------------------------------------------------------
    # КОМАНДЫ БОТА
    # ---------------------------------------------------------

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        chat_id = message.chat.id
        _keyboard_hidden_users[chat_id] = False
        webapp_url = getattr(settings, "WEBAPP_URL", "")
        text = _build_dashboard_text(filter_instance, reg_manager, chat_id)
        current_reg_name = reg_manager.current["name"]
        bot = message.bot

        # Сбрасываем кастомную кнопку меню в строке ввода, возвращая стандартное меню Telegram
        if bot:
            try:
                await bot.set_chat_menu_button(
                    chat_id=chat_id,
                    menu_button=MenuButtonDefault(),
                )
            except Exception as e:
                logger.debug("Не удалось сбросить MenuButton для %s: %s", chat_id, e)

        # Отправляем главное меню через send_rich_message (формат статьи через скрепку)
        if bot:
            await send_rich_message(
                chat_id=chat_id,
                bot=bot,
                text=text,
                reply_markup=get_reply_keyboard(current_region=current_reg_name),
            )
        else:
            photo = FSInputFile(str(BANNER_FILE_PATH)) if BANNER_FILE_PATH.exists() else None
            if photo:
                await message.answer_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=get_reply_keyboard(current_region=current_reg_name),
                )
            else:
                await message.answer(
                    text,
                    reply_markup=get_reply_keyboard(current_region=current_reg_name),
                )

    @dp.message(Command("keyboard", "kb", "buttons", "show_keyboard"))
    async def cmd_keyboard(message: types.Message):
        await cleanup_user_message(message)
        _keyboard_hidden_users[message.chat.id] = False
        current_reg_name = reg_manager.current["name"]
        text = (
            "⌨️ <b>Клавиатура быстрого доступа активирована!</b>\n\n"
            "Кнопки управления доступны внизу экрана."
        )
        bot = message.bot
        if bot:
            await send_or_replace_functional_message(
                chat_id=message.chat.id,
                bot=bot,
                text=text,
                reply_markup=get_reply_keyboard(current_region=current_reg_name),
            )
        else:
            await message.answer(text, reply_markup=get_reply_keyboard(current_region=current_reg_name))

    @dp.message(Command("hide_keyboard", "hide", "hide_buttons"))
    async def cmd_hide_keyboard(message: types.Message):
        await cleanup_user_message(message)
        _keyboard_hidden_users[message.chat.id] = True
        text = (
            "📴 <b>Клавиатура скрыта!</b>\n\n"
            "Чтобы кнопки снова появились:\n"
            "• Напишите команду <code>/keyboard</code> или <code>/info</code>."
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

    @dp.message(Command("info", "information", "menu", "settings", "help"))
    async def cmd_menu(message: types.Message):
        await cleanup_user_message(message)
        chat_id = message.chat.id
        text = _build_dashboard_text(filter_instance, reg_manager, chat_id)
        current_reg_name = reg_manager.current["name"]
        bot = message.bot
        if bot:
            await send_rich_message(
                chat_id=chat_id,
                bot=bot,
                text=text,
                reply_markup=get_reply_keyboard(current_region=current_reg_name),
            )
        else:
            photo = FSInputFile(str(BANNER_FILE_PATH)) if BANNER_FILE_PATH.exists() else None
            if photo:
                await message.answer_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=get_reply_keyboard(current_region=current_reg_name),
                )
            else:
                await message.answer(
                    text,
                    reply_markup=get_reply_keyboard(current_region=current_reg_name),
                )

    @dp.message(Command("status"))
    async def cmd_status(message: types.Message):
        await cleanup_user_message(message)
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
        await cleanup_user_message(message)
        chat_id = message.chat.id
        bot = message.bot
        raw_text = (message.text or "").strip()
        text_parts = raw_text.split(maxsplit=1)

        # Обрабатываем аргумент только если команда вызвана как /city Название или /region Название
        if len(text_parts) > 1 and text_parts[0].lower().startswith(("/city", "/region")):
            city_query = text_parts[1].strip()
            updated = reg_manager.set_region(city_query)
            if updated:
                ans = (
                    f"✅ <b>Регион поиска успешно изменен!</b>\n\n"
                    f"📍 Новый активный регион: <b>{updated['name']}</b>\n\n"
                    "Воркеры Авито и Юлы мгновенно переключились на поиск в новом регионе ⚡️"
                )
                if bot:
                    await send_or_replace_functional_message(
                        chat_id=chat_id,
                        bot=bot,
                        text=ans,
                        reply_markup=get_reply_keyboard(current_region=updated["name"]),
                    )
                else:
                    await message.answer(ans, reply_markup=get_reply_keyboard(current_region=updated["name"]))
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

        await _show_city_selection_guide(message, reg_manager)

    @dp.message(Command("export_prices"))
    async def cmd_export_prices(message: types.Message):
        await cleanup_user_message(message)
        await _send_excel_file(message, filter_instance)

    @dp.message(Command("stream", "link", "search_link"))
    async def cmd_stream(message: types.Message):
        await cleanup_user_message(message)
        chat_id = message.chat.id
        stream = stream_mgr.get_stream(chat_id)
        bot = message.bot
        if stream:
            text = _build_stream_dashboard_text(stream)
            kb = get_stream_control_keyboard(stream)
            if bot:
                await send_or_replace_functional_message(chat_id=chat_id, bot=bot, text=text, reply_markup=kb)
            else:
                await message.answer(text, reply_markup=kb)
        else:
            text = (
                "🔗 <b>Мониторинг по ссылке с Авито или Юлы</b>\n\n"
                "Вы можете привязать персональный поиск к этому чату:\n"
                "1. Откройте Авито или Юлу в браузере.\n"
                "2. Задайте город, категорию, цены и сортировку «По дате».\n"
                "3. Скопируйте ссылку и <b>отправьте её прямо в этот чат</b>!\n\n"
                "<i>Бот сразу начнет отслеживать появление лотов по этой ссылке ⚡️</i>"
            )
            if bot:
                await send_or_replace_functional_message(chat_id=chat_id, bot=bot, text=text)
            else:
                await message.answer(text)

    @dp.message(Command("stop_word", "add_stop_word"))
    async def cmd_add_stop_word(message: types.Message):
        await cleanup_user_message(message)
        chat_id = message.chat.id
        parts = (message.text or "").split(maxsplit=1)
        bot = message.bot
        if len(parts) > 1:
            word = parts[1].strip()
            ok = stream_mgr.add_blacklist_word(chat_id, word)
            st = stream_mgr.get_stream(chat_id)
            if ok:
                ans = f"✅ Стоп-слово «{word}» добавлено в черный список потока!"
            else:
                ans = f"ℹ️ Слово «{word}» уже есть в списке или поиск еще не подключен."
        else:
            st = stream_mgr.get_stream(chat_id)
            if st:
                words_list = "\n".join(f"• <code>{w}</code>" for w in st.blacklist_words)
                ans = (
                    f"⛔️ <b>Черный список стоп-слов потока:</b>\n\n"
                    f"{words_list}\n\n"
                    "<i>Чтобы добавить слово: <code>/stop_word слово</code>\n"
                    "Чтобы удалить слово: <code>/remove_word слово</code></i>"
                )
            else:
                ans = "ℹ️ В этом чате пока нет настроенного поиска. Отправьте ссылку на поиск с Авито или Юлы."
        if bot:
            await send_or_replace_functional_message(chat_id=chat_id, bot=bot, text=ans)
        else:
            await message.answer(ans)

    @dp.message(Command("remove_word", "del_stop_word"))
    async def cmd_remove_stop_word(message: types.Message):
        await cleanup_user_message(message)
        chat_id = message.chat.id
        parts = (message.text or "").split(maxsplit=1)
        bot = message.bot
        if len(parts) > 1:
            word = parts[1].strip()
            ok = stream_mgr.remove_blacklist_word(chat_id, word)
            ans = f"🗑 Стоп-слово «{word}» удалено из фильтра!" if ok else f"ℹ️ Слово «{word}» не найдено в списке."
        else:
            ans = "Укажите слово для удаления: <code>/remove_word слово</code>"
        if bot:
            await send_or_replace_functional_message(chat_id=chat_id, bot=bot, text=ans)
        else:
            await message.answer(ans)

    @dp.message(Command("del_stream", "delete_stream"))
    async def cmd_del_stream(message: types.Message):
        await cleanup_user_message(message)
        chat_id = message.chat.id
        deleted = stream_mgr.delete_stream(chat_id)
        ans = "🗑 <b>Поисковый поток отключен для этого чата.</b>" if deleted else "ℹ️ В этом чате нет активного потока."
        bot = message.bot
        if bot:
            await send_or_replace_functional_message(chat_id=chat_id, bot=bot, text=ans)
        else:
            await message.answer(ans)

    # ---------------------------------------------------------
    # СИНХРОНИЗАЦИЯ TELEGRAM MINI APP 2.0 (WEB APP DATA)
    # ---------------------------------------------------------

    @dp.message(F.web_app_data)
    async def handle_webapp_data(message: types.Message):
        """Принимает измененные настройки матрицы цен и новые модели из Telegram Mini App."""
        try:
            raw_payload = json.loads(message.web_app_data.data)
            action = raw_payload.get("action")

            if action == "set_region":
                user_id = message.chat.id
                region_name = str(raw_payload.get("region") or raw_payload.get("key") or "Москва").strip()
                region_key = str(raw_payload.get("key") or "").strip()
                updated = reg_manager.set_region(region_key) if region_key else None
                if not updated:
                    updated = reg_manager.set_region(region_name)
                if updated:
                    ans = (
                        "⚡️ <b>ПЕРЕКУПЕР</b>\n\n"
                        f"✅ <b>Регион поиска успешно переключен:</b> {updated['name']}\n"
                        "📡 <b>Мониторинг:</b> Авито + Юла ⚡️\n\n"
                        "<i>Воркеры мгновенно переключились на поиск в новом регионе.</i>"
                    )
                else:
                    ans = f"⚠️ Не удалось распознать регион: {region_name}"
                bot = message.bot
                if bot:
                    await send_or_replace_functional_message(chat_id=user_id, bot=bot, text=ans, reply_markup=get_reply_keyboard(current_region=reg_manager.current["name"]))
                else:
                    photo_obj = FSInputFile(str(BANNER_FILE_PATH)) if BANNER_FILE_PATH.exists() else None
                    if photo_obj:
                        await message.answer_photo(photo=photo_obj, caption=ans, reply_markup=get_reply_keyboard(current_region=reg_manager.current["name"]))
                    else:
                        await message.answer(ans, reply_markup=get_reply_keyboard(current_region=reg_manager.current["name"]))
                return

            if action == "save_resell_profile":
                user_id = message.chat.id
                cond_data = raw_payload.get("condition_rules", {})
                models_data = raw_payload.get("models", [])
                categories_data = raw_payload.get("categories", [])
                selected_region = raw_payload.get("region")
                reg_info = ""
                if selected_region:
                    updated_reg = reg_manager.set_region(str(selected_region).strip())
                    if updated_reg:
                        reg_info = f"📍 <b>Активный регион:</b> <b>{updated_reg['name']}</b>\n"

                condition_rules = UserConditionRules(
                    battery_threshold=int(cond_data.get("battery_threshold", 80)),
                    battery_discount=int(cond_data.get("battery_discount", 3000)),
                    allow_defects=bool(cond_data.get("allow_defects", False)),
                    defect_discount=int(cond_data.get("defect_discount", 8000)),
                    ignore_no_face_id=bool(cond_data.get("ignore_no_face_id", True)),
                    ignore_mdm_rsim=bool(cond_data.get("ignore_mdm_rsim", True)),
                    ignore_replicas=bool(cond_data.get("ignore_replicas", True)),
                )

                profile = user_profile_mgr.get_or_create_profile(user_id)
                profile.condition_rules = condition_rules

                # Сохраняем пользовательские папки/категории
                parsed_categories = []
                for c in categories_data:
                    c_name = str(c.get("name", "")).strip()
                    c_id = str(c.get("id", "")).strip() or c_name.lower().replace(" ", "_")
                    c_icon = str(c.get("icon", "📱")).strip()
                    if c_name:
                        parsed_categories.append(CustomCategory(id=c_id, name=c_name, icon=c_icon))
                        # Автоматически регистрируем поисковый запрос бренда на Авито и Юле
                        broadcast_worker_query(c_name)
                profile.categories = parsed_categories

                deleted_keys = set(raw_payload.get("deleted_keys", []))
                remaining_keys = raw_payload.get("remaining_keys")
                remaining_set = set(remaining_keys) if (isinstance(remaining_keys, list) and remaining_keys) else None

                # 1. Удаление моделей и конфигураций по явному списку deleted_keys
                for del_key in deleted_keys:
                    if "_" in del_key:
                        m_part, s_part = del_key.rsplit("_", 1)
                        if m_part in filter_instance.matrix:
                            filter_instance.matrix[m_part].pop(s_part, None)
                            if not filter_instance.matrix[m_part]:
                                del filter_instance.matrix[m_part]
                        if m_part in profile.models:
                            profile.models[m_part].pop(s_part, None)
                            if not profile.models[m_part]:
                                del profile.models[m_part]
                    if del_key in filter_instance.matrix:
                        del filter_instance.matrix[del_key]
                    if del_key in profile.models:
                        del profile.models[del_key]

                # 2. Очистка конфигураций, отсутствующих в remaining_keys (если передан список оставшихся)
                if remaining_set is not None:
                    for m_name in list(filter_instance.matrix.keys()):
                        for s_val in list(filter_instance.matrix[m_name].keys()):
                            if f"{m_name}_{s_val}" not in remaining_set:
                                filter_instance.matrix[m_name].pop(s_val, None)
                        if not filter_instance.matrix[m_name]:
                            del filter_instance.matrix[m_name]

                    for m_name in list(profile.models.keys()):
                        for s_val in list(profile.models[m_name].keys()):
                            if f"{m_name}_{s_val}" not in remaining_set:
                                profile.models[m_name].pop(s_val, None)
                        if not profile.models[m_name]:
                            del profile.models[m_name]

                # 3. Сохранение измененных/добавленных моделей и цен
                for item in models_data:
                    if isinstance(item, (list, tuple)) and len(item) >= 3:
                        m_name = str(item[0]).strip()
                        s_val = int(item[1]) if str(item[1]).isdigit() else item[1]
                        m_buy = int(item[2])
                        en = bool(item[3]) if len(item) > 3 else True
                        cat = str(item[4]).strip() if len(item) > 4 else ""
                        mkt = int(item[5]) if len(item) > 5 and (isinstance(item[5], (int, float)) or str(item[5]).isdigit()) else (int(m_buy * 1.2) if m_buy > 0 else 0)
                        min_p = 0
                    elif isinstance(item, dict):
                        m_name = str(item.get("model", "")).strip()
                        s_val = int(item.get("storage", 128)) if str(item.get("storage", "")).isdigit() else 128
                        m_buy = int(item.get("price") or item.get("max_buy", 0))
                        mkt = int(item.get("market") or (int(m_buy * 1.2) if m_buy > 0 else 0))
                        en = bool(item.get("enabled", True))
                        min_p = int(item.get("min_price", 0))
                        cat = str(item.get("category", "")).strip()
                    else:
                        continue

                    if not m_name:
                        continue

                    if m_name not in profile.models:
                        profile.models[m_name] = {}
                    profile.models[m_name][str(s_val)] = UserModelConfig(
                        model=m_name,
                        storage=s_val,
                        enabled=en,
                        min_price=min_p,
                        max_buy=m_buy,
                        market=mkt,
                        category=cat,
                    )
                    if en:
                        # Добавляем в поисковый цикл воркеров
                        broadcast_worker_query(m_name)

                    # Синхронизируем также глобальную матрицу
                    if m_name not in filter_instance.matrix:
                        filter_instance.matrix[m_name] = {}
                    filter_instance.matrix[m_name][str(s_val)] = {
                        "max_buy": m_buy,
                        "market": mkt,
                        "enabled": en,
                    }

                user_profile_mgr.save_profile(profile)
                filter_instance.save_matrix()
                filter_instance.reload_matrix()

                front_active_count = raw_payload.get("active_count")
                if front_active_count is not None and isinstance(front_active_count, int):
                    active_count = front_active_count
                else:
                    active_count = filter_instance.get_stats().get("active_configs", 0)

                active_reg_name = reg_manager.current["name"]
                text = (
                    "⚡️ <b>ПЕРЕКУПЕР</b>\n\n"
                    "✅ <b>Настройки и цены успешно сохранены!</b>\n"
                    f"📍 <b>Активный регион:</b> {active_reg_name}\n"
                    f"📱 <b>Активных конфигураций:</b> {active_count}\n\n"
                    "⚡️ <i>Мониторинг Авито и Юлы обновлен</i>"
                )
                bot = message.bot
                if bot:
                    await send_or_replace_functional_message(
                        chat_id=message.chat.id,
                        bot=bot,
                        text=text,
                        reply_markup=get_reply_keyboard(current_region=active_reg_name),
                    )
                else:
                    photo_obj = FSInputFile(str(BANNER_FILE_PATH)) if BANNER_FILE_PATH.exists() else None
                    if photo_obj:
                        await message.answer_photo(
                            photo=photo_obj,
                            caption=text,
                            reply_markup=get_reply_keyboard(current_region=active_reg_name),
                        )
                    else:
                        await message.answer(
                            text,
                            reply_markup=get_reply_keyboard(current_region=active_reg_name),
                        )

            elif action in ("update_matrix", "sync_matrix"):
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
        await cleanup_user_message(message)
        await cmd_hide_keyboard(message)

    @dp.message(F.text.in_({"ℹ️ Информация", "ℹ️ Инфо", "Информация", "О боте", "⚡️ Меню", "⚡️ Главное меню", "Меню"}))
    async def handle_reply_menu_btn(message: types.Message):
        await cleanup_user_message(message)
        await cmd_menu(message)

    @dp.message(F.text.startswith("📍 Регион") | F.text.in_({"📍 Сменить регион", "📍 Регион", "Сменить регион"}))
    async def handle_reply_region_btn(message: types.Message):
        await cleanup_user_message(message)
        await _show_city_selection_guide(message, reg_manager)

    @dp.message(F.text.in_({
        "📥 Скачать/загрузить Excel", "Скачать/загрузить Excel", "📥/📤 Скачать/загрузить Excel",
        "📊 Скачать Excel", "📊 Excel-прайс", "Скачать Excel", "/export_prices"
    }))
    async def handle_reply_export_btn(message: types.Message):
        await cleanup_user_message(message)
        await _send_excel_file(message, filter_instance)

    @dp.message(Command("favorites", "fav", "bookmarks", "saved"))
    async def cmd_favorites(message: types.Message):
        await cleanup_user_message(message)
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else chat_id
        text, kb = _build_favorites_view(user_id)
        bot = message.bot
        if bot:
            old_fav_id = _last_favorites_messages.get(chat_id)
            if old_fav_id:
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=old_fav_id)
                except Exception:
                    pass
            fav_msg = await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=kb,
                parse_mode="HTML",
            )
            _last_favorites_messages[chat_id] = fav_msg.message_id
        else:
            await message.answer(text, reply_markup=kb)

    @dp.message(F.text.in_({"⭐️ Избранное", "Избранное", "⭐️ Закладки", "Закладки"}))
    async def handle_reply_favorites_btn(message: types.Message):
        await cleanup_user_message(message)
        await cmd_favorites(message)

    @dp.message(F.text.in_({"🔄 Статус воркеров", "🔄 Статус", "Статус"}))
    async def handle_reply_status_btn(message: types.Message):
        await cleanup_user_message(message)
        await cmd_status(message)

    @dp.message(F.text.in_({
        "ПЕРЕКУПЕР", "😎 ПЕРЕКУПЕР", "📱 ПЕРЕКУПЕР",
        "📱 Матрица цен", "Матрица цен", "😎 Матрица цен"
    }))
    async def handle_reply_webapp_btn(message: types.Message):
        await cleanup_user_message(message)
        webapp_url = getattr(settings, "WEBAPP_URL", "")
        if webapp_url:
            text = (
                "📱 <b>ПЕРЕКУПЕР (Telegram Mini App)</b>\n\n"
                "Вы можете управлять порогами цен, добавлять новые модели, папки и менять статусы выкупа со смартфона.\n\n"
                f"🔗 <b>Открыть в браузере или Telegram:</b>\n{webapp_url}\n\n"
                "<i>💡 Кнопка «ПЕРЕКУПЕР» доступна на клавиатуре и по иконке «😎» в строке ввода сообщения.</i>"
            )
        else:
            text = (
                "📱 <b>ПЕРЕКУПЕР (Mini App):</b>\n\n"
                "URL веб-приложения не задан в конфигурации (.env WEBAPP_URL).\n"
                "Вы можете выгрузить прайс-лист в Excel командой <code>/export_prices</code>."
            )
        bot = message.bot
        if bot:
            await send_or_replace_functional_message(chat_id=message.chat.id, bot=bot, text=text)
        else:
            await message.answer(text)

    # ---------------------------------------------------------
    # МОНИТОРИНГ ПО ССЫЛКЕ И СОБЫТИЯ ГРУПП
    # ---------------------------------------------------------

    @dp.my_chat_member()
    async def on_my_chat_member_updated(event: types.ChatMemberUpdated):
        """Приветствие при добавлении бота в новую группу или супергруппу (беседу)."""
        if event.new_chat_member.status in ("member", "administrator"):
            welcome_text = (
                "👋 <b>Всем привет! Бот по перекупу активирован в этой беседе!</b>\n\n"
                "Чтобы запустить мониторинг свежих лотов в эту группу:\n"
                "1. Настройте поиск на Авито или Юле (город, цены, сортировка «По дате»).\n"
                "2. Скопируйте ссылку из браузера.\n"
                "3. <b>Отправьте ссылку прямо в эту беседу!</b>\n\n"
                "<i>Бот начнет отслеживать все выгодные предложения и присылать их сюда ⚡️</i>"
            )
            try:
                await event.bot.send_message(
                    chat_id=event.chat.id,
                    text=welcome_text,
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.debug("Не удалось отправить приветствие в группу %s: %s", event.chat.id, e)

    @dp.message(F.text.regexp(r"(https?://)?([a-zA-Z0-9-]+\.)?(avito\.ru|youla\.ru)/\S+"))
    async def handle_stream_url(message: types.Message):
        """Перехватывает ссылки на поиск Авито / Юлы и создает персональный поток."""
        await cleanup_user_message(message)
        chat_id = message.chat.id
        bot = message.bot
        raw_text = (message.text or "").strip()

        # Извлекаем URL регулярным выражением
        url_match = re.search(r"(?:https?://)?(?:[a-zA-Z0-9-]+\.)?(?:avito\.ru|youla\.ru)/\S+", raw_text)
        url = url_match.group(0) if url_match else raw_text

        stream = stream_mgr.create_or_update_stream(chat_id=chat_id, url=url)
        if not stream:
            err_text = (
                "❌ <b>Не удалось распознать ссылку на поиск!</b>\n\n"
                "Убедитесь, что ссылка ведет на поиск или каталог <b>Авито</b> или <b>Юлы</b>.\n"
                "Пример: <code>https://www.avito.ru/moskva/telefony/apple-ASgBAgICAUSTAcYOtA0?s=104</code>"
            )
            if bot:
                await send_or_replace_functional_message(chat_id=chat_id, bot=bot, text=err_text)
            else:
                await message.answer(err_text)
            return

        dash_text = _build_stream_dashboard_text(stream)
        kb = get_stream_control_keyboard(stream)
        if bot:
            await send_or_replace_functional_message(chat_id=chat_id, bot=bot, text=dash_text, reply_markup=kb)
        else:
            await message.answer(dash_text, reply_markup=kb)

    # ---------------------------------------------------------
    # ВВОД ГОРОДА ТЕКСТОМ
    # ---------------------------------------------------------

    @dp.message(F.text & ~F.text.startswith("/"))
    async def handle_city_text_search(message: types.Message):
        query = (message.text or "").strip()
        if not query or len(query) > 40:
            return

        # Игнорируем нажатия на кнопки всплывающей клавиатуры, если они дошли сюда
        if (
            query in KNOWN_BUTTON_TEXTS
            or query.startswith(("📍", "ℹ️", "📊", "🔄", "⚡️", "❌", "📥", "😎"))
        ):
            return

        # Удаляем входящее сообщение пользователя, чтобы не спамить в чате
        await cleanup_user_message(message)

        chat_id = message.chat.id
        bot = message.bot

        # Пробуем распознать город или алиас
        updated = reg_manager.set_region(query)
        if updated:
            ans = (
                f"✅ <b>Регион поиска успешно переключен на: {updated['name']}!</b>\n\n"
                "Воркеры мгновенно начали мониторинг в новом регионе ⚡️"
            )
            if bot:
                await send_or_replace_functional_message(
                    chat_id=chat_id,
                    bot=bot,
                    text=ans,
                    reply_markup=get_reply_keyboard(current_region=updated["name"]),
                )
            else:
                await message.answer(ans, reply_markup=get_reply_keyboard(current_region=updated["name"]))
            return

        # Если прямого совпадения нет, ищем подсказки
        matches = reg_manager.find_cities(query)
        if matches:
            hints = "\n".join(f"• <code>/city {m[1]['name']}</code>" for m in matches[:5])
            ans = (
                f"🔍 По запросу «{query}» найдены города:\n\n{hints}\n\n"
                "<i>Напишите точный город из списка выше.</i>"
            )
        else:
            ans = (
                f"❌ Город «{query}» не найден в базе.\n\n"
                "<i>Напишите точное название города (например: <code>Якутск</code>, <code>Казань</code>, <code>Омск</code>) или <code>/city Россия</code>.</i>"
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
        if callback.message:
            try:
                await callback.message.delete()
            except Exception:
                pass
            await cmd_menu(callback.message)

    @dp.callback_query(F.data == "fav_close")
    async def cb_fav_close(callback: types.CallbackQuery):
        await callback.answer()
        if callback.message:
            try:
                await callback.message.delete()
            except Exception:
                pass

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
            if callback.message:
                try:
                    await callback.message.delete()
                except Exception:
                    pass
                await cmd_menu(callback.message)
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
        user_id = callback.from_user.id
        item_id = callback.data.split(":")[1]
        msg = callback.message

        if favorites_manager.is_favorite(user_id, item_id):
            favorites_manager.remove_favorite(user_id, item_id)
            await callback.answer("🗑 Лот удален из избранного", show_alert=False)
            is_fav = False
        else:
            cached = favorites_manager.get_cached_lot(item_id)
            if not cached:
                model = "Гаджет"
                price = 0
                url = ""
                content = ""
                if isinstance(msg, types.Message):
                    content = msg.text or msg.caption or ""
                for line in content.split("\n"):
                    if "Модель:" in line:
                        model = line.replace("Модель:", "").strip()
                    elif "Цена:" in line:
                        p_match = re.search(r"(\d[\d\s]*)\s*₽", line)
                        if p_match:
                            price = int(re.sub(r"\s+", "", p_match.group(1)))
                if isinstance(msg, types.Message) and msg.reply_markup and msg.reply_markup.inline_keyboard:
                    for row in msg.reply_markup.inline_keyboard:
                        for btn in row:
                            if btn.url:
                                url = btn.url
                                break
                cached = {
                    "item_id": item_id,
                    "model": model,
                    "price": price,
                    "url": url,
                    "platform": "Юла" if "Юла" in content else "Авито",
                }
            favorites_manager.add_favorite(user_id, cached)
            await callback.answer("⭐️ Лот сохранен в Избранное!", show_alert=False)
            is_fav = True

        if isinstance(msg, types.Message) and msg.reply_markup and msg.reply_markup.inline_keyboard:
            url = ""
            for row in msg.reply_markup.inline_keyboard:
                for btn in row:
                    if btn.url:
                        url = btn.url
                        break
            if url:
                try:
                    await msg.edit_reply_markup(
                        reply_markup=get_item_keyboard(
                            url=url,
                            item_id=item_id,
                            is_favorite=is_fav,
                        )
                    )
                except Exception as e:
                    logger.debug("Не удалось обновить клавиатуру лота: %s", e)

    @dp.callback_query(F.data.startswith("fav_del:"))
    async def cb_fav_del(callback: types.CallbackQuery):
        parts = callback.data.split(":")
        item_id = parts[1]
        page = int(parts[2]) if len(parts) > 2 else 0
        favorites_manager.remove_favorite(callback.from_user.id, item_id)
        await callback.answer("Лот удален из избранного 🗑")
        text, kb = _build_favorites_view(callback.from_user.id, page=page)
        if isinstance(callback.message, types.Message):
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
            except Exception:
                pass

    @dp.callback_query(F.data.startswith("fav_page:"))
    async def cb_fav_page(callback: types.CallbackQuery):
        page = int(callback.data.split(":")[1])
        await callback.answer()
        text, kb = _build_favorites_view(callback.from_user.id, page=page)
        if isinstance(callback.message, types.Message):
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
            except Exception:
                pass

    @dp.callback_query(F.data == "fav_clear")
    async def cb_fav_clear(callback: types.CallbackQuery):
        count = favorites_manager.clear_favorites(callback.from_user.id)
        await callback.answer(f"Очищено {count} лотов 🗑")
        text, kb = _build_favorites_view(callback.from_user.id, page=0)
        if isinstance(callback.message, types.Message):
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
            except Exception:
                pass

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
        bot = callback.bot or (callback.message.bot if callback.message else None)
        current_reg_name = reg_manager.current["name"]
        text = (
            "⌨️ <b>Клавиатура быстрого доступа активирована!</b>\n\n"
            "Кнопки управления доступны внизу экрана."
        )
        if callback.message and bot:
            await send_or_replace_functional_message(
                chat_id=callback.message.chat.id,
                bot=bot,
                text=text,
                reply_markup=get_reply_keyboard(current_region=current_reg_name),
            )
        elif callback.message:
            await callback.message.answer(
                text,
                reply_markup=get_reply_keyboard(current_region=current_reg_name),
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

    @dp.callback_query(F.data.startswith("stream_toggle:"))
    async def cb_stream_toggle(callback: types.CallbackQuery):
        cid = int(callback.data.split(":")[1])
        new_active = stream_mgr.toggle_active(cid)
        st = stream_mgr.get_stream(cid)
        if st and callback.message:
            await callback.answer("Поток возобновлен ▶️" if new_active else "Поток приостановлен ⏸")
            try:
                await callback.message.edit_text(
                    text=_build_stream_dashboard_text(st),
                    reply_markup=get_stream_control_keyboard(st),
                    parse_mode="HTML",
                )
            except Exception:
                pass
        else:
            await callback.answer("Стрим не найден")

    @dp.callback_query(F.data.startswith("stream_filters:"))
    async def cb_stream_filters(callback: types.CallbackQuery):
        cid = int(callback.data.split(":")[1])
        st = stream_mgr.get_stream(cid)
        if st and callback.message:
            await callback.answer()
            text = (
                f"⚙️ <b>Настройка фильтров потока:</b> <code>{st.title}</code>\n\n"
                "Нажимайте на кнопки, чтобы включать или отключать нужные правила:\n\n"
                "• <b>Только с фото:</b> отсекает объявления без снимков\n"
                "• <b>Без брони (резерва):</b> отсекает лоты с оформленной Авито Доставкой\n"
                "• <b>Без рекламы/промо:</b> отсекает продвигаемые платные объявления\n"
                "• <b>Только с описанием:</b> отсекает пустые карточки"
            )
            try:
                await callback.message.edit_text(
                    text=text,
                    reply_markup=get_stream_filters_keyboard(st),
                    parse_mode="HTML",
                )
            except Exception:
                pass
        else:
            await callback.answer("Стрим не найден")

    @dp.callback_query(F.data.startswith("sfilter:"))
    async def cb_sfilter_toggle(callback: types.CallbackQuery):
        parts = callback.data.split(":")
        cid = int(parts[1])
        filter_key = parts[2]
        new_val = stream_mgr.toggle_filter(cid, filter_key)
        st = stream_mgr.get_stream(cid)
        if st and callback.message:
            status_word = "ВКЛЮЧЕН ✅" if new_val else "ВЫКЛЮЧЕН ❌"
            await callback.answer(f"Фильтр {status_word}")
            try:
                await callback.message.edit_reply_markup(
                    reply_markup=get_stream_filters_keyboard(st),
                )
            except Exception:
                pass
        else:
            await callback.answer()

    @dp.callback_query(F.data.startswith("stream_back:"))
    async def cb_stream_back(callback: types.CallbackQuery):
        cid = int(callback.data.split(":")[1])
        st = stream_mgr.get_stream(cid)
        if st and callback.message:
            await callback.answer()
            try:
                await callback.message.edit_text(
                    text=_build_stream_dashboard_text(st),
                    reply_markup=get_stream_control_keyboard(st),
                    parse_mode="HTML",
                )
            except Exception:
                pass
        else:
            await callback.answer("Стрим не найден")

    @dp.callback_query(F.data.startswith("stream_words:"))
    async def cb_stream_words(callback: types.CallbackQuery):
        cid = int(callback.data.split(":")[1])
        st = stream_mgr.get_stream(cid)
        if st and callback.message:
            await callback.answer()
            words_formatted = "\n".join(f"• <code>{w}</code>" for w in st.blacklist_words)
            text = (
                f"⛔️ <b>Черный список стоп-слов ({len(st.blacklist_words)}):</b>\n\n"
                f"{words_formatted}\n\n"
                "<b>Как управлять стоп-словами:</b>\n"
                "• Добавить: отправьте команду <code>/stop_word слово</code>\n"
                "• Удалить: отправьте команду <code>/remove_word слово</code>"
            )
            back_kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="⬅️ Назад к потоку", callback_data=f"stream_back:{cid}")
            ]])
            try:
                await callback.message.edit_text(
                    text=text,
                    reply_markup=back_kb,
                    parse_mode="HTML",
                )
            except Exception:
                pass
        else:
            await callback.answer("Стрим не найден")

    @dp.callback_query(F.data.startswith("stream_delete:"))
    async def cb_stream_delete(callback: types.CallbackQuery):
        cid = int(callback.data.split(":")[1])
        deleted = stream_mgr.delete_stream(cid)
        if deleted:
            await callback.answer("Поток успешно отключен 🗑")
            if callback.message:
                try:
                    await callback.message.edit_text(
                        "🗑 <b>Поисковый поток отключен.</b>\n\nЧтобы подключить новый поиск, просто пришлите ссылку с Авито или Юлы в этот чат.",
                        parse_mode="HTML",
                    )
                except Exception:
                    pass
        else:
            await callback.answer("Стрим уже отключен")

    @dp.callback_query(F.data == "menu:stream")
    async def cb_menu_stream(callback: types.CallbackQuery):
        cid = callback.message.chat.id if callback.message else 0
        st = stream_mgr.get_stream(cid)
        await callback.answer()
        if st and callback.message:
            try:
                await callback.message.edit_text(
                    text=_build_stream_dashboard_text(st),
                    reply_markup=get_stream_control_keyboard(st),
                    parse_mode="HTML",
                )
            except Exception:
                pass
        elif callback.message:
            guide = (
                "🔗 <b>Мониторинг по ссылке (Авито & Юла)</b>\n\n"
                "В этом чате пока нет подключенного поиска по ссылке.\n\n"
                "<b>Как подключить:</b>\n"
                "1. Откройте Авито или Юлу в браузере или приложении.\n"
                "2. Настройте город, фильтры цен и категорию (например, iPhone до 60 000 ₽ с сортировкой «По дате»).\n"
                "3. Скопируйте ссылку и <b>отправьте её прямо в этот чат</b>!\n\n"
                "<i>Бот автоматически распознает ссылку и включит поток мониторинга ⚡️</i>"
            )
            back_kb = get_back_to_menu_keyboard()
            try:
                await callback.message.edit_text(text=guide, reply_markup=back_kb, parse_mode="HTML")
            except Exception:
                pass

    return dp


def _build_stream_dashboard_text(stream: SearchStream) -> str:
    """Генерирует форматированный статус и настройки стрима мониторинга."""
    status_icon = "🟢 Активен" if stream.is_active else "⏸ На паузе"

    price_info = "любая"
    if stream.pmin and stream.pmax:
        price_info = f"{stream.pmin:,} – {stream.pmax:,} ₽".replace(",", " ")
    elif stream.pmax:
        price_info = f"до {stream.pmax:,} ₽".replace(",", " ")
    elif stream.pmin:
        price_info = f"от {stream.pmin:,} ₽".replace(",", " ")

    stop_words_preview = ", ".join(stream.blacklist_words[:5])
    if len(stream.blacklist_words) > 5:
        stop_words_preview += "..."

    return (
        f"🎯 <b>ПОИСКОВЫЙ ПОТОК:</b> <code>{stream.title}</code>\n\n"
        f"🔗 <b>Платформа:</b> {stream.platform.value}\n"
        f"📍 <b>Город/Регион:</b> {stream.city_name}\n"
        f"🔍 <b>Поисковый запрос:</b> <code>{stream.query or 'Все объявления категории'}</code>\n"
        f"💰 <b>Ценовой диапазон:</b> {price_info}\n"
        f"📊 <b>Статус:</b> {status_icon}\n"
        f"📦 <b>Передано в чат:</b> {stream.lots_found} лотов\n\n"
        "⚙️ <b>Параметры фильтрации:</b>\n"
        f"• Только с фото: {'✅ ВКЛ' if stream.filter_only_photo else '❌ ВЫКЛ'}\n"
        f"• Без брони/резерва: {'✅ ВКЛ' if stream.filter_exclude_reserved else '❌ ВЫКЛ'}\n"
        f"• Без рекламы/промо: {'✅ ВКЛ' if stream.filter_exclude_promo else '❌ ВЫКЛ'}\n"
        f"• Только с описанием: {'✅ ВКЛ' if stream.filter_only_desc else '❌ ВЫКЛ'}\n"
        f"• Стоп-слова ({len(stream.blacklist_words)} шт.): <i>{stop_words_preview}</i>\n\n"
        "<i>⚡️ Бот проверяет этот поиск каждые 3–5 секунд. Новые выгодные предложения публикуются прямо в этот чат!</i>"
    )


def _build_favorites_view(user_id: int | str, page: int = 0, per_page: int = 5) -> tuple[str, InlineKeyboardMarkup]:
    """Формирует текст и инлайн-клавиатуру для просмотра сохраненных лотов пользователя."""
    favs = favorites_manager.get_favorites(user_id)
    if not favs:
        text = (
            "⭐️ <b>Ваше избранное пока пусто</b>\n\n"
            "Нажимайте кнопку «⭐️ В избранное» под любым объявлением в чате, чтобы сохранить его сюда и вернуться к покупке в удобный момент!"
        )
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Закрыть", callback_data="fav_close")]
            ]
        )
        return text, kb

    total_pages = max(1, (len(favs) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    start_idx = page * per_page
    page_favs = favs[start_idx : start_idx + per_page]

    lines = [
        f"⭐️ <b>Ваши избранные лоты (всего: {len(favs)}):</b>\n"
    ]
    for idx, item in enumerate(page_favs, start=start_idx + 1):
        price_val = item.get("price")
        price_fmt = f"{price_val:,}".replace(",", " ") if price_val else "Цена не указана"
        platform = item.get("platform", "Авито")
        model = item.get("model", "Гаджет")
        loc = f" 📍 {item['location']}" if item.get("location") else ""
        lines.append(f"{idx}. <b>{model}</b> — <b>{price_fmt} ₽</b> <i>({platform})</i>{loc}")

    lines.append("\n<i>💡 Нажмите кнопку с названием лота внизу, чтобы открыть его на источнике, или 🗑, чтобы удалить из списка.</i>")
    text = "\n".join(lines)
    kb = get_favorites_keyboard(favs, page=page, per_page=per_page)
    return text, kb


def _build_dashboard_text(
    filter_instance: MarginFilter,
    reg_manager: RegionManager,
    chat_id: int | str = "",
) -> str:
    """Единое информативное сообщение панели управления (дашборд без спама)."""
    current_reg = reg_manager.current
    return (
        "⚡️ <b>ПЕРЕКУПЕР</b>\n\n"
        f"📍 <b>Текущий регион:</b> {current_reg['name']}\n"
        "📡 <b>Мониторинг:</b> Авито + Юла"
    )


def _build_status_text(
    filter_instance: MarginFilter,
    region_manager: Optional[RegionManager] = None,
) -> str:
    """Генерирует форматированный статус работы мониторинга."""
    stats = filter_instance.get_stats()
    region_name = region_manager.current["name"] if region_manager else "Москва"
    return (
        "🟢 <b>Статус мониторинга лотов:</b>\n\n"
        f"• Текущий регион: <b>{region_name}</b>\n"
        "• Воркер Авито: <b>АКТИВЕН ⚡️</b> (sort=104, первые 20 позиций)\n"
        "• Воркер Юла: <b>АКТИВЕН ⚡️</b> (web-api & REST выдача)\n"
        "• Дедупликация: <b>Redis + SQLite Local Fallback (48h)</b>\n"
        "• Детекция снижения цен: <b>АКТИВНА 📉</b>\n"
        "• Фотокарточки объявлений: <b>АКТИВНЫ 📸</b>\n"
        f"• Активных конфигураций гаджетов: <b>{stats['active_configs']} из {stats['total_configs']}</b>\n"
        "• Скорость реакции: <b>до 2.5 сек</b>\n\n"
        "<i>💡 Чтобы сменить регион, просто напишите название города в чат или используйте команду /city.</i>"
    )


async def _send_excel_file(message: types.Message, filter_instance: MarginFilter) -> None:
    """Генерирует и отправляет Excel-таблицу прайс-листа пользователю."""
    try:
        chat_id = message.chat.id
        bot = message.bot
        now = time.time()
        # Защита от спама/двойного клика: если файл запрашивался меньше 2.5 сек назад, игнорируем
        if now - _last_excel_send_time.get(chat_id, 0.0) < 2.5:
            return
        _last_excel_send_time[chat_id] = now

        old_msg_id = _last_functional_messages.get(chat_id)
        if old_msg_id and bot:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=old_msg_id)
            except Exception as e:
                logger.debug("Старое функциональное сообщение не удалено: %s", e)

        excel_bytes = ExcelPricingManager.export_matrix_to_bytes(filter_instance.matrix)
        file = BufferedInputFile(excel_bytes, filename="gadget_resell_prices.xlsx")
        caption = (
            "📥 <b>Скачать / Загрузить Excel (Матрица цен)</b>\n\n"
            "Инструкция по настройке:\n"
            "1. Откройте прикрепленную таблицу в Excel, Google Таблицах или на телефоне.\n"
            "2. Измените <b>Макс. выкуп (₽)</b> или <b>Статус (ВКЛ / ВЫКЛ)</b>.\n"
            "3. <b>Отправьте сохраненный файл обратно в этот чат</b> — бот мгновенно обновит базу!\n\n"
            "<i>💡 Также вы можете управлять всеми ценами и моделями в Mini App «ПЕРЕКУПЕР» (кнопка 😎).</i>"
        )
        if _keyboard_hidden_users.get(chat_id, False):
            reply_markup = get_hide_keyboard()
        else:
            current_reg_name = _active_region_manager.current["name"] if _active_region_manager else "Москва"
            reply_markup = get_reply_keyboard(current_region=current_reg_name)

        doc_msg = await message.answer_document(
            document=file,
            caption=caption,
            reply_markup=reply_markup,
        )
        _last_functional_messages[chat_id] = doc_msg.message_id
    except Exception as e:
        logger.error("Ошибка при генерации Excel прайса: %s", e, exc_info=True)
        await message.answer(f"❌ <b>Ошибка при экспорте Excel:</b> {e}")
