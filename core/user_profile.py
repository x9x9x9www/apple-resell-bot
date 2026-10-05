from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel, Field

from config import settings
from core.models import ParsedIPhone

logger = logging.getLogger(__name__)


class UserConditionRules(BaseModel):
    """Правила оценки состояния и дисконтов перекупщика."""
    battery_threshold: int = Field(default=80, description="Порог износа АКБ (%) ниже которого применяется скидка")
    battery_discount: int = Field(default=3000, description="Сумма уценки на замену аккумулятора (₽)")
    allow_defects: bool = Field(default=False, description="Разрешать ли лоты с дефектами (битые, трещины, замены)")
    defect_discount: int = Field(default=8000, description="Скидка за дефект (₽) если они разрешены")
    ignore_no_face_id: bool = Field(default=True, description="Игнорировать лоты без Face ID / Touch ID")
    ignore_mdm_rsim: bool = Field(default=True, description="Игнорировать MDM / Demo / R-Sim / залоченные")
    ignore_replicas: bool = Field(default=True, description="Игнорировать реплики и копии")


class UserModelConfig(BaseModel):
    """Индивидуальные настройки поиска по конкретной конфигурации гаджета."""
    model: str
    storage: int = 128
    enabled: bool = True
    min_price: int = Field(default=0, description="Нижний порог цены (отсекает запчасти, коробки и хлам)")
    max_buy: int = Field(default=0, description="Максимальная цена выкупа")
    market: int = Field(default=0, description="Среднерыночная стоимость")


class UserResellProfile(BaseModel):
    """
    Персональный профиль перекупщика:
    - Желаемая маржа
    - Правила состояния и фильтры риска
    - Каталог отслеживаемых моделей с персональными лимитами
    """
    user_id: int
    target_margin: int = Field(default=5000, description="Желаемая минимальная чистая прибыль (₽)")
    margin_mode: str = Field(default="rub", description="'rub' или 'percent'")
    condition_rules: UserConditionRules = Field(default_factory=UserConditionRules)
    models: dict[str, dict[str, UserModelConfig]] = Field(default_factory=dict)

    def get_config(self, model: str, storage: int) -> Optional[UserModelConfig]:
        """Возвращает настройки модели или None."""
        model_cfgs = self.models.get(model)
        if not model_cfgs:
            return None
        cfg = model_cfgs.get(str(storage))
        if not cfg:
            # Fallback к 128 или первой доступной
            cfg = model_cfgs.get("128") or next(iter(model_cfgs.values()), None)
        return cfg

    def apply_global_margin(self, margin_rub: int) -> None:
        """Пересчитывает лимиты выкупа (max_buy = market - margin) для всех моделей."""
        self.target_margin = margin_rub
        for model_name, storages in self.models.items():
            for storage_str, cfg in storages.items():
                if cfg.market > 0:
                    cfg.max_buy = max(0, cfg.market - margin_rub)


class UserProfileManager:
    """Менеджер сохранения, загрузки и оценки профилей перекупщиков."""

    def __init__(self, storage_path: Optional[Path | str] = None):
        self.storage_path = Path(storage_path) if storage_path else (settings.BASE_DIR / "user_profiles.json")
        self._profiles: dict[int, UserResellProfile] = {}
        self.load_all()

    def load_all(self) -> None:
        """Загрузка всех профилей из JSON файла."""
        if not self.storage_path.exists():
            self._profiles = {}
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            
            loaded = {}
            for uid_str, p_data in raw_data.items():
                try:
                    uid = int(uid_str)
                    profile = UserResellProfile.model_validate(p_data)
                    loaded[uid] = profile
                except Exception as ex:
                    logger.warning("Ошибка разбора профиля пользователя %s: %s", uid_str, ex)
            self._profiles = loaded
            logger.info("Загружено %d профилей пользователей из %s", len(self._profiles), self.storage_path)
        except Exception as e:
            logger.error("Ошибка при чтении %s: %s", self.storage_path, e)
            self._profiles = {}

    def save_all(self) -> None:
        """Сохранение всех профилей в файл."""
        try:
            data = {}
            for uid, prof in self._profiles.items():
                data[str(uid)] = prof.model_dump()

            tmp_path = self.storage_path.with_suffix(".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            tmp_path.replace(self.storage_path)
            logger.debug("Профили пользователей сохранены в %s", self.storage_path)
        except Exception as e:
            logger.error("Ошибка при сохранении %s: %s", self.storage_path, e)

    def get_or_create_profile(self, user_id: int) -> UserResellProfile:
        """Возвращает существующий профиль пользователя или создает дефолтный на основе общей матрицы."""
        if user_id in self._profiles:
            return self._profiles[user_id]

        profile = self._build_default_profile(user_id)
        self._profiles[user_id] = profile
        self.save_all()
        return profile

    def save_profile(self, profile: UserResellProfile) -> None:
        """Сохраняет профиль конкретного пользователя."""
        self._profiles[profile.user_id] = profile
        self.save_all()

    def _build_default_profile(self, user_id: int) -> UserResellProfile:
        """Создает профиль по умолчанию на основе базовой pricing_matrix.json."""
        default_matrix = settings.load_pricing_matrix()
        models_dict: dict[str, dict[str, UserModelConfig]] = {}

        for model, storages in default_matrix.items():
            models_dict[model] = {}
            for storage, data in storages.items():
                max_buy = int(data.get("max_buy", 0))
                market = int(data.get("market", max_buy))
                enabled = bool(data.get("enabled", True))
                # По умолчанию минимальный порог отсева = 30% от рынка или 5000 руб
                min_price = max(5000, int(market * 0.35)) if market > 0 else 0

                models_dict[model][str(storage)] = UserModelConfig(
                    model=model,
                    storage=int(storage) if str(storage).isdigit() else 128,
                    enabled=enabled,
                    min_price=min_price,
                    max_buy=max_buy,
                    market=market,
                )

        return UserResellProfile(
            user_id=user_id,
            target_margin=5000,
            condition_rules=UserConditionRules(),
            models=models_dict,
        )

    def evaluate_item(
        self, profile: UserResellProfile, item: ParsedIPhone
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Проверяет лот на соответствие персональным настройкам перекупщика:
        1. Проверка активности модели и объема памяти.
        2. Проверка нижней планки цены (min_price) — отсев запчастей/коробок/мусора.
        3. Проверка фильтров риска (Face ID, MDM/R-Sim).
        4. Расчет дисконтов за состояние (АКБ, дефекты).
        5. Финальная проверка выкупной цены (price <= effective_max_buy).

        Возвращает:
            (is_profitable, rejection_reason, breakdown_data)
        """
        cfg = profile.get_config(item.model, item.storage_gb)
        if not cfg:
            return False, f"Модель '{item.model}' отсутствует в вашем списке выкупа", {}

        if not cfg.enabled:
            return False, f"Выкуп модели '{item.model}' отключен в ваших настройках", {}

        # 1. Проверка нижней границы цены
        if cfg.min_price > 0 and item.price < cfg.min_price:
            p_fmt = f"{item.price:,}".replace(",", " ")
            min_fmt = f"{cfg.min_price:,}".replace(",", " ")
            return False, (
                f"Цена {p_fmt} ₽ ниже минимального порога {min_fmt} ₽ "
                f"(вероятно запчасти, коробка или сомнительный лот)"
            ), {}

        rules = profile.condition_rules
        breakdown: Dict[str, Any] = {
            "base_max_buy": cfg.max_buy,
            "market_price": cfg.market,
            "applied_battery_discount": 0,
            "applied_defect_discount": 0,
            "condition_notes": [],
        }

        # 2. Проверка рискованных флагов
        if rules.ignore_no_face_id and getattr(item, "has_no_face_id", False):
            return False, "Отсеян: не работает Face ID / Touch ID (согласно вашим настройкам риска)", {}

        if rules.ignore_mdm_rsim and getattr(item, "is_mdm_rsim", False):
            return False, "Отсеян: обнаружена блокировка MDM / Demo / R-Sim", {}

        # 3. Проверка дефектов
        has_defects = getattr(item, "has_defects", False)
        defect_reasons = getattr(item, "defect_reasons", [])

        if has_defects:
            if not rules.allow_defects:
                def_str = ", ".join(defect_reasons) if defect_reasons else "дефект корпуса/экрана"
                return False, f"Отсеян: обнаружен дефект ({def_str}), лоты под ремонт выключены", {}
            else:
                def_fmt = f"{rules.defect_discount:,}".replace(",", " ")
                breakdown["applied_defect_discount"] = rules.defect_discount
                breakdown["condition_notes"].append(f"Дефект (-{def_fmt} ₽)")

        # 4. Проверка износа АКБ
        if item.battery_health is not None and item.battery_health < rules.battery_threshold:
            bat_fmt = f"{rules.battery_discount:,}".replace(",", " ")
            breakdown["applied_battery_discount"] = rules.battery_discount
            breakdown["condition_notes"].append(f"АКБ {item.battery_health}% (-{bat_fmt} ₽)")

        # 5. Итоговый лимит выкупа с учетом всех дисконтов
        total_discount = breakdown["applied_battery_discount"] + breakdown["applied_defect_discount"]
        effective_max_buy = max(0, cfg.max_buy - total_discount)

        breakdown["effective_max_buy"] = effective_max_buy
        breakdown["calculated_profit"] = max(0, cfg.market - item.price)

        # Обновляем метаданные в самом лоте
        item.max_buy_price = effective_max_buy
        item.market_price = cfg.market
        item.profit = breakdown["calculated_profit"]
        item.battery_penalty = breakdown["applied_battery_discount"]
        item.defect_penalty = breakdown["applied_defect_discount"]

        if item.price <= effective_max_buy:
            item.is_profitable = True
            return True, None, breakdown
        else:
            diff = item.price - effective_max_buy
            p_fmt = f"{item.price:,}".replace(",", " ")
            eff_fmt = f"{effective_max_buy:,}".replace(",", " ")
            diff_fmt = f"{diff:,}".replace(",", " ")
            tot_fmt = f"{total_discount:,}".replace(",", " ")
            discount_note = f" (с учетом уценок -{tot_fmt} ₽)" if total_discount > 0 else ""
            item.is_profitable = False
            rejection = (
                f"Цена {p_fmt} ₽ выше вашего лимита {eff_fmt} ₽{discount_note} "
                f"(превышение на {diff_fmt} ₽)"
            )
            item.rejection_reason = rejection
            return False, rejection, breakdown
