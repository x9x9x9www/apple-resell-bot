#!/usr/bin/env python3
"""
Optimization & Emoji Cleanup Script for Apple Resell Bot Mini App.
1. Removes heavy CSS blur filters and infinite repainting animations to eliminate lag.
2. Removes intrusive global error/unhandledrejection toast popups on startup.
3. Completely replaces emojis on buttons and UI with clean SVG icons and modern typography.
"""

import re
from pathlib import Path

def optimize_file(filepath: Path):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # -------------------------------------------------------------
    # 1. OPTIMIZE CSS: Atmosphere Glows & Glass Performance
    # -------------------------------------------------------------
    # Replace pulseTopAtmosphere & pulseBottomAtmosphere with hardware-efficient static layers
    old_glows = """    .glow-atmosphere-top {
      position: fixed;
      top: -100px;
      left: 50%;
      transform: translateX(-50%);
      width: 140vw;
      height: 420px;
      background: radial-gradient(ellipse 65% 65% at 50% 18%, rgba(200, 230, 255, 0.40) 0%, rgba(140, 190, 255, 0.22) 30%, rgba(70, 130, 220, 0.10) 55%, transparent 75%);
      filter: blur(50px);
      pointer-events: none;
      z-index: 0;
      animation: pulseTopAtmosphere 8s infinite alternate ease-in-out;
    }

    .glow-atmosphere-bottom {
      position: fixed;
      bottom: -80px;
      left: 50%;
      transform: translateX(-50%);
      width: 140vw;
      height: 380px;
      background: radial-gradient(ellipse 65% 65% at 50% 82%, rgba(210, 235, 255, 0.38) 0%, rgba(150, 200, 255, 0.20) 30%, rgba(80, 140, 230, 0.08) 55%, transparent 75%);
      filter: blur(50px);
      pointer-events: none;
      z-index: 0;
      animation: pulseBottomAtmosphere 8s infinite alternate ease-in-out;
    }

    @keyframes pulseTopAtmosphere {
      0% { opacity: 0.85; transform: translateX(-50%) scale(0.98); }
      100% { opacity: 1.15; transform: translateX(-50%) scale(1.03); }
    }

    @keyframes pulseBottomAtmosphere {
      0% { opacity: 0.85; transform: translateX(-50%) scale(0.98); }
      100% { opacity: 1.15; transform: translateX(-50%) scale(1.03); }
    }"""

    new_glows = """    .glow-atmosphere-top {
      position: fixed;
      top: -40px;
      left: 50%;
      transform: translateX(-50%) translateZ(0);
      width: 120vw;
      height: 300px;
      background: radial-gradient(ellipse 60% 60% at 50% 18%, rgba(180, 215, 255, 0.16) 0%, rgba(100, 160, 240, 0.05) 45%, transparent 70%);
      pointer-events: none;
      z-index: 0;
      will-change: transform;
    }

    .glow-atmosphere-bottom {
      position: fixed;
      bottom: -40px;
      left: 50%;
      transform: translateX(-50%) translateZ(0);
      width: 120vw;
      height: 280px;
      background: radial-gradient(ellipse 60% 60% at 50% 82%, rgba(180, 215, 255, 0.14) 0%, rgba(90, 150, 230, 0.04) 45%, transparent 70%);
      pointer-events: none;
      z-index: 0;
      will-change: transform;
    }"""

    if old_glows in content:
        content = content.replace(old_glows, new_glows)
        print("Replaced old heavy glows")

    # Replace heavy card styling with high-performance glass
    old_cards_css = """    .ios-inset-card,
    .model-card,
    .kpi-card,
    .deals-section,
    .search-wrapper,
    .master-bot-bar,
    .modal-sheet {
      border-radius: 28px !important;
      background: linear-gradient(145deg, rgba(26, 30, 40, 0.68) 0%, rgba(14, 16, 22, 0.78) 100%) !important;
      backdrop-filter: blur(32px) saturate(200%) brightness(1.05) !important;
      -webkit-backdrop-filter: blur(32px) saturate(200%) brightness(1.05) !important;
      border: 1.2px solid rgba(255, 255, 255, 0.32) !important;
      box-shadow:
        inset 0 2px 3px 0 rgba(255, 255, 255, 0.75),
        inset 0 -2px 3px 0 rgba(0, 0, 0, 0.45),
        inset 2px 0 2px 0 rgba(255, 255, 255, 0.3),
        inset -2px 0 2px 0 rgba(255, 255, 255, 0.2),
        0 20px 48px -8px rgba(0, 0, 0, 0.7),
        0 0 22px rgba(180, 215, 255, 0.12) !important;
    }

    .model-card:hover {
      border-color: rgba(255, 255, 255, 0.45) !important;
      box-shadow:
        inset 0 2px 4px 0 rgba(255, 255, 255, 0.9),
        inset 0 -2px 3px 0 rgba(0, 0, 0, 0.5),
        0 24px 54px -6px rgba(0, 0, 0, 0.8),
        0 0 28px rgba(190, 225, 255, 0.22) !important;
    }"""

    new_cards_css = """    .ios-inset-card,
    .model-card,
    .kpi-card,
    .deals-section,
    .search-wrapper,
    .master-bot-bar {
      border-radius: 24px !important;
      background: rgba(22, 26, 36, 0.92) !important;
      border: 1px solid rgba(255, 255, 255, 0.16) !important;
      box-shadow:
        inset 0 1px 1px 0 rgba(255, 255, 255, 0.35),
        0 8px 24px rgba(0, 0, 0, 0.45) !important;
      contain: content;
      transform: translateZ(0);
    }

    .modal-sheet {
      border-radius: 28px !important;
      background: rgba(20, 24, 34, 0.96) !important;
      border: 1px solid rgba(255, 255, 255, 0.22) !important;
      box-shadow:
        inset 0 1px 1.5px 0 rgba(255, 255, 255, 0.5),
        0 20px 48px rgba(0, 0, 0, 0.85) !important;
      transform: translateZ(0);
    }

    .model-card:hover {
      border-color: rgba(255, 255, 255, 0.28) !important;
      box-shadow:
        inset 0 1px 1.5px 0 rgba(255, 255, 255, 0.55),
        0 10px 28px rgba(0, 0, 0, 0.55) !important;
    }"""

    if old_cards_css in content:
        content = content.replace(old_cards_css, new_cards_css)
        print("Replaced heavy cards CSS")

    # Replace floating tab bar and save bar for optimal GPU composition
    old_tab_bar_css = """    /* Floating Capsule Tab Bar (Liquid Glass Style) */
    .ios-tab-bar {
      margin: 0 14px calc(10px + env(safe-area-inset-bottom, 0px)) !important;
      border-radius: 9999px !important;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.20) 0%, rgba(18, 22, 30, 0.82) 50%, rgba(255, 255, 255, 0.12) 100%) !important;
      backdrop-filter: blur(36px) saturate(210%) !important;
      -webkit-backdrop-filter: blur(36px) saturate(210%) !important;
      border: 1.2px solid rgba(255, 255, 255, 0.42) !important;
      box-shadow:
        inset 0 2px 3px 0 rgba(255, 255, 255, 0.8),
        inset 0 -2px 3px 0 rgba(0, 0, 0, 0.5),
        0 20px 48px rgba(0, 0, 0, 0.8),
        0 0 30px rgba(180, 215, 255, 0.20) !important;
    }"""

    new_tab_bar_css = """    /* Floating Capsule Tab Bar (High-Performance Glass) */
    .ios-tab-bar {
      margin: 0 14px calc(10px + env(safe-area-inset-bottom, 0px)) !important;
      border-radius: 9999px !important;
      background: rgba(18, 22, 30, 0.88) !important;
      backdrop-filter: blur(20px) !important;
      -webkit-backdrop-filter: blur(20px) !important;
      border: 1px solid rgba(255, 255, 255, 0.28) !important;
      box-shadow:
        inset 0 1px 1px 0 rgba(255, 255, 255, 0.6),
        0 12px 32px rgba(0, 0, 0, 0.7) !important;
      will-change: transform;
      transform: translateZ(0);
    }"""

    if old_tab_bar_css in content:
        content = content.replace(old_tab_bar_css, new_tab_bar_css)
        print("Replaced tab bar CSS")

    old_save_bar_css = """    /* Save Bar floating liquid glass */
    .save-bar {
      margin: 0 14px calc(72px + env(safe-area-inset-bottom, 0px)) !important;
      border-radius: 9999px !important;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.20) 0%, rgba(18, 22, 30, 0.85) 50%, rgba(255, 255, 255, 0.12) 100%) !important;
      backdrop-filter: blur(32px) saturate(200%) !important;
      -webkit-backdrop-filter: blur(32px) saturate(200%) !important;
      border: 1.2px solid rgba(255, 255, 255, 0.42) !important;
      box-shadow:
        inset 0 2px 3px 0 rgba(255, 255, 255, 0.8),
        inset 0 -2px 3px 0 rgba(0, 0, 0, 0.5),
        0 18px 42px rgba(0, 0, 0, 0.75),
        0 0 24px rgba(180, 215, 255, 0.18) !important;
    }"""

    new_save_bar_css = """    /* Save Bar floating glass */
    .save-bar {
      margin: 0 14px calc(72px + env(safe-area-inset-bottom, 0px)) !important;
      border-radius: 9999px !important;
      background: rgba(18, 22, 30, 0.90) !important;
      backdrop-filter: blur(20px) !important;
      -webkit-backdrop-filter: blur(20px) !important;
      border: 1px solid rgba(255, 255, 255, 0.28) !important;
      box-shadow:
        inset 0 1px 1px 0 rgba(255, 255, 255, 0.6),
        0 12px 32px rgba(0, 0, 0, 0.7) !important;
      will-change: transform;
      transform: translateZ(0);
    }"""

    if old_save_bar_css in content:
        content = content.replace(old_save_bar_css, new_save_bar_css)
        print("Replaced save bar CSS")

    # -------------------------------------------------------------
    # 2. FIX STARTUP ERROR: Remove global unhandled error popup
    # -------------------------------------------------------------
    old_error_listeners = """    // Global Unhandled Error Boundary (keeps everything inside the in-app concept)
    window.addEventListener('error', (e) => {
      console.error("Unhandled error:", e);
      showDynamicIsland("Сбой в приложении", e.message || "Непредвиденная ошибка", "⚠️", "error");
    });
    window.addEventListener('unhandledrejection', (e) => {
      console.error("Unhandled rejection:", e);
      showDynamicIsland("Сетевой сбой", "Не удалось завершить операцию", "⚠️", "error");
    });"""

    new_error_listeners = """    // Global Unhandled Error Boundary (console logging only to prevent false-alarm popups)
    window.addEventListener('error', (e) => {
      console.error("App error:", e);
    });
    window.addEventListener('unhandledrejection', (e) => {
      console.error("App rejection:", e);
    });"""

    if old_error_listeners in content:
        content = content.replace(old_error_listeners, new_error_listeners)
        print("Replaced global error listeners")

    # Safely wrap Telegram WebApp setup
    old_tg_init = """    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.ready();
      tg.expand();
      if (tg.setHeaderColor) tg.setHeaderColor('#000000');
      if (tg.setBackgroundColor) tg.setBackgroundColor('#000000');
    }"""

    new_tg_init = """    const tg = window.Telegram?.WebApp;
    if (tg) {
      try {
        tg.ready();
        tg.expand();
        if (typeof tg.setHeaderColor === 'function') tg.setHeaderColor('#000000');
        if (typeof tg.setBackgroundColor === 'function') tg.setBackgroundColor('#000000');
      } catch (err) {
        console.warn("Telegram WebApp init warning:", err);
      }
    }"""

    if old_tg_init in content:
        content = content.replace(old_tg_init, new_tg_init)
        print("Safely wrapped Telegram WebApp init")

    # -------------------------------------------------------------
    # 3. REMOVE ALL EMOJIS FROM BUTTONS AND UI
    # -------------------------------------------------------------
    # 3.1 Button toggle config: 🟢 Включен / ⚪️ Отключен -> clean SVG + text
    content = content.replace(
        "${activeItem.enabled ? '🟢 Включен' : '⚪️ Отключен'}",
        "${activeItem.enabled ? '<span class=\"config-dot active\"></span>Включен' : '<span class=\"config-dot\"></span>Отключен'}"
    )
    content = content.replace(
        "configCheckIcon.textContent = activeItem.enabled ? '🟢 Включен' : '⚪️ Отключен';",
        "configCheckIcon.innerHTML = activeItem.enabled ? '<span class=\"config-dot active\"></span>Включен' : '<span class=\"config-dot\"></span>Отключен';"
    )

    # Add .config-dot styling if not present
    dot_css = """
    .config-dot {
      display: inline-block;
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--text-muted);
      margin-right: 5px;
      vertical-align: middle;
    }
    .config-dot.active {
      background: var(--success-color);
      box-shadow: 0 0 6px rgba(48, 209, 88, 0.6);
    }
    """
    if ".config-dot {" not in content:
        content = content.replace("</style>", dot_css + "\n</style>", 1)

    # 3.2 Master bot text: 🟢 Поиск активен / ⏸ На паузе
    content = content.replace("isActive ? '🟢 Поиск активен' : '⏸ На паузе'", "isActive ? 'Поиск активен' : 'На паузе'")
    content = content.replace("🟢 Поиск активен", "Поиск активен")
    content = content.replace("⏸ На паузе", "На паузе")

    # 3.3 Dynamic Toast messages & Icons
    content = content.replace("'▶️ Поиск включен'", "'Поиск включен'")
    content = content.replace("'⏸ Поиск выключен'", "'Поиск выключен'")

    old_toast_icons = """        if (tIcon) {
          if (theme === 'error') tIcon.textContent = "⚠️";
          else if (theme === 'warning') tIcon.textContent = "⏸";
          else if (theme === 'success') tIcon.textContent = "✅";
          else tIcon.textContent = "⚡️";
        }"""

    new_toast_icons = """        if (tIcon) {
          if (theme === 'error') {
            tIcon.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:16px;height:16px;"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
          } else if (theme === 'warning') {
            tIcon.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:16px;height:16px;"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>';
          } else if (theme === 'success') {
            tIcon.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:16px;height:16px;"><polyline points="20 6 9 17 4 12"/></svg>';
          } else {
            tIcon.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:16px;height:16px;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>';
          }
        }"""

    if old_toast_icons in content:
        content = content.replace(old_toast_icons, new_toast_icons)
        print("Replaced dynamic toast icons with SVG")

    # 3.4 Platform filter names
    old_plat_names = """        const platNames = {
          all: '🟢 Авито + 🟣 Юла (Все)',
          avito: '🟢 Только Авито',
          youla: '🟣 Только Юла',
          none: '⏸ Мониторинг на паузе'
        };"""

    new_plat_names = """        const platNames = {
          all: 'Авито + Юла (Все)',
          avito: 'Только Авито',
          youla: 'Только Юла',
          none: 'Мониторинг на паузе'
        };"""

    if old_plat_names in content:
        content = content.replace(old_plat_names, new_plat_names)
        print("Replaced platform switcher labels")

    content = content.replace("none: '⏸ Пауза'", "none: 'Пауза'")

    # 3.5 Action cards in Catalog Manage Modal
    content = content.replace(
        '<div class="action-card-icon" style="background: rgba(10, 132, 255, 0.18); border-color: rgba(10, 132, 255, 0.35); color: var(--accent-color);">\n            🔄\n          </div>',
        '<div class="action-card-icon" style="background: rgba(10, 132, 255, 0.18); border-color: rgba(10, 132, 255, 0.35); color: var(--accent-color);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg></div>'
    )
    content = content.replace(
        '<div class="action-card-icon" style="background: rgba(255, 69, 58, 0.18); border-color: rgba(255, 69, 58, 0.35); color: #ff453a;">\n            🗑️\n          </div>',
        '<div class="action-card-icon" style="background: rgba(255, 69, 58, 0.18); border-color: rgba(255, 69, 58, 0.35); color: #ff453a;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:20px;height:20px;"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/></svg></div>'
    )
    content = content.replace('<div class="ios-alert-icon" id="iosAlertIcon">⚠️</div>', '<div class="ios-alert-icon" id="iosAlertIcon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:32px;height:32px;margin:0 auto;color:var(--warning-color);"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>')

    # 3.6 Button text cleanups
    content = content.replace("✕ Отмена", "Отмена")
    content = content.replace("➕ Добавить первую модель", "Добавить первую модель")
    content = content.replace("➕ Добавить модель", "Добавить модель")
    content = content.replace("⚡️ Добавить из шаблона", "Добавить из шаблона")
    content = content.replace("«➕ Добавить модель»", "«Добавить модель»")
    content = content.replace("«🔄 Сброс»", "«Сброс»")
    content = content.replace("✅ Добавить выбранные", "Добавить выбранные")
    content = content.replace("✅ Создать пустую папку", "Создать пустую папку")
    content = content.replace("✅ Добавить в матрицу", "Добавить в матрицу")
    content = content.replace("➕ Создать новую папку...", "+ Создать новую папку...")
    content = content.replace("📁 Все (без привязки к папке)", "Все (без привязки к папке)")
    content = content.replace("linkBtn.innerHTML = '🔗 По ссылке';", "linkBtn.innerHTML = '<span class=\"svg-icon\" style=\"width:11px; height:11px; margin-right:3px;\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"10\"/><line x1=\"2\" x2=\"22\" y1=\"12\" y2=\"12\"/><path d=\"M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z\"/></svg></span>По ссылке';")
    content = content.replace("linkBtn.innerHTML = '+ 🔗 ссылка';", "linkBtn.innerHTML = '<span class=\"svg-icon\" style=\"width:11px; height:11px; margin-right:3px;\">' + AppIcons.plus + '</span>Ссылка';")
    content = content.replace("editLinkModalTitle.textContent = `🔗 Ссылка: ${item.model}`;", "editLinkModalTitle.textContent = `Ссылка: ${item.model}`;")
    content = content.replace("document.getElementById('quickAddStorageTitle').textContent = `➕ Память: ${group.model}`;", "document.getElementById('quickAddStorageTitle').textContent = `Память: ${group.model}`;")
    content = content.replace("Автозаполнение ⚡️", "Автозаполнение")
    content = content.replace("💡 Можно выбрать один или несколько объемов сразу", "Можно выбрать один или несколько объемов сразу")
    content = content.replace("<span>⚡️</span>`;\n        customRow.addEventListener", "<span>+</span>`;\n        customRow.addEventListener")
    content = content.replace("✓ Выбран", "Выбран")
    content = content.replace("Нажмите «Применить в бота» ⚡️", "Нажмите «Применить»")
    content = content.replace("Стандартный поиск ⚡️", "Стандартный поиск")
    content = content.replace("Заводские цены восстановлены ⚡️", "Заводские цены восстановлены")
    content = content.replace("чистая маржа ⚡️", "чистая маржа")

    # 3.7 showDynamicIsland emoji icon removal (clean call)
    content = re.sub(r'showDynamicIsland\(([^,]+),\s*([^,]+),\s*["\'][^"\']+["\'](\s*,\s*["\'][^"\']+["\'])?\)', r'showDynamicIsland(\1, \2, ""\3)', content)

    # 3.8 Trends text (▲ / ▼ -> +/-)
    content = content.replace("'▲ +100%'", "'+100%'")
    content = content.replace("`▲ +${rounded}%`", "`+${rounded}%`")
    content = content.replace("`▼ -${rounded}%`", "`-${rounded}%`")
    content = content.replace("`▲ +${diffProfit}%`", "`+${diffProfit}%`")
    content = content.replace("`▼ ${diffProfit}%`", "`${diffProfit}%`")
    content = content.replace("`▲ +${Math.round((1 / (sorted.length - 1)) * 100)}%`", "`+${Math.round((1 / (sorted.length - 1)) * 100)}%`")
    content = content.replace("`▲ +${totalMarginPct}% маржа`", "`+${totalMarginPct}% маржа`")
    content = content.replace("'▲ 100%'", "'100%'")

    # 3.9 Sticky header title: remove ⚡️
    content = content.replace('<span style="font-size:16px;">⚡️</span>', '<span class="svg-icon" style="width:16px; height:16px; color:#fff;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></span>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Optimized {filepath}")

def main():
    root = Path(__file__).resolve().parent.parent
    files = [
        root / 'index.html',
        root / 'webapp' / 'index.html',
        root / 'docs' / 'index.html'
    ]
    for p in files:
        if p.exists():
            optimize_file(p)

if __name__ == '__main__':
    main()
