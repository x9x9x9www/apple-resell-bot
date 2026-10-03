from __future__ import annotations

from typing import TYPE_CHECKING
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

if TYPE_CHECKING:
    from core.margin_filter import MarginFilter


def get_item_keyboard(url: str) -> InlineKeyboardMarkup:
    """Генерирует инлайн-кнопку для моментального перехода к объявлению."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔗 Перейти к объявлению",
                    url=url,
                )
            ]
        ]
    )


def get_main_menu_keyboard(current_region: str = "Москва") -> InlineKeyboardMarkup:
    """Главное интерактивное меню настроек бота."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"📍 Регион поиска: {current_region}",
                    callback_data="menu:region",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📊 Выгрузить Excel-прайс",
                    callback_data="menu:export_excel",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📱 Фильтр моделей iPhone",
                    callback_data="menu:models",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔋 Политика скидок на АКБ",
                    callback_data="menu:battery",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Статус воркеров и очередей",
                    callback_data="menu:status",
                ),
            ],
        ]
    )


def get_regions_keyboard(current_key: str = "moskva") -> InlineKeyboardMarkup:
    """Меню выбора региона поиска."""
    from core.regions import POPULAR_REGIONS
    rows = []
    current_row = []
    for key, label in POPULAR_REGIONS:
        check = "✅ " if key == current_key else ""
        btn = InlineKeyboardButton(
            text=f"{check}{label}",
            callback_data=f"set_region:{key}",
        )
        current_row.append(btn)
        if len(current_row) == 2:
            rows.append(current_row)
            current_row = []
    if current_row:
        rows.append(current_row)

    rows.append([
        InlineKeyboardButton(
            text="🔍 Ввести город текстом (/city)",
            callback_data="region:custom",
        )
    ])
    rows.append([
        InlineKeyboardButton(
            text="⬅️ Назад в главное меню",
            callback_data="menu:main",
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_models_menu_keyboard(margin_filter: MarginFilter) -> InlineKeyboardMarkup:
    """Меню переключения серий iPhone с отображением статуса активных фильтров."""
    buttons = []
    for series_key, label in margin_filter.SERIES_LIST:
        is_on = margin_filter.is_series_enabled(series_key)
        icon = "✅" if is_on else "❌"
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {label}",
                callback_data=f"toggle_series:{series_key}",
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад в главное меню",
            callback_data="menu:main",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад в главное меню",
                    callback_data="menu:main",
                )
            ]
        ]
    )
