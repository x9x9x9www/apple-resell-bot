from __future__ import annotations

import asyncio
import logging
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError

from config import settings
from core.models import RawItem, ParsedIPhone
from core.parser import IPhoneNLPParser
from core.margin_filter import MarginFilter
from core.deduplicator import RedisDeduplicator
from bot.keyboards import get_item_keyboard

from aiogram.types import LinkPreviewOptions

logger = logging.getLogger(__name__)

# Официальные ID анимационных эффектов сообщений Telegram
FIRE_EFFECT_ID = "5104841245755180586"    # 🔥 Огонь / Пламя
PARTY_EFFECT_ID = "5046509860389126442"   # 🎉 Конфетти


def format_lot_message(item: ParsedIPhone) -> str:
    """
    Форматирует уведомление в строгом HTML-стиле согласно ТЗ перекупа:

    ⚡️ <b>СВЕЖИЙ ЛОТ | {Авито / Юла}</b> <i>(Только что)</i>
    или
    📉 <b>СНИЖЕНИЕ ЦЕНЫ | {Авито / Юла}</b> <i>(Продавец снизил цену!)</i>

    📱 <b>Модель:</b> iPhone 15 Pro
    💾 <b>Память:</b> 128 GB
    🔋 <b>АКБ:</b> 91%
    💰 <b>Цена:</b> 51 000 ₽ <i>(Ниже рынка на ~14 000 ₽)</i>
    📍 <b>Локация:</b> Москва, метро Сокол

    <blockquote expandable>📝 <b>Описание продавца:</b> ...</blockquote>
    """
    # Память
    storage_display = f"{item.storage_gb} GB" if item.storage_gb < 1024 else "1 TB"

    # АКБ и скидка на замену
    battery_display = f"{item.battery_health}%" if item.battery_health is not None else "Не указан"
    battery_penalty_text = ""
    if item.battery_penalty and item.battery_penalty > 0:
        penalty_fmt = f"{item.battery_penalty:,}".replace(",", " ")
        battery_penalty_text = f" <i>(Уценка на замену: -{penalty_fmt} ₽)</i>"

    # Разделитель тысяч в цене
    price_formatted = f"{item.price:,}".replace(",", " ")

    # Блок выгоды
    profit_text = ""
    if item.profit and item.profit > 0:
        profit_formatted = f"{item.profit:,}".replace(",", " ")
        profit_text = f" <i>(Ниже рынка на ~{profit_formatted} ₽)</i>"

    # Заголовок и блок цены в зависимости от снижения цены
    if item.is_price_drop and item.old_price:
        old_formatted = f"{item.old_price:,}".replace(",", " ")
        diff = item.old_price - item.price
        diff_formatted = f"{diff:,}".replace(",", " ")
        header = f"📉 <b>СНИЖЕНИЕ ЦЕНЫ | {item.platform.value}</b> <i>(Скидка -{diff_formatted} ₽!)</i>"
        price_line = f"💰 <b>Цена:</b> <s>{old_formatted} ₽</s> ➔ <b>{price_formatted} ₽</b>{profit_text}"
    else:
        header = f"⚡️ <b>СВЕЖИЙ ЛОТ | {item.platform.value}</b> <i>(Только что)</i>"
        price_line = f"💰 <b>Цена:</b> {price_formatted} ₽{profit_text}"

    message = (
        f"{header}\n\n"
        f"📱 <b>Модель:</b> {item.model}\n"
        f"💾 <b>Память:</b> {storage_display}\n"
        f"🔋 <b>АКБ:</b> {battery_display}{battery_penalty_text}\n"
        f"{price_line}\n"
        f"📍 <b>Локация:</b> {item.location}"
    )

    # Современная сворачиваемая цитата Telegram для описания продавца
    if item.description and item.description.strip():
        desc_clean = item.description.strip().replace("<", "&lt;").replace(">", "&gt;")
        if len(desc_clean) > 400:
            desc_clean = desc_clean[:400] + "..."
        message += f"\n\n<blockquote expandable>📝 <b>Описание продавца:</b>\n{desc_clean}</blockquote>"

    return message


class ItemDispatcher:
    """
    Асинхронный диспетчер обработки очереди лотов.
    Обеспечивает сквозной конвейер:
    Очередь -> NLP/Regex парсер -> Фильтр маржинальности -> Семантическая дедупликация -> Мгновенная отправка в Telegram.
    """

    def __init__(
        self,
        bot: Bot,
        queue: asyncio.Queue[RawItem],
        margin_filter: Optional[MarginFilter] = None,
        target_chat_id: Optional[int] = None,
        deduplicator: Optional[RedisDeduplicator] = None,
    ):
        self.bot = bot
        self.queue = queue
        self.margin_filter = margin_filter or MarginFilter()
        self.target_chat_id = target_chat_id or settings.TARGET_CHAT_ID
        self.deduplicator = deduplicator
        self.is_running = False

    async def start(self) -> None:
        """Запуск цикла прослушивания очереди."""
        self.is_running = True
        logger.info("Диспетчер очередей Telegram запущен. Target chat: %s", self.target_chat_id)

        while self.is_running:
            try:
                raw_item = await self.queue.get()
                try:
                    await self._process_single_item(raw_item)
                finally:
                    self.queue.task_done()
            except asyncio.CancelledError:
                logger.info("Диспетчер очереди остановлен.")
                break
            except Exception as e:
                logger.error("Критический сбой в диспетчере: %s", e, exc_info=True)

    async def _process_single_item(self, raw_item: RawItem) -> None:
        """Обрабатывает одну карточку через конвейер фильтрации и отправляет в чат."""
        # 1. NLP & Regex извлечение параметров и отсев мусора/копий
        custom_models = self.margin_filter.matrix.keys() if self.margin_filter else None
        parsed_item = IPhoneNLPParser.parse_raw_item(raw_item, custom_models=custom_models)
        if not parsed_item:
            logger.debug(
                "[%s] Пропуск лота #%s: не прошел фильтр характеристик / мусор",
                raw_item.platform.value,
                raw_item.item_id,
            )
            return

        # 2. Фильтр маржинальности (цена_лота <= лимит_цены)
        is_profitable = self.margin_filter.evaluate(parsed_item)
        if not is_profitable:
            logger.info(
                "[%s] Лот #%s '%s %dGB' за %d ₽ отклонен: %s",
                parsed_item.platform.value,
                parsed_item.item_id,
                parsed_item.model,
                parsed_item.storage_gb,
                parsed_item.price,
                parsed_item.rejection_reason,
            )
            return

        # 3. Интеллектуальная семантическая дедупликация (кросспостинг, перевыкладка, дубликаты фото)
        if self.deduplicator:
            is_dup, dup_reason = await self.deduplicator.check_and_mark_semantic_duplicate(parsed_item)
            if is_dup:
                logger.info(
                    "[%s] 🛡 ОТСЕЯН ДУБЛИКАТ #%s '%s %dGB' за %d ₽: %s",
                    parsed_item.platform.value,
                    parsed_item.item_id,
                    parsed_item.model,
                    parsed_item.storage_gb,
                    parsed_item.price,
                    dup_reason,
                )
                return

        # 4. Форматирование текста и клавиатуры с быстрыми действиями
        text = format_lot_message(parsed_item)
        keyboard = get_item_keyboard(
            url=parsed_item.url,
            item_id=parsed_item.item_id,
            model=parsed_item.model,
            price=parsed_item.price,
        )

        # 5. Определение визуального эффекта сообщения (Message Effect)
        effect_id: Optional[str] = None
        if parsed_item.profit and parsed_item.profit >= 8000:
            effect_id = FIRE_EFFECT_ID
        elif parsed_item.is_price_drop and parsed_item.old_price and (parsed_item.old_price - parsed_item.price >= 4000):
            effect_id = PARTY_EFFECT_ID

        # 6. Моментальная отправка в Telegram
        if not self.target_chat_id:
            logger.warning(
                "TARGET_CHAT_ID не настроен в .env! Сформированное сообщение:\n%s\nURL: %s",
                text,
                parsed_item.url,
            )
            return

        preview_opts = LinkPreviewOptions(
            is_disabled=False,
            url=parsed_item.url,
            prefer_large_media=True,
            show_above_text=True,
        )

        for attempt in range(1, 4):
            try:
                # Если у лота есть фотография — отправляем фотокарточку с описанием
                if parsed_item.image_url:
                    try:
                        send_kwargs = {
                            "chat_id": self.target_chat_id,
                            "photo": parsed_item.image_url,
                            "caption": text,
                            "parse_mode": "HTML",
                            "reply_markup": keyboard,
                        }
                        if effect_id:
                            send_kwargs["message_effect_id"] = effect_id

                        try:
                            await self.bot.send_photo(**send_kwargs)
                        except TelegramAPIError:
                            # Fallback без эффекта, если чат не поддерживает эффекты
                            send_kwargs.pop("message_effect_id", None)
                            await self.bot.send_photo(**send_kwargs)

                        logger.info(
                            "🔥 ФОТО-УВЕДОМЛЕНИЕ ОТПРАВЛЕНО: [%s] %s %dGB за %d ₽ (Выгода: %s ₽)",
                            parsed_item.platform.value,
                            parsed_item.model,
                            parsed_item.storage_gb,
                            parsed_item.price,
                            parsed_item.profit,
                        )
                        break
                    except TelegramAPIError as photo_err:
                        logger.warning(
                            "Не удалось отправить фото лота (%s): %s. Отправка обычным сообщением...",
                            parsed_item.image_url,
                            photo_err,
                        )

                # Отправка текстовым сообщением с LinkPreviewOptions и эффектом
                msg_kwargs = {
                    "chat_id": self.target_chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "reply_markup": keyboard,
                    "link_preview_options": preview_opts,
                }
                if effect_id:
                    msg_kwargs["message_effect_id"] = effect_id

                try:
                    await self.bot.send_message(**msg_kwargs)
                except TelegramAPIError:
                    msg_kwargs.pop("message_effect_id", None)
                    await self.bot.send_message(**msg_kwargs)

                logger.info(
                    "🔥 УВЕДОМЛЕНИЕ ОТПРАВЛЕНО: [%s] %s %dGB за %d ₽ (Выгода: %s ₽)",
                    parsed_item.platform.value,
                    parsed_item.model,
                    parsed_item.storage_gb,
                    parsed_item.price,
                    parsed_item.profit,
                )
                break
            except TelegramRetryAfter as e:
                logger.warning("Telegram Flood Control! Ожидание %d сек...", e.retry_after)
                await asyncio.sleep(e.retry_after)
            except TelegramAPIError as e:
                logger.error("Ошибка Telegram API при отправке лота #%s: %s", parsed_item.item_id, e)
                break

    def stop(self) -> None:
        self.is_running = False
