#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

def clean_emojis():
    with open("webapp/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update Category Chips in Add Folder & Manage Folder Modals
    old_cat_emojis_html = """        <div class="emoji-picker-row" id="catEmojiRow">
          <span class="emoji-chip active">📱</span>
          <span class="emoji-chip">💻</span>
          <span class="emoji-chip">📟</span>
          <span class="emoji-chip">🎧</span>
          <span class="emoji-chip">⌚️</span>
          <span class="emoji-chip">🎮</span>
          <span class="emoji-chip">💨</span>
          <span class="emoji-chip">📷</span>
          <span class="emoji-chip">📺</span>
          <span class="emoji-chip">⚡️</span>
          <span class="emoji-chip">📁</span>
          <span class="emoji-chip">⭐️</span>
        </div>"""

    new_cat_emojis_html = """        <div class="emoji-picker-row" id="catEmojiRow">
          <span class="emoji-chip active" data-icon="phone"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg></span>Смартфоны</span>
          <span class="emoji-chip" data-icon="laptop"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55A1 1 0 0 1 20.38 20H3.62a1 1 0 0 1-.9-1.45L4 16"/></svg></span>Ноутбуки</span>
          <span class="emoji-chip" data-icon="tablet"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><line x1="12" x2="12.01" y1="18" y2="18"/></svg></span>Планшеты</span>
          <span class="emoji-chip" data-icon="headphones"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/></svg></span>Аудио</span>
          <span class="emoji-chip" data-icon="watch"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="7"/><polyline points="12 9 12 12 13.5 13.5"/><path d="M16.51 17.35l-.35 3.83a2 2 0 0 1-2 1.82H9.83a2 2 0 0 1-2-1.82l-.35-3.83m.01-10.7.35-3.83A2 2 0 0 1 9.83 1h4.34a2 2 0 0 1 2 1.82l.35 3.83"/></svg></span>Часы</span>
          <span class="emoji-chip" data-icon="gamepad"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="20" height="12" x="2" y="6" rx="6"/><line x1="6" x2="10" y1="12" y2="12"/><line x1="8" x2="8" y1="10" y2="14"/></svg></span>Консоли</span>
          <span class="emoji-chip" data-icon="folder"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg></span>Другое</span>
        </div>"""
    html = html.replace(old_cat_emojis_html, new_cat_emojis_html)

    old_edit_cat_emojis = """        <div class="emoji-picker-row" id="editEmojiRow">
          <span class="emoji-chip">📱</span>
          <span class="emoji-chip">💻</span>
          <span class="emoji-chip">📟</span>
          <span class="emoji-chip">🎧</span>
          <span class="emoji-chip">⌚️</span>
          <span class="emoji-chip">🎮</span>
          <span class="emoji-chip">💨</span>
          <span class="emoji-chip">📷</span>
          <span class="emoji-chip">📺</span>
          <span class="emoji-chip">⚡️</span>
          <span class="emoji-chip">📁</span>
          <span class="emoji-chip">⭐️</span>
        </div>"""
    new_edit_cat_emojis = """        <div class="emoji-picker-row" id="editEmojiRow">
          <span class="emoji-chip" data-icon="phone"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg></span>Смартфоны</span>
          <span class="emoji-chip" data-icon="laptop"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55A1 1 0 0 1 20.38 20H3.62a1 1 0 0 1-.9-1.45L4 16"/></svg></span>Ноутбуки</span>
          <span class="emoji-chip" data-icon="tablet"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><line x1="12" x2="12.01" y1="18" y2="18"/></svg></span>Планшеты</span>
          <span class="emoji-chip" data-icon="headphones"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/></svg></span>Аудио</span>
          <span class="emoji-chip" data-icon="watch"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="7"/><polyline points="12 9 12 12 13.5 13.5"/><path d="M16.51 17.35l-.35 3.83a2 2 0 0 1-2 1.82H9.83a2 2 0 0 1-2-1.82l-.35-3.83m.01-10.7.35-3.83A2 2 0 0 1 9.83 1h4.34a2 2 0 0 1 2 1.82l.35 3.83"/></svg></span>Часы</span>
          <span class="emoji-chip" data-icon="gamepad"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="20" height="12" x="2" y="6" rx="6"/><line x1="6" x2="10" y1="12" y2="12"/><line x1="8" x2="8" y1="10" y2="14"/></svg></span>Консоли</span>
          <span class="emoji-chip" data-icon="folder"><span class="svg-icon" style="width:14px; height:14px; margin-right:4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg></span>Другое</span>
        </div>"""
    html = html.replace(old_edit_cat_emojis, new_edit_cat_emojis)

    # Clean dropdown options in Add Model Modal
    html = html.replace('<option value="iphone">📱 iPhone</option>', '<option value="iphone">iPhone</option>')
    html = html.replace('<option value="macbook">💻 Mac</option>', '<option value="macbook">Mac</option>')
    html = html.replace('<option value="samsung">📱 Samsung</option>', '<option value="samsung">Samsung</option>')
    html = html.replace('<option value="pixel">📱 Pixel</option>', '<option value="pixel">Pixel</option>')
    html = html.replace('<option value="ipad">📟 iPad</option>', '<option value="ipad">iPad</option>')
    html = html.replace('<option value="consoles">🎮 Консоли</option>', '<option value="consoles">Консоли</option>')
    html = html.replace('<option value="__new__">➕ Создать новую папку...</option>', '<option value="__new__">Создать новую папку...</option>')

    # Clean other modal text
    html = html.replace('<span>🔗 Ссылка на поиск Авито/Юлы</span>', '<span>Ссылка на поиск Авито/Юлы</span>')
    html = html.replace('<span style="font-size:11px; color:var(--accent-highlight); font-weight:normal;">⚡️ автозаполнение</span>', '<span style="font-size:11px; color:var(--text-muted); font-weight:normal;">автозаполнение</span>')
    html = html.replace('💡 Опционально. Если вставить ссылку', 'Опционально. Если вставить ссылку')
    html = html.replace('💡 Можно выбрать несколько объемов сразу', 'Можно выбрать несколько объемов сразу')
    html = html.replace('<span id="btnSubmitNewModelText">✅ Добавить в матрицу</span>', '<span id="btnSubmitNewModelText">Добавить в матрицу</span>')
    html = html.replace('<h3 class="modal-title" id="quickAddStorageTitle">➕ Добавить объем</h3>', '<h3 class="modal-title" id="quickAddStorageTitle">Добавить объем</h3>')
    html = html.replace('<span>✅ Добавить объем в модель</span>', '<span>Добавить объем в модель</span>')
    html = html.replace('<h3 class="modal-title" id="editLinkModalTitle">🔗 Ссылка поиска</h3>', '<h3 class="modal-title" id="editLinkModalTitle">Ссылка поиска</h3>')
    html = html.replace('<span>💾 Сохранить ссылку</span>', '<span>Сохранить ссылку</span>')
    html = html.replace('<span>✨ Настройки применены в бота!</span>', '<span>Настройки применены в бота!</span>')

    # Update Toast Icon
    html = re.sub(r'<div class="dynamic-toast-icon" id="dynamicToastIcon">.*?</div>',
                  '<div class="dynamic-toast-icon svg-icon" id="dynamicToastIcon" style="width:16px; height:16px; color:#fff;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg></div>',
                  html)

    # 2. Update JS getDeviceIcon and getCategoryIconSvg
    icon_helpers_js = """
    function getCategoryIconSvg(iconKey) {
      if (!iconKey) return AppIcons.folder;
      const k = String(iconKey).toLowerCase();
      if (k === 'laptop' || k.includes('mac') || k.includes('💻')) return AppIcons.laptop;
      if (k === 'tablet' || k.includes('ipad') || k.includes('📟')) return AppIcons.tablet;
      if (k === 'gamepad' || k.includes('playstation') || k.includes('xbox') || k.includes('🎮')) return AppIcons.gamepad;
      if (k === 'headphones' || k.includes('audio') || k.includes('airpods') || k.includes('🎧')) return AppIcons.headphones;
      if (k === 'watch' || k.includes('часы') || k.includes('⌚')) return AppIcons.watch;
      if (k === 'phone' || k.includes('iphone') || k.includes('samsung') || k.includes('pixel') || k.includes('📱')) return AppIcons.phone;
      return AppIcons.folder;
    }

    function getDeviceIcon(name, series) {
      const lower = ((name || '') + ' ' + (series || '')).toLowerCase();
      if (lower.includes('macbook') || lower.includes('mac')) return AppIcons.laptop;
      if (lower.includes('ipad')) return AppIcons.tablet;
      if (lower.includes('playstation') || lower.includes('ps5') || lower.includes('steam deck') || lower.includes('xbox')) return AppIcons.gamepad;
      if (lower.includes('watch') || lower.includes('часы')) return AppIcons.watch;
      if (lower.includes('наушники') || lower.includes('airpods') || lower.includes('sony') || lower.includes('wh-')) return AppIcons.headphones;
      return AppIcons.phone;
    }
    """

    # Replace old getDeviceIcon
    old_device_icon_pattern = r"function getDeviceIcon\(name, series\)\s*\{[^}]*return '📱';\s*\}"
    html = re.sub(old_device_icon_pattern, icon_helpers_js, html)

    # In renderSeriesBar:
    html = html.replace("titleSpan.textContent = `${cat.icon || '📁'} ${cat.name}`;",
                        "titleSpan.innerHTML = `<span class=\"svg-icon\" style=\"width:13px; height:13px; margin-right:4px; opacity:0.85;\">${getCategoryIconSvg(cat.icon)}</span>${escapeHtml(cat.name)}`;")
    html = html.replace("editBtn.textContent = '✏️';", "editBtn.innerHTML = AppIcons.edit;")
    html = html.replace("addBtn.innerHTML = '<span>➕ Папка</span>';", "addBtn.innerHTML = `<span class=\"svg-icon\" style=\"width:11px; height:11px; margin-right:3px;\">${AppIcons.plus}</span><span>Папка</span>`;")
    html = html.replace("btnToggle.innerHTML = '⏸ Выкл. всё';", "btnToggle.innerHTML = 'Выкл. всё';")
    html = html.replace("btnToggle.innerHTML = '▶️ Вкл. всё';", "btnToggle.innerHTML = 'Вкл. всё';")

    # In renderCards:
    # Empty states
    html = html.replace('<p style="font-size: 32px; margin-bottom: 8px">📭</p>',
                        '<div class="svg-icon" style="width: 44px; height: 44px; margin: 0 auto 12px; color: var(--text-tertiary);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg></div>')
    html = html.replace('<p style="font-size: 32px; margin-bottom: 8px">📁</p>',
                        '<div class="svg-icon" style="width: 44px; height: 44px; margin: 0 auto 12px; color: var(--text-tertiary);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg></div>')
    html = html.replace('<p style="font-size: 26px; margin-bottom: 6px">🔍</p>',
                        '<div class="svg-icon" style="width: 38px; height: 38px; margin: 0 auto 10px; color: var(--text-tertiary);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg></div>')

    # Card badges & links
    html = html.replace('? `<span class="badge-category">${catObj.icon || \'📁\'} ${catObj.name}</span>`',
                        '? `<span class="badge-category"><span class="svg-icon" style="width:11px; height:11px; margin-right:3px;">${getCategoryIconSvg(catObj.icon)}</span>${catObj.name}</span>`')
    html = html.replace('title="Нажмите, чтобы изменить ссылку: ${activeItem.search_link}">🔗 По ссылке</button>',
                        'title="Нажмите, чтобы изменить ссылку: ${activeItem.search_link}"><span class="svg-icon" style="width:11px; height:11px; margin-right:3px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" x2="22" y1="12" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg></span>По ссылке</button>')
    html = html.replace('title="Привязать ссылку поиска с Авито/Юлы">+ 🔗 ссылка</button>',
                        'title="Привязать ссылку поиска с Авито/Юлы"><span class="svg-icon" style="width:11px; height:11px; margin-right:3px;">${AppIcons.plus}</span>Ссылка</button>')
    html = html.replace('<button class="btn-delete" title="Удалить выбранную конфигурацию">✕</button>',
                        '<button class="btn-delete" title="Удалить выбранную конфигурацию"><span class="svg-icon" style="width:12px; height:12px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/></svg></span></button>')

    # In KPI Cards
    html = html.replace('<div class="kpi-icon-badge">💰</div>', '<div class="kpi-icon-badge" style="background:rgba(255,255,255,0.08); color:#f5f5f7;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg></div>')
    html = html.replace('<div class="kpi-icon-badge">📱</div>', '<div class="kpi-icon-badge" style="background:rgba(255,255,255,0.08); color:#f5f5f7;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg></div>')
    html = html.replace('<div class="kpi-icon-badge">🎯</div>', '<div class="kpi-icon-badge" style="background:rgba(255,255,255,0.08); color:#f5f5f7;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg></div>')
    html = html.replace('<p style="font-size: 28px; margin-bottom: 6px;">📭</p>', '<div class="svg-icon" style="width: 32px; height: 32px; margin: 0 auto 8px; color: var(--text-tertiary);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg></div>')

    # In Deals items
    html = html.replace('<span>📱 ${d.model}</span>', '<span>${d.model}</span>')
    html = html.replace('<span>📅 ${dDate}</span>', '<span>${dDate}</span>')
    html = html.replace('<span>• 💬 ${d.note}</span>', '<span>• ${d.note}</span>')
    html = html.replace('➔', '→')
    html = html.replace('<button type="button" class="btn-delete-deal" data-id="${d.id}" title="Удалить сделку">✕</button>',
                        '<button type="button" class="btn-delete-deal" data-id="${d.id}" title="Удалить сделку"><span class="svg-icon" style="width:11px; height:11px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></span></button>')

    # In Templates Grid
    html = html.replace("chip.innerHTML = `${tpl.icon} <span>${tpl.name}</span>${isAdded ? ' ✓' : ' ➕'}`;",
                        "chip.innerHTML = `<span class=\"svg-icon\" style=\"width:13px; height:13px; margin-right:4px;\">${getCategoryIconSvg(tpl.icon)}</span> <span>${tpl.name}</span>${isAdded ? ' ✓' : ''}`;")
    html = html.replace("document.getElementById('presetModalTitle').textContent = `${tpl.icon} Добавить: ${tpl.name}`;",
                        "document.getElementById('presetModalTitle').innerHTML = `<span class=\"svg-icon\" style=\"width:16px; height:16px; margin-right:6px;\">${getCategoryIconSvg(tpl.icon)}</span>Добавить: ${tpl.name}`;")

    with open("webapp/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Emojis thoroughly cleaned and replaced with vector SVG icons!")

if __name__ == "__main__":
    clean_emojis()
