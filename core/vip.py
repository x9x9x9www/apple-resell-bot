from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)


class VIPManager:
    """
    Менеджер VIP-подписок и интеграции Telegram Stars (XTR).
    Позволяет пользователям оформлять премиум-подписку в Telegram Stars
    для получения мгновенных оповещений без задержек и доступа к умному автоторгу.
    """

    STAR_PRICE_VIP_MONTH = 250  # 250 Telegram Stars за 30 дней VIP

    def __init__(self, data_file: Optional[Path | str] = None):
        self.data_file = Path(data_file) if data_file else (settings.BASE_DIR / "vip_users.json")
        self._vip_data: Dict[str, Dict[str, Any]] = self._load()

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception as e:
                logger.warning("Ошибка чтения %s: %s", self.data_file, e)
        return {}

    def _save(self) -> None:
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self._vip_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("Ошибка сохранения VIP данных: %s", e)

    def is_vip(self, user_id: int | str) -> bool:
        """Проверяет, активен ли статус VIP у пользователя."""
        uid = str(user_id)
        user_info = self._vip_data.get(uid)
        if not user_info:
            return False
        expires_at = user_info.get("expires_at", 0)
        return expires_at > time.time()

    def get_vip_expiry_date(self, user_id: int | str) -> Optional[str]:
        """Возвращает дату окончания VIP в читаемом формате."""
        uid = str(user_id)
        user_info = self._vip_data.get(uid)
        if not user_info:
            return None
        expires_at = user_info.get("expires_at", 0)
        if expires_at <= time.time():
            return None
        import datetime
        dt = datetime.datetime.fromtimestamp(expires_at)
        return dt.strftime("%d.%m.%Y %H:%M")

    def grant_vip(self, user_id: int | str, days: int = 30, stars_paid: int = 0) -> None:
        """Активирует или продлевает VIP подписку."""
        uid = str(user_id)
        now = time.time()
        current_expiry = self._vip_data.get(uid, {}).get("expires_at", now)
        base_time = max(now, current_expiry)
        new_expiry = base_time + (days * 86400)

        self._vip_data[uid] = {
            "expires_at": new_expiry,
            "stars_paid_total": self._vip_data.get(uid, {}).get("stars_paid_total", 0) + stars_paid,
            "last_payment_ts": now,
        }
        self._save()
        logger.info("Пользователю %s активирован VIP на %d дней (до %s)", uid, days, new_expiry)
