import os

files = ['index.html', 'webapp/index.html', 'docs/index.html']

old_css = """    /* Deals List in Analytics */
    .deals-section {
      margin-top: 6px;
    }

    .deals-section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }

    .deals-section-title {
      font-size: 14px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .deals-count-pill {
      background: rgba(255, 255, 255, 0.08);
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 8px;
      color: var(--text-muted);
    }

    .deal-item-row {
      background: var(--card-bg);
      border: 0.5px solid var(--card-border);
      border-radius: 16px;
      padding: 12px 14px;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      transition: all 0.2s ease;
    }

    .deal-item-row:hover {
      border-color: var(--card-border-hover);
    }

    .deal-left {
      flex: 1;
      min-width: 0;
    }

    .deal-model-title {
      font-size: 14px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .deal-storage-badge {
      font-size: 10px;
      font-weight: 700;
      color: var(--accent-highlight);
      background: var(--accent-subtle);
      padding: 2px 6px;
      border-radius: 6px;
    }

    .deal-meta-line {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 3px;
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }

    .deal-profit-badge {
      font-size: 14px;
      font-weight: 800;
      color: var(--success-color);
      white-space: nowrap;
      text-align: right;
    }

    .btn-delete-deal {
      background: transparent;
      border: none;
      color: var(--text-tertiary);
      cursor: pointer;
      font-size: 14px;
      padding: 4px;
      border-radius: 6px;
      transition: color 0.15s ease;
    }

    .btn-delete-deal:hover {
      color: var(--danger-color);
    }"""

new_css = """    /* Deals List in Analytics */
    .deals-section {
      margin-top: 8px;
      padding: 14px 14px 8px !important;
      box-sizing: border-box !important;
      overflow: hidden !important;
      width: 100% !important;
      max-width: 100% !important;
    }

    .deals-section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      gap: 8px;
      width: 100%;
      box-sizing: border-box;
    }

    .deals-section-title {
      font-size: 14px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 6px;
      min-width: 0;
    }

    .deals-count-pill {
      background: rgba(255, 255, 255, 0.08);
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 8px;
      color: var(--text-muted);
      flex-shrink: 0;
    }

    .deal-item-row {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 10px 12px;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      box-sizing: border-box;
      width: 100%;
      max-width: 100%;
      transition: all 0.2s ease;
    }

    .deal-item-row:hover {
      border-color: rgba(255, 255, 255, 0.2);
      background: rgba(255, 255, 255, 0.06);
    }

    .deal-left {
      flex: 1 1 auto;
      min-width: 0;
      overflow: hidden;
    }

    .deal-model-title {
      font-size: 13.5px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .deal-model-title span:first-child {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .deal-storage-badge {
      font-size: 10px;
      font-weight: 700;
      color: var(--accent-highlight);
      background: var(--accent-subtle);
      padding: 2px 6px;
      border-radius: 6px;
      flex-shrink: 0;
    }

    .deal-meta-line {
      font-size: 10.5px;
      color: var(--text-muted);
      margin-top: 3px;
      display: flex;
      align-items: center;
      gap: 4px 6px;
      flex-wrap: wrap;
      line-height: 1.35;
    }

    .deal-right {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
      text-align: right;
    }

    .deal-profit-badge {
      font-size: 13px;
      font-weight: 800;
      color: var(--success-color);
      white-space: nowrap;
      text-align: right;
      line-height: 1.2;
    }

    .btn-delete-deal {
      background: transparent;
      border: none;
      color: var(--text-tertiary);
      cursor: pointer;
      font-size: 14px;
      padding: 4px;
      border-radius: 6px;
      transition: color 0.15s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .btn-delete-deal:hover {
      color: var(--danger-color);
    }"""

old_render = """      if (userDeals.length === 0) {
        dealsListEl.innerHTML = `
          <div style="text-align: center; padding: 30px 10px; color: var(--text-muted); background: var(--card-bg); border-radius: 16px; border: 0.5px solid var(--card-border);">
            <div class="svg-icon" style="width: 32px; height: 32px; margin: 0 auto 8px; color: var(--text-tertiary);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg></div>
            <p style="font-size: 14px; font-weight: 600; color: #fff;">Нет записанных продаж</p>
            <p style="font-size: 12px; margin-top: 4px;">Нажмите «<span class="svg-icon" style="width: 11px; height: 11px; margin-right: 3px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"/><path d="M12 5v14"/></svg></span> Записать сделку», чтобы вести учет продаж</p>
          </div>
        `;
        return;
      }

      const sortedAll = [...userDeals].sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0));
      dealsListEl.innerHTML = sortedAll.map(d => {
        const dDate = d.date ? new Date(d.date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }) : '';
        const marginPct = d.buyPrice > 0 ? Math.round(((d.profit || 0) / d.buyPrice) * 100) : 0;
        return `
          <div class="deal-item-row" data-id="${d.id}">
            <div class="deal-left">
              <div class="deal-model-title">
                <span>${d.model}</span>
                ${d.storage ? `<span class="deal-storage-badge">${d.storage} GB</span>` : ''}
              </div>
              <div class="deal-meta-line">
                <span>${dDate}</span>
                <span>•</span>
                <span>Выкуп: ${(d.buyPrice || 0).toLocaleString('ru-RU')} ₽ → ${(d.sellPrice || 0).toLocaleString('ru-RU')} ₽</span>
                ${d.note ? `<span>• ${d.note}</span>` : ''}
              </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <div class="deal-profit-badge">
                +${(d.profit || 0).toLocaleString('ru-RU')} ₽
                <div style="font-size: 10px; color: var(--text-muted); font-weight: 600;">+${marginPct}% маржа</div>
              </div>
              <button type="button" class="btn-delete-deal" data-id="${d.id}" title="Удалить сделку"><span class="svg-icon" style="width:11px; height:11px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></span></button>
            </div>
          </div>
        `;
      }).join('');"""

new_render = """      if (userDeals.length === 0) {
        dealsListEl.innerHTML = `
          <div style="text-align: center; padding: 26px 14px; color: var(--text-muted); background: rgba(255, 255, 255, 0.04); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.08);">
            <div class="svg-icon" style="width: 28px; height: 28px; margin: 0 auto 8px; color: var(--text-tertiary);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg></div>
            <p style="font-size: 13.5px; font-weight: 600; color: #fff;">Нет записанных продаж</p>
            <p style="font-size: 11.5px; margin-top: 4px;">Нажмите «<span class="svg-icon" style="width: 11px; height: 11px; margin-right: 3px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"/><path d="M12 5v14"/></svg></span> Записать», чтобы вести учет продаж</p>
          </div>
        `;
        return;
      }

      const sortedAll = [...userDeals].sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0));
      dealsListEl.innerHTML = sortedAll.map(d => {
        const dDate = d.date ? new Date(d.date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }) : '';
        const marginPct = d.buyPrice > 0 ? Math.round(((d.profit || 0) / d.buyPrice) * 100) : 0;
        return `
          <div class="deal-item-row" data-id="${d.id}">
            <div class="deal-left">
              <div class="deal-model-title">
                <span>${d.model}</span>
                ${d.storage ? `<span class="deal-storage-badge">${d.storage} GB</span>` : ''}
              </div>
              <div class="deal-meta-line">
                <span>${dDate}</span>
                <span>•</span>
                <span>Выкуп: ${(d.buyPrice || 0).toLocaleString('ru-RU')} ₽ → ${(d.sellPrice || 0).toLocaleString('ru-RU')} ₽</span>
                ${d.note ? `<span>• ${d.note}</span>` : ''}
              </div>
            </div>
            <div class="deal-right">
              <div class="deal-profit-badge">
                +${(d.profit || 0).toLocaleString('ru-RU')} ₽
                <div style="font-size: 10px; color: var(--text-muted); font-weight: 600;">+${marginPct}% маржа</div>
              </div>
              <button type="button" class="btn-delete-deal" data-id="${d.id}" title="Удалить сделку"><span class="svg-icon" style="width:11px; height:11px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></span></button>
            </div>
          </div>
        `;
      }).join('');"""

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_css not in content:
        raise ValueError(f'old_css not found in {path}')
    if old_render not in content:
        raise ValueError(f'old_render not found in {path}')
    content = content.replace(old_css, new_css).replace(old_render, new_render)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Successfully updated {path}')
