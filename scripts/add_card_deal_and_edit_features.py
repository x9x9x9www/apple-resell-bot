import os

files = ['index.html', 'webapp/index.html', 'docs/index.html']

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add CSS for .btn-card-to-analytics and .btn-edit-deal
    old_css_anchor = """    .btn-delete-deal {
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

    new_css = """    .btn-card-to-analytics {
      background: rgba(255, 255, 255, 0.08);
      border: 0.5px solid var(--card-border);
      color: #fff;
      padding: 5px 9px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: -0.2px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 3px;
      box-shadow: var(--card-specular);
      transition: transform 0.15s var(--spring-press), background 0.15s ease;
      white-space: nowrap;
    }
    .btn-card-to-analytics:active {
      transform: scale(0.94);
      background: rgba(255, 255, 255, 0.16);
    }

    .btn-edit-deal {
      background: transparent;
      border: none;
      color: var(--text-tertiary);
      cursor: pointer;
      font-size: 13px;
      padding: 4px;
      border-radius: 6px;
      transition: color 0.15s ease, background 0.15s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .btn-edit-deal:hover {
      color: var(--accent-highlight);
      background: rgba(255, 255, 255, 0.08);
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

    assert old_css_anchor in content, f'old_css_anchor not found in {path}'
    content = content.replace(old_css_anchor, new_css)

    # 2. Update modal header and hidden editing id in #addDealModal
    old_modal_header = """  <!-- Модалка: Запись продажи (Сделка) -->
  <div class="modal-overlay" id="addDealModal">
    <div class="modal-sheet">
      <div class="modal-grabber"></div>
      <div class="modal-header">
        <h3 class="modal-title"><span class="svg-icon" style="width:16px; height:16px; margin-right:6px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg></span>Записать сделку</h3>
        <button class="btn-close-modal" id="btnCloseDealModal"><span class="svg-icon" style="width: 12px; height: 12px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></span></button>
      </div>"""

    new_modal_header = """  <!-- Модалка: Запись продажи (Сделка) -->
  <div class="modal-overlay" id="addDealModal">
    <div class="modal-sheet">
      <div class="modal-grabber"></div>
      <div class="modal-header">
        <h3 class="modal-title"><span class="svg-icon" style="width:16px; height:16px; margin-right:6px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg></span><span id="dealModalTitleText">Записать сделку</span></h3>
        <button class="btn-close-modal" id="btnCloseDealModal"><span class="svg-icon" style="width: 12px; height: 12px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></span></button>
      </div>
      <input type="hidden" id="dealEditingId" value="">"""

    assert old_modal_header in content, f'old_modal_header not found in {path}'
    content = content.replace(old_modal_header, new_modal_header)

    # 3. Update modal submit button text span
    old_modal_btn = """      <button type="button" class="btn-save" id="btnSubmitDeal" style="width: 100%; margin-top: 10px;">
        <span>Сохранить сделку</span>
      </button>"""

    new_modal_btn = """      <button type="button" class="btn-save" id="btnSubmitDeal" style="width: 100%; margin-top: 10px;">
        <span id="btnSubmitDealText">Сохранить сделку</span>
      </button>"""

    assert old_modal_btn in content, f'old_modal_btn not found in {path}'
    content = content.replace(old_modal_btn, new_modal_btn)

    # 4. Add "В аналитику" button to card-footer in renderCards()
    old_card_footer = """          <div class="card-footer" style="display:flex; justify-content:space-between; align-items:center;">
            <span class="profit-badge ${profit < 0 ? 'negative' : ''}" data-current-value="${profit}">Навар: ~${profit.toLocaleString('ru-RU')} ₽</span>
            <button type="button" class="btn-toggle-config ${activeItem.enabled ? 'active' : ''}" title="Отслеживать именно этот объем памяти">
              <span class="config-check-icon">${activeItem.enabled ? '<span class="config-dot active"></span>Включен' : '<span class="config-dot"></span>Отключен'}</span>
            </button>
          </div>"""

    new_card_footer = """          <div class="card-footer" style="display:flex; justify-content:space-between; align-items:center; gap: 8px;">
            <span class="profit-badge ${profit < 0 ? 'negative' : ''}" data-current-value="${profit}">Навар: ~${profit.toLocaleString('ru-RU')} ₽</span>
            <div style="display:flex; align-items:center; gap:6px;">
              <button type="button" class="btn-card-to-analytics" title="Записать продажу этой модели в аналитику">
                <span class="svg-icon" style="width:11px; height:11px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg></span>
                <span>В аналитику</span>
              </button>
              <button type="button" class="btn-toggle-config ${activeItem.enabled ? 'active' : ''}" title="Отслеживать именно этот объем памяти">
                <span class="config-check-icon">${activeItem.enabled ? '<span class="config-dot active"></span>Включен' : '<span class="config-dot"></span>Отключен'}</span>
              </button>
            </div>
          </div>"""

    assert old_card_footer in content, f'old_card_footer not found in {path}'
    content = content.replace(old_card_footer, new_card_footer)

    # 5. Bind .btn-card-to-analytics click event in renderCards()
    old_card_bind = """        const masterSwitch = card.querySelector('.master-switch');"""
    new_card_bind = """        const btnToAnalytics = card.querySelector('.btn-card-to-analytics');
        if (btnToAnalytics) {
          btnToAnalytics.addEventListener('click', (e) => {
            e.stopPropagation();
            if (tg?.HapticFeedback) tg.HapticFeedback.selectionChanged();
            openDealModal({
              model: group.model,
              storage: activeItem.storage || 128,
              buyPrice: activeItem.price || 0,
              sellPrice: activeItem.market || Math.round((activeItem.price || 0) * 1.2),
              note: ''
            });
          });
        }

        const masterSwitch = card.querySelector('.master-switch');"""

    assert old_card_bind in content, f'old_card_bind not found in {path}'
    content = content.replace(old_card_bind, new_card_bind)

    # 6. Update deals list rendering to include edit button and click on row
    old_deal_row = """          <div class="deal-item-row" data-id="${d.id}">
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
          </div>"""

    new_deal_row = """          <div class="deal-item-row" data-id="${d.id}" style="cursor: pointer;" title="Нажмите, чтобы редактировать сделку">
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
              <button type="button" class="btn-edit-deal" data-id="${d.id}" title="Редактировать сделку"><span class="svg-icon" style="width:11px; height:11px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg></span></button>
              <button type="button" class="btn-delete-deal" data-id="${d.id}" title="Удалить сделку"><span class="svg-icon" style="width:11px; height:11px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></span></button>
            </div>
          </div>"""

    assert old_deal_row in content, f'old_deal_row not found in {path}'
    content = content.replace(old_deal_row, new_deal_row)

    # 7. Bind row click and edit button in renderAnalyticsDashboard()
    old_deal_events = """      // Привязка удаления сделки
      dealsListEl.querySelectorAll('.btn-delete-deal').forEach(btn => {"""

    new_deal_events = """      // Клик по строке сделки для редактирования
      dealsListEl.querySelectorAll('.deal-item-row').forEach(row => {
        row.addEventListener('click', (e) => {
          if (e.target.closest('.btn-delete-deal')) return;
          const dealId = row.dataset.id;
          const found = userDeals.find(d => d.id === dealId);
          if (found) {
            if (tg?.HapticFeedback) tg.HapticFeedback.selectionChanged();
            openDealModal(found, true);
          }
        });
      });

      // Клик по кнопке редактирования сделки
      dealsListEl.querySelectorAll('.btn-edit-deal').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const dealId = btn.dataset.id;
          const found = userDeals.find(d => d.id === dealId);
          if (found) {
            if (tg?.HapticFeedback) tg.HapticFeedback.selectionChanged();
            openDealModal(found, true);
          }
        });
      });

      // Привязка удаления сделки
      dealsListEl.querySelectorAll('.btn-delete-deal').forEach(btn => {"""

    assert old_deal_events in content, f'old_deal_events not found in {path}'
    content = content.replace(old_deal_events, new_deal_events)

    # 8. Update openAddDealModal -> openDealModal with full support for new/prefilled/edit modes
    old_open_deal = """    function openAddDealModal() {
      // Заполняем datalist предложениями моделей из текущего каталога
      const dl = document.getElementById('dealModelSuggestions');
      if (dl && currentMatrix) {
        const uniqueModels = Array.from(new Set(currentMatrix.map(m => m.model))).slice(0, 30);
        dl.innerHTML = uniqueModels.map(m => `<option value="${m}">`).join('');
      }

      dealModelInput.value = '';
      dealBuyInput.value = '';
      dealSellInput.value = '';
      dealNoteInput.value = '';
      dealStorageHidden.value = '128';
      document.querySelectorAll('#dealMemoryChips .mem-chip').forEach(c => {
        c.classList.toggle('active', c.dataset.val === '128');
      });

      // По умолчанию сегодня
      const todayStr = new Date().toISOString().split('T')[0];
      dealDateInput.value = todayStr;

      updateDealProfitPreview();
      addDealModal.classList.add('active');
      setTimeout(() => dealModelInput.focus(), 100);
    }

    document.getElementById('btnOpenAddDealModal')?.addEventListener('click', openAddDealModal);
    document.getElementById('btnQuickAddDeal')?.addEventListener('click', openAddDealModal);"""

    new_open_deal = """    function openDealModal(presetOrDeal, isEdit = false) {
      // Заполняем datalist предложениями моделей из текущего каталога
      const dl = document.getElementById('dealModelSuggestions');
      if (dl && currentMatrix) {
        const uniqueModels = Array.from(new Set(currentMatrix.map(m => m.model))).slice(0, 30);
        dl.innerHTML = uniqueModels.map(m => `<option value="${m}">`).join('');
      }

      const modalTitleText = document.getElementById('dealModalTitleText');
      const submitBtnText = document.getElementById('btnSubmitDealText');
      const editingIdInput = document.getElementById('dealEditingId');

      if (isEdit && presetOrDeal && presetOrDeal.id) {
        // Режим редактирования существующей сделки
        if (modalTitleText) modalTitleText.textContent = "Редактировать сделку";
        if (submitBtnText) submitBtnText.textContent = "Сохранить изменения";
        if (editingIdInput) editingIdInput.value = presetOrDeal.id;

        dealModelInput.value = presetOrDeal.model || '';
        dealBuyInput.value = presetOrDeal.buyPrice || '';
        dealSellInput.value = presetOrDeal.sellPrice || '';
        dealDateInput.value = presetOrDeal.date || new Date().toISOString().split('T')[0];
        dealNoteInput.value = presetOrDeal.note || '';

        const storageVal = String(presetOrDeal.storage || 128);
        dealStorageHidden.value = storageVal;
        document.querySelectorAll('#dealMemoryChips .mem-chip').forEach(c => {
          c.classList.toggle('active', c.dataset.val === storageVal);
        });
      } else {
        // Режим новой сделки (пустая или предзаполненная из карточки каталога)
        if (modalTitleText) modalTitleText.textContent = "Записать сделку";
        if (submitBtnText) submitBtnText.textContent = "Сохранить сделку";
        if (editingIdInput) editingIdInput.value = '';

        if (presetOrDeal) {
          dealModelInput.value = presetOrDeal.model || '';
          dealBuyInput.value = presetOrDeal.buyPrice || '';
          dealSellInput.value = presetOrDeal.sellPrice || '';
          dealNoteInput.value = presetOrDeal.note || '';
          const storageVal = String(presetOrDeal.storage || 128);
          dealStorageHidden.value = storageVal;
          document.querySelectorAll('#dealMemoryChips .mem-chip').forEach(c => {
            c.classList.toggle('active', c.dataset.val === storageVal);
          });
        } else {
          dealModelInput.value = '';
          dealBuyInput.value = '';
          dealSellInput.value = '';
          dealNoteInput.value = '';
          dealStorageHidden.value = '128';
          document.querySelectorAll('#dealMemoryChips .mem-chip').forEach(c => {
            c.classList.toggle('active', c.dataset.val === '128');
          });
        }
        dealDateInput.value = new Date().toISOString().split('T')[0];
      }

      updateDealProfitPreview();
      addDealModal.classList.add('active');
      setTimeout(() => {
        if (!dealModelInput.value) dealModelInput.focus();
        else dealBuyInput.focus();
      }, 100);
    }

    function openAddDealModal() {
      openDealModal();
    }

    document.getElementById('btnOpenAddDealModal')?.addEventListener('click', () => openDealModal());
    document.getElementById('btnQuickAddDeal')?.addEventListener('click', () => openDealModal());"""

    assert old_open_deal in content, f'old_open_deal not found in {path}'
    content = content.replace(old_open_deal, new_open_deal)

    # 9. Update btnSubmitDeal to support both edit and create
    old_submit_deal = """      const profit = sellPrice - buyPrice;
      const newDeal = {
        id: 'deal_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
        model,
        storage,
        buyPrice,
        sellPrice,
        profit,
        date,
        note
      };

      userDeals.unshift(newDeal);
      saveUserDeals();
      renderAnalyticsDashboard();
      addDealModal.classList.remove('active');

      if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
      showDynamicIsland("Сделка сохранена", `+${profit.toLocaleString('ru-RU')} ₽ чистая маржа`, "");
    });"""

    new_submit_deal = """      const profit = sellPrice - buyPrice;
      const editingId = document.getElementById('dealEditingId')?.value;

      if (editingId) {
        // Обновляем существующую сделку
        const dealIndex = userDeals.findIndex(d => d.id === editingId);
        if (dealIndex !== -1) {
          userDeals[dealIndex] = {
            ...userDeals[dealIndex],
            model,
            storage,
            buyPrice,
            sellPrice,
            profit,
            date,
            note
          };
          saveUserDeals();
          renderAnalyticsDashboard();
          addDealModal.classList.remove('active');
          if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
          showDynamicIsland("Сделка обновлена", `«${model}» сохранена`, "");
          return;
        }
      }

      // Создаем новую сделку
      const newDeal = {
        id: 'deal_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
        model,
        storage,
        buyPrice,
        sellPrice,
        profit,
        date,
        note
      };

      userDeals.unshift(newDeal);
      saveUserDeals();
      renderAnalyticsDashboard();
      addDealModal.classList.remove('active');

      if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
      showDynamicIsland("Сделка сохранена", `+${profit.toLocaleString('ru-RU')} ₽ чистая маржа`, "");
    });"""

    assert old_submit_deal in content, f'old_submit_deal not found in {path}'
    content = content.replace(old_submit_deal, new_submit_deal)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Successfully updated {path}')
