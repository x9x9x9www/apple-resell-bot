from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    WebAppInfo,
)

from config import settings

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
    webapp_url: Optional[str] = None,
) -> InlineKeyboardMarkup:
    """Главное интерактивное меню настроек бота."""
    if webapp_url is None:
        webapp_url = getattr(settings, "WEBAPP_URL", "")
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
                text="🔗 Мониторинг по ссылке (Авито/Юла)",
                callback_data="menu:stream",
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
                text="⚡️ Фильтр гаджетов и моделей",
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
        [
            InlineKeyboardButton(
                text="⌨️ Показать кнопки",
                callback_data="menu:show_keyboard",
            ),
            InlineKeyboardButton(
                text="📴 Скрыть кнопки",
                callback_data="menu:hide_keyboard",
            ),
        ],
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_reply_keyboard(
    current_region: str = "Москва",
    webapp_url: Optional[str] = None,
) -> ReplyKeyboardMarkup:
    """
    Всплывающая клавиатура быстрого доступа (Reply Keyboard) внизу экрана:
    - [ ℹ️ Информация ] [ 📥 Скачать/загрузить Excel ]
    - [ ПЕРЕКУПЕР ] (открывает Mini App)
    """
    if current_region.startswith(("http://", "https://")):
        webapp_url = current_region
        current_region = "Москва"

    if webapp_url is None:
        webapp_url = getattr(settings, "WEBAPP_URL", "")

    app_btn = (
        KeyboardButton(text="ПЕРЕКУПЕР", web_app=WebAppInfo(url=webapp_url))
        if webapp_url
        else KeyboardButton(text="ПЕРЕКУПЕР")
    )

    keyboard = [
        [
            KeyboardButton(text="ℹ️ Информация"),
            KeyboardButton(text="📥 Скачать/загрузить Excel"),
        ],
        [
            app_btn,
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )


def get_hide_keyboard() -> ReplyKeyboardRemove:
    """Убирает всплывающую нижнюю клавиатуру."""
    return ReplyKeyboardRemove()



def get_regions_keyboard(current_key: str = "moskva", page: int = 0, per_page: int = 12) -> InlineKeyboardMarkup:
    """Меню выбора региона поиска с удобной пагинацией."""
    from core.regions import POPULAR_REGIONS

    total = len(POPULAR_REGIONS)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))

    start = page * per_page
    end = start + per_page
    slice_items = POPULAR_REGIONS[start:end]

    rows = []
    current_row = []
    for key, label in slice_items:
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

    # Навигация пагинации (если больше 1 страницы)
    if total_pages > 1:
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"page_regions:{page - 1}"))
        nav_row.append(InlineKeyboardButton(text=f"Стр. {page + 1}/{total_pages}", callback_data="noop"))
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"page_regions:{page + 1}"))
        rows.append(nav_row)

    rows.append([
        InlineKeyboardButton(
            text="🔍 Ввести любой город текстом (/city)",
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


def get_stream_control_keyboard(stream: Any) -> InlineKeyboardMarkup:
    """Инлайн-пульт управления поисковым потоком по ссылке (как в видео-гайде)."""
    status_icon = "⏸ Приостановить" if stream.is_active else "▶️ Возобновить"
    rows = [
        [
            InlineKeyboardButton(
                text=status_icon,
                callback_data=f"stream_toggle:{stream.chat_id}",
            ),
            InlineKeyboardButton(
                text="⚙️ Фильтры потока",
                callback_data=f"stream_filters:{stream.chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🌐 Открыть поиск на источнике",
                url=stream.url,
            ),
        ],
        [
            InlineKeyboardButton(
                text="⛔️ Стоп-слова",
                callback_data=f"stream_words:{stream.chat_id}",
            ),
            InlineKeyboardButton(
                text="❌ Отключить поиск",
                callback_data=f"stream_delete:{stream.chat_id}",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_stream_filters_keyboard(stream: Any) -> InlineKeyboardMarkup:
    """Меню тонкой настройки фильтрации объявлений для потока."""
    photo_text = "📸 Только с фото: ✅ ВКЛ" if stream.filter_only_photo else "📸 Только с фото: ❌ ВЫКЛ"
    reserve_text = "📦 Без брони (резерва): ✅ ВКЛ" if stream.filter_exclude_reserved else "📦 Без брони (резерва): ❌ ВЫКЛ"
    promo_text = "🚫 Без рекламы/промо: ✅ ВКЛ" if stream.filter_exclude_promo else "🚫 Без рекламы/промо: ❌ ВЫКЛ"
    desc_text = "📝 Только с описанием: ✅ ВКЛ" if stream.filter_only_desc else "📝 Только с описанием: ❌ ВЫКЛ"

    rows = [
        [
            InlineKeyboardButton(
                text=photo_text,
                callback_data=f"sfilter:{stream.chat_id}:filter_only_photo",
            ),
        ],
        [
            InlineKeyboardButton(
                text=reserve_text,
                callback_data=f"sfilter:{stream.chat_id}:filter_exclude_reserved",
            ),
        ],
        [
            InlineKeyboardButton(
                text=promo_text,
                callback_data=f"sfilter:{stream.chat_id}:filter_exclude_promo",
            ),
        ],
        [
            InlineKeyboardButton(
                text=desc_text,
                callback_data=f"sfilter:{stream.chat_id}:filter_only_desc",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад к пульту потока",
                callback_data=f"stream_back:{stream.chat_id}",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
