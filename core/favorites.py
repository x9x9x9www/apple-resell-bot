from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models import ParsedIPhone

logger = logging.getLogger(__name__)

FAVORITES_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "favorites.json",
)


class FavoritesManager:
    """
    Менеджер сохраненных лотов (Избранное).
    Обеспечивает сохранение, удаление, проверку и кэширование отправленных лотов.
    """

    def __init__(self, file_path: str = FAVORITES_FILE_PATH) -> None:
        self.file_path = file_path
        # user_id (str) -> list of lot dicts
        self._favorites: dict[str, list[dict[str, Any]]] = {}
        # item_id -> lot dict (LRU / recent lots cache up to 500 items)
        self._recent_lots_cache: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.file_path):
            self._favorites = {}
            return
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self._favorites = data
                else:
                    self._favorites = {}
        except Exception as e:
            logger.error("Ошибка при чтении %s: %s", self.file_path, e)
            self._favorites = {}

    def _save(self) -> None:
        try:
            tmp_path = f"{self.file_path}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._favorites, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.file_path)
        except Exception as e:
            logger.error("Ошибка при сохранении %s: %s", self.file_path, e)

    def cache_dispatched_lot(self, item: Any) -> None:
        """Кэширует отправленный лот, чтобы при нажатии 'В избранное' были все метаданные."""
        if not hasattr(item, "item_id") or not item.item_id:
            return
        # Ограничиваем размер кэша
        if len(self._recent_lots_cache) > 1000:
            # Удаляем старейшие 200 записей
            keys_to_del = list(self._recent_lots_cache.keys())[:200]
            for k in keys_to_del:
                self._recent_lots_cache.pop(k, None)

        self._recent_lots_cache[str(item.item_id)] = {
            "item_id": str(item.item_id),
            "model": getattr(item, "model", "") or getattr(item, "title", "Гаджет"),
            "price": getattr(item, "price", 0),
            "url": getattr(item, "url", ""),
            "platform": getattr(item.platform, "value", str(item.platform)) if hasattr(item, "platform") else "Авито",
            "location": getattr(item, "location", ""),
            "image_url": getattr(item, "image_url", None),
            "storage_gb": getattr(item, "storage_gb", None),
            "battery_health": getattr(item, "battery_health", None),
        }

    def get_cached_lot(self, item_id: str | int) -> Optional[dict[str, Any]]:
        return self._recent_lots_cache.get(str(item_id))

    def get_favorites(self, user_id: int | str) -> list[dict[str, Any]]:
        uid = str(user_id)
        return list(self._favorites.get(uid, []))

    def is_favorite(self, user_id: int | str, item_id: str | int) -> bool:
        uid = str(user_id)
        iid = str(item_id)
        user_favs = self._favorites.get(uid, [])
        return any(f.get("item_id") == iid for f in user_favs)

    def add_favorite(self, user_id: int | str, lot: dict[str, Any]) -> bool:
        """Добавляет лот в избранное пользователя. Возвращает True, если добавлен."""
        uid = str(user_id)
        iid = str(lot.get("item_id", ""))
        if not iid:
            return False

        if uid not in self._favorites:
            self._favorites[uid] = []

        # Проверяем на дубликат
        if any(f.get("item_id") == iid for f in self._favorites[uid]):
            return False

        lot_entry = {
            "item_id": iid,
            "model": lot.get("model", "Гаджет"),
            "price": lot.get("price", 0),
            "url": lot.get("url", ""),
            "platform": lot.get("platform", "Авито"),
            "location": lot.get("location", ""),
            "added_at": int(time.time()),
        }
        self._favorites[uid].insert(0, lot_entry)
        self._save()
        return True

    def remove_favorite(self, user_id: int | str, item_id: str | int) -> bool:
        """Удаляет лот из избранного пользователя. Возвращает True, если был удален."""
        uid = str(user_id)
        iid = str(item_id)
        user_favs = self._favorites.get(uid, [])
        new_favs = [f for f in user_favs if f.get("item_id") != iid]
        if len(new_favs) != len(user_favs):
            self._favorites[uid] = new_favs
            self._save()
            return True
        return False

    def clear_favorites(self, user_id: int | str) -> int:
        """Очищает всё избранное пользователя. Возвращает количество удаленных лотов."""
        uid = str(user_id)
        count = len(self._favorites.get(uid, []))
        if count > 0:
            self._favorites[uid] = []
            self._save()
        return count


# Глобальный синглтон
favorites_manager = FavoritesManager()
