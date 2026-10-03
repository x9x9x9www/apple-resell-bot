from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from config import settings
from core.models import ParsedIPhone

logger = logging.getLogger(__name__)


class MarginFilter:
    """
    Фильтр маржинальности лотов.
    Сопоставляет вычисленные характеристики (модель, память, цена)
    с матрицей пороговых цен выкупа.
    """

    SERIES_LIST = [
        ("macbook", "💻 MacBook (Air / Pro)"),
        ("samsung", "📱 Samsung Galaxy"),
        ("pixel", "📱 Google Pixel"),
        ("ipad", "📟 iPad (Pro / Air / 10)"),
        ("consoles", "🎮 Консоли (PS5 / Steam Deck)"),
        ("16", "iPhone 16 / 16 Pro"),
        ("15", "iPhone 15 / 15 Pro"),
        ("14", "iPhone 14 / 14 Pro"),
        ("13", "iPhone 13 / 13 Pro"),
        ("12", "iPhone 12 / 12 Pro"),
        ("11", "iPhone 11 / 11 Pro"),
        ("X_SE", "iPhone X / XS / SE"),
        ("custom", "⭐ Свои гаджеты"),
    ]

    def __init__(self, matrix: Optional[dict[str, dict[str, dict[str, Any]]]] = None):
        self.matrix = matrix if matrix is not None else settings.load_pricing_matrix()

    def reload_matrix(self) -> None:
        """Перезагрузка матрицы цен без перезапуска сервиса."""
        self.matrix = settings.load_pricing_matrix()
        logger.info("Матрица цен успешно обновлена.")

    def save_matrix(self, path: Optional[Path | str] = None) -> None:
        """Сохраняет текущую матрицу цен в JSON файл."""
        target = Path(path) if path else (settings.BASE_DIR / "pricing_matrix.json")
        try:
            with open(target, "w", encoding="utf-8") as f:
                json.dump(self.matrix, f, ensure_ascii=False, indent=2)
            logger.info("Матрица цен сохранена в %s", target)
        except Exception as e:
            logger.error("Ошибка при сохранении матрицы цен: %s", e)

    def is_series_enabled(self, series_key: str) -> bool:
        """Проверяет, включена ли серия моделей (хотя бы одна конфигурация)."""
        for model_name, configs in self.matrix.items():
            if self._matches_series(model_name, series_key):
                for cfg in configs.values():
                    if cfg.get("enabled", True):
                        return True
        return False

    def toggle_series(self, series_key: str, save: bool = True) -> bool:
        """Переключает статус активности всей серии моделей и опционально сохраняет матрицу."""
        current_state = self.is_series_enabled(series_key)
        new_state = not current_state
        for model_name, configs in self.matrix.items():
            if self._matches_series(model_name, series_key):
                for cfg in configs.values():
                    cfg["enabled"] = new_state
        if save:
            self.save_matrix()
        return new_state

    def _matches_series(self, model_name: str, series_key: str) -> bool:
        nl = model_name.lower()
        if series_key == "macbook":
            return "macbook" in nl or "mac" in nl
        elif series_key == "samsung":
            return "samsung" in nl or "galaxy" in nl
        elif series_key == "pixel":
            return "pixel" in nl
        elif series_key == "ipad":
            return "ipad" in nl
        elif series_key == "consoles":
            return any(k in nl for k in ["playstation", "ps5", "steam deck", "xbox"])
        elif series_key == "X_SE":
            return any(k in model_name for k in ["XS", "XR", "iPhone X", "SE"])
        elif series_key == "custom":
            standard = [
                "16", "15", "14", "13", "12", "11", "xs", "xr", "iphone x", "se",
                "macbook", "samsung", "galaxy", "pixel", "ipad", "playstation", "ps5", "steam deck", "xbox"
            ]
            return not any(s in nl for s in standard)
        return f"iPhone {series_key}" in model_name

    def get_stats(self) -> dict[str, int]:
        """Возвращает статистику по активным конфигурациям."""
        total_models = len(self.matrix)
        total_configs = sum(len(c) for c in self.matrix.values())
        active_configs = sum(
            1 for c in self.matrix.values() for cfg in c.values() if cfg.get("enabled", True)
        )
        return {
            "total_models": total_models,
            "total_configs": total_configs,
            "active_configs": active_configs,
        }

    def evaluate(self, item: ParsedIPhone) -> bool:
        """
        Проверяет, удовлетворяет ли лот критерию выкупной цены.
        Заполняет поля: max_buy_price, market_price, profit, is_profitable.
        Возвращает:
            True  -> лот выгоден (price <= max_buy_price)
            False -> лот не проходит по цене или модель не в списке выкупа
        """
        model_rules = self.matrix.get(item.model)
        if not model_rules:
            item.rejection_reason = f"Модель '{item.model}' отсутствует в матрице выкупа"
            item.is_profitable = False
            return False

        storage_str = str(item.storage_gb)
        storage_rules = model_rules.get(storage_str)

        # Если точный объем памяти не найден, берем ближайший меньший либо базовый
        if not storage_rules:
            # Попробуем 128 как дефолт
            storage_rules = model_rules.get("128") or next(iter(model_rules.values()), None)

        if not storage_rules:
            item.rejection_reason = f"Нет цен для {item.model} {item.storage_gb}GB"
            item.is_profitable = False
            return False

        # Проверка флага включения выкупа
        if storage_rules.get("enabled") is False:
            item.rejection_reason = f"Выкуп {item.model} {item.storage_gb}GB отключен пользователем"
            item.is_profitable = False
            return False

        max_buy = storage_rules.get("max_buy", 0)
        market = storage_rules.get("market", max_buy)

        # Умный расчет скидки на замену батареи (если АКБ изношен)
        battery_penalty = 0
        if item.battery_health is not None:
            if item.battery_health < 75:
                # Изношенная батарея (<75%) -> минус 4 000 ₽ на замену в сервисе
                battery_penalty = 4000
            elif item.battery_health < 80:
                # Слабая батарея (75-79%) -> минус 2 500 ₽
                battery_penalty = 2500

        item.battery_penalty = battery_penalty
        effective_max_buy = max(0, max_buy - battery_penalty)

        item.max_buy_price = effective_max_buy
        item.market_price = market
        item.profit = max(0, market - item.price)

        if item.price <= effective_max_buy:
            item.is_profitable = True
            return True
        else:
            penalty_info = f" (с учетом скидки на АКБ -{battery_penalty} ₽)" if battery_penalty else ""
            item.rejection_reason = (
                f"Цена {item.price:,} ₽ выше порога выкупа {effective_max_buy:,} ₽{penalty_info} "
                f"(рынок: {market:,} ₽)"
            )
            item.is_profitable = False
            return False
