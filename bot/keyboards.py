from __future__ import annotations

from typing import TYPE_CHECKING
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

if TYPE_CHECKING:
    from core.margin_filter import MarginFilter


def get_item_keyboard(
    url: str,
    item_id: str = "",
    model: str = "",
    price: int = 0,
) -> InlineKeyboardMarkup:
    """Генерирует инлайн-кнопки для лота: быстрый переход, торг и избранное."""
    rows = [
        [
            InlineKeyboardButton(
                text="⚡️ Перейти к объявлению",
                url=url,
            )
        ]
    ]

    # Интерактивные кнопки действий
    if item_id:
        rows.append([
            InlineKeyboardButton(
                text="💬 Шаблон торга",
                callback_data=f"bargain:{item_id}:{price}",
            ),
            InlineKeyboardButton(
                text="⭐️ В избранное",
                callback_data=f"fav:{item_id}",
            ),
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_main_menu_keyboard(
    current_region: str = "Москва",
    webapp_url: str = "",
) -> InlineKeyboardMarkup:
    """Главное интерактивное меню настроек бота."""
    rows = [
        [
            InlineKeyboardButton(
                text=f"📍 Регион поиска: {current_region}",
                callback_data="menu:region",
            ),
        ],
    ]

    # Если задан URL Web App — добавляем кнопку прямого открытия Mini App
    if webapp_url:
        rows.append([
            InlineKeyboardButton(
                text="📱 Матрица цен (Mini App)",
                web_app=WebAppInfo(url=webapp_url),
            )
        ])
    else:
        rows.append([
            InlineKeyboardButton(
                text="📱 Матрица цен (Web App)",
                callback_data="menu:webapp_info",
            )
        ])

    rows.extend([
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
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


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
