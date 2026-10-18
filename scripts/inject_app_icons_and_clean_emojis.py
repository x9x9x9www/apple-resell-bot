#!/usr/bin/env python3
"""
Injects AppIcons definition and completes full emoji removal from buttons & UI.
"""

from pathlib import Path
import re

APP_ICONS_JS = """    // Apple SF Symbol Style SVG Icons Library (No Emojis)
    const AppIcons = {
      tag: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"/><circle cx="7" cy="7" r=".5" fill="currentColor"/></svg>`,
      analytics: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>`,
      settings: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>`,
      search: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>`,
      plus: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>`,
      mapPin: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>`,
      save: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>`,
      reset: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>`,
      trash: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>`,
      close: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>`,
      edit: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>`,
      check: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
      folder: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg>`,
      phone: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg>`,
      laptop: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55A1 1 0 0 1 20.38 20H3.62a1 1 0 0 1-.9-1.45L4 16"/></svg>`,
      tablet: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><line x1="12" x2="12.01" y1="18" y2="18"/></svg>`,
      gamepad: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" x2="10" y1="12" y2="12"/><line x1="8" x2="8" y1="10" y2="14"/><rect width="20" height="12" x="2" y="6" rx="6"/></svg>`,
      headphones: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/></svg>`,
      watch: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="7"/><polyline points="12 9 12 12 13.5 13.5"/><path d="M16.51 17.35l-.35 3.83a2 2 0 0 1-2 1.82H9.83a2 2 0 0 1-2-1.82l-.35-3.83m.01-10.7.35-3.83A2 2 0 0 1 9.83 1h4.34a2 2 0 0 1 2 1.82l.35 3.83"/></svg>`
    };
"""

SVG_EMOJI_PICKER = """        <div class="emoji-row" id="createEmojiRow">
          <span class="emoji-chip active" data-icon="phone" title="Смартфон"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg></span></span>
          <span class="emoji-chip" data-icon="laptop" title="Ноутбук"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55A1 1 0 0 1 20.38 20H3.62a1 1 0 0 1-.9-1.45L4 16"/></svg></span></span>
          <span class="emoji-chip" data-icon="tablet" title="Планшет"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><line x1="12" x2="12.01" y1="18" y2="18"/></svg></span></span>
          <span class="emoji-chip" data-icon="headphones" title="Наушники"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/></svg></span></span>
          <span class="emoji-chip" data-icon="watch" title="Часы"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="7"/><polyline points="12 9 12 12 13.5 13.5"/><path d="M16.51 17.35l-.35 3.83a2 2 0 0 1-2 1.82H9.83a2 2 0 0 1-2-1.82l-.35-3.83m.01-10.7.35-3.83A2 2 0 0 1 9.83 1h4.34a2 2 0 0 1 2 1.82l.35 3.83"/></svg></span></span>
          <span class="emoji-chip" data-icon="gamepad" title="Консоли"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="6" x2="10" y1="12" y2="12"/><line x1="8" x2="8" y1="10" y2="14"/><rect width="20" height="12" x="2" y="6" rx="6"/></svg></span></span>
          <span class="emoji-chip" data-icon="folder" title="Папка"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg></span></span>
        </div>"""

SVG_EDIT_EMOJI_PICKER = """        <div class="emoji-row" id="editEmojiRow">
          <span class="emoji-chip active" data-icon="phone" title="Смартфон"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg></span></span>
          <span class="emoji-chip" data-icon="laptop" title="Ноутбук"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 16V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v9m16 0H4m16 0 1.28 2.55A1 1 0 0 1 20.38 20H3.62a1 1 0 0 1-.9-1.45L4 16"/></svg></span></span>
          <span class="emoji-chip" data-icon="tablet" title="Планшет"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><line x1="12" x2="12.01" y1="18" y2="18"/></svg></span></span>
          <span class="emoji-chip" data-icon="headphones" title="Наушники"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/></svg></span></span>
          <span class="emoji-chip" data-icon="watch" title="Часы"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="7"/><polyline points="12 9 12 12 13.5 13.5"/><path d="M16.51 17.35l-.35 3.83a2 2 0 0 1-2 1.82H9.83a2 2 0 0 1-2-1.82l-.35-3.83m.01-10.7.35-3.83A2 2 0 0 1 9.83 1h4.34a2 2 0 0 1 2 1.82l.35 3.83"/></svg></span></span>
          <span class="emoji-chip" data-icon="gamepad" title="Консоли"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="6" x2="10" y1="12" y2="12"/><line x1="8" x2="8" y1="10" y2="14"/><rect width="20" height="12" x="2" y="6" rx="6"/></svg></span></span>
          <span class="emoji-chip" data-icon="folder" title="Папка"><span class="svg-icon" style="width:14px;height:14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg></span></span>
        </div>"""

def process_file(filepath: Path):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Inject AppIcons right after <script>
    if "const AppIcons =" not in content:
        content = content.replace("<script>\n", "<script>\n" + APP_ICONS_JS + "\n", 1)
        print(f"Injected AppIcons into {filepath.name}")

    # 2. Replace emoji pickers with SVG icon pickers
    old_create_picker_pattern = re.compile(r'<div class="emoji-row" id="createEmojiRow">[\s\S]*?</div>')
    content = old_create_picker_pattern.sub(SVG_EMOJI_PICKER, content, count=1)

    old_edit_picker_pattern = re.compile(r'<div class="emoji-row" id="editEmojiRow">[\s\S]*?</div>')
    content = old_edit_picker_pattern.sub(SVG_EDIT_EMOJI_PICKER, content, count=1)

    content = content.replace('<label class="form-label">Иконка / Эмодзи:</label>', '<label class="form-label">Иконка папки:</label>')
    content = content.replace('value="📱"', 'value="phone"')
    content = content.replace("value = '📱';", "value = 'phone';")
    content = content.replace("value = cat.icon || '📱';", "value = cat.icon || 'phone';")
    content = content.replace("|| '📁'", "|| 'folder'")
    content = content.replace("|| '📱'", "|| 'phone'")
    content = content.replace("opt.textContent = `${cat.icon || '📁'} ${cat.name}`;", "opt.textContent = cat.name;")
    content = content.replace("opt.textContent = `${cat.icon || 'folder'} ${cat.name}`;", "opt.textContent = cat.name;")
    content = content.replace("chip.textContent.trim()", "chip.dataset.icon || 'phone'")
    content = content.replace("c.textContent.trim() === cat.icon", "c.dataset.icon === cat.icon")
    content = content.replace("document.getElementById('newCatEmoji').value = chip.dataset.icon || 'phone';", "document.getElementById('newCatEmoji').value = chip.dataset.icon || 'phone';")
    content = content.replace("document.getElementById('editCatEmoji').value = chip.dataset.icon || 'phone';", "document.getElementById('editCatEmoji').value = chip.dataset.icon || 'phone';")

    # Update POPULAR_TEMPLATES icons to icon names
    content = content.replace('icon: "📱"', 'icon: "phone"')
    content = content.replace('icon: "💻"', 'icon: "laptop"')
    content = content.replace('icon: "📟"', 'icon: "tablet"')
    content = content.replace('icon: "🎮"', 'icon: "gamepad"')
    content = content.replace('icon: "🎧"', 'icon: "headphones"')
    content = content.replace('icon: "⌚️"', 'icon: "watch"')
    content = content.replace('icon: "📁"', 'icon: "folder"')
    content = content.replace('icon: "🗑️"', 'icon: ""')
    content = content.replace('icon: "🔄"', 'icon: ""')

    # 3. Clean remaining button texts
    content = content.replace("btn.textContent = `✅ Добавить (${selectedAddModalMemories.size} конф.)`;", "btn.textContent = `Добавить (${selectedAddModalMemories.size} конф.)`;")
    content = content.replace("${detected.name || 'Параметры подставлены'} ⚡️", "${detected.name || 'Параметры подставлены'}")
    content = content.replace('icon = "⚡️"', 'icon = ""')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Processed {filepath.name}")

def main():
    root = Path(__file__).resolve().parent.parent
    for name in ['index.html', 'webapp/index.html', 'docs/index.html']:
        p = root / name
        if p.exists():
            process_file(p)

if __name__ == '__main__':
    main()
