#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

def update():
    with open("webapp/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Add Ambient Glow Top and Bottom right after <body>
    glow_markup = """<body>
  <!-- ==================== RADIANT TOP & BOTTOM GLOW ATMOSPHERE ==================== -->
  <div class="glow-atmosphere-top" aria-hidden="true"></div>
  <div class="glow-atmosphere-bottom" aria-hidden="true"></div>
"""
    html = re.sub(r"<body>", glow_markup, html, count=1)

    # 2. Update Central 3D iPhone Stage:
    # Remove old hero3dStage and replace with the Centered 3D iPhone Hub
    old_hero_pattern = r'<!-- ==================== 3D IPHONE SHOWCASE HERO ==================== -->.*?<!-- Поиск -->'
    new_hero_markup = """<!-- ==================== CENTRAL 3D IPHONE LIQUID GLASS HUB ==================== -->
    <div class="hero-center-stage" id="heroCenterStage">
      <div class="hero-stage-aura"></div>

      <!-- Interactive Single 3D iPhone in the Center (angled at ~30 deg) -->
      <div class="iphone-3d-scene" id="iphone3dScene" title="Потяните для свободного 3D вращения">
        <div class="iphone-3d-device" id="iphone3dDevice">
          <!-- Front Face: Single iPhone Screen at 30 deg -->
          <div class="iphone-face iphone-face-front">
            <img src="./iphone_single_front.png" alt="3D iPhone" class="iphone-render-img">
            <div class="iphone-glass-sheen"></div>
          </div>
          <!-- Back Face: Titanium with Camera Bump -->
          <div class="iphone-face iphone-face-back">
            <img src="./iphone_single_back.png" alt="3D iPhone Back" class="iphone-render-img">
          </div>
        </div>
        <!-- 3D Ground Shadow -->
        <div class="iphone-3d-ground-shadow"></div>
      </div>

      <!-- Central Info Badge -->
      <div class="hero-center-info">
        <div class="liquid-glass-badge">
          <span class="liquid-glass-dot"></span>
          <span>APPLE RESELL PRO</span>
        </div>
        <h2 class="hero-center-headline">Интеллектуальный радар</h2>
        <p class="hero-center-subline">Мониторинг и моментальный выкуп с Авито и Юлы</p>
      </div>

      <!-- Central Liquid Glass Navigation Hub Buttons (from the center 3D iPhone) -->
      <div class="hero-central-glass-nav" id="heroCentralGlassNav">
        <button type="button" class="liquid-glass-hub-pill active" id="hubBtnCatalog" data-tab="catalog">
          <span class="svg-icon" style="width:16px; height:16px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"/><circle cx="7" cy="7" r=".5" fill="currentColor"/></svg>
          </span>
          <span>Прайс-лист</span>
        </button>
        <button type="button" class="liquid-glass-hub-pill" id="hubBtnAnalytics" data-tab="analytics">
          <span class="svg-icon" style="width:16px; height:16px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
          </span>
          <span>Аналитика</span>
        </button>
        <button type="button" class="liquid-glass-hub-pill" id="hubBtnSettings" data-tab="settings">
          <span class="svg-icon" style="width:16px; height:16px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          </span>
          <span>Настройки</span>
        </button>
      </div>
    </div>

    <!-- Поиск -->"""

    html = re.sub(old_hero_pattern, new_hero_markup, html, flags=re.DOTALL)

    # 3. Inject Enhanced Liquid Glass & 3D Center CSS styles
    liquid_glass_css = """
    /* ========================================================
       TOP & BOTTOM ETHEREAL RADIANT GLOW (HIGH VISIBILITY)
       ======================================================== */
    .glow-atmosphere-top {
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
    }

    /* ========================================================
       CENTRAL 3D IPHONE HUB & STAGE
       ======================================================== */
    .hero-center-stage {
      position: relative;
      border-radius: 36px !important;
      padding: 24px 18px 22px;
      margin-bottom: 20px;
      overflow: hidden;
      perspective: 1200px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      background: linear-gradient(145deg, rgba(28, 32, 42, 0.65) 0%, rgba(15, 17, 24, 0.78) 100%) !important;
      backdrop-filter: blur(36px) saturate(210%) brightness(1.06) !important;
      -webkit-backdrop-filter: blur(36px) saturate(210%) brightness(1.06) !important;
      border: 1.2px solid rgba(255, 255, 255, 0.36) !important;
      box-shadow:
        inset 0 2px 3px 0 rgba(255, 255, 255, 0.8),
        inset 0 -2px 3px 0 rgba(0, 0, 0, 0.45),
        inset 2px 0 2.5px 0 rgba(255, 255, 255, 0.35),
        inset -2px 0 2.5px 0 rgba(255, 255, 255, 0.2),
        0 24px 50px -10px rgba(0, 0, 0, 0.75),
        0 0 30px rgba(180, 215, 255, 0.16) !important;
      z-index: 2;
    }

    .hero-stage-aura {
      position: absolute;
      top: 10%;
      left: 50%;
      transform: translateX(-50%);
      width: 280px;
      height: 280px;
      background: radial-gradient(circle, rgba(200, 230, 255, 0.18) 0%, rgba(140, 180, 240, 0.08) 45%, transparent 75%);
      pointer-events: none;
      z-index: 1;
      filter: blur(30px);
    }

    /* 3D Scene containing ONE single iPhone at ~30 degrees in the Center */
    .iphone-3d-scene {
      position: relative;
      width: 220px;
      height: 270px;
      perspective: 1200px;
      perspective-origin: 50% 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 4px auto 16px;
      cursor: grab;
      touch-action: pan-y;
      z-index: 2;
    }
    .iphone-3d-scene:active {
      cursor: grabbing;
    }

    .iphone-3d-device {
      position: relative;
      width: 140px;
      height: 280px;
      transform-style: preserve-3d;
      transform: rotateY(-30deg) rotateX(10deg) rotateZ(-2deg);
      transition: transform 0.65s cubic-bezier(0.16, 1, 0.3, 1);
      will-change: transform;
    }

    .iphone-face {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      border-radius: 32px;
      backface-visibility: hidden;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .iphone-face-front {
      z-index: 2;
      transform: translateZ(4px);
      box-shadow:
        1px 1px 0 #3a3a3e,
        2px 2px 0 #28282c,
        3px 3px 0 #1c1c1f,
        4px 4px 0 #101012,
        5px 5px 0 #050506,
        14px 26px 42px rgba(0, 0, 0, 0.85);
    }

    .iphone-face-back {
      transform: rotateY(180deg) translateZ(4px);
      box-shadow:
        -1px 1px 0 #3a3a3e,
        -2px 2px 0 #28282c,
        -3px 3px 0 #1c1c1f,
        -4px 4px 0 #101012,
        -5px 5px 0 #050506,
        -14px 26px 42px rgba(0, 0, 0, 0.85);
    }

    .iphone-render-img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      user-select: none;
      -webkit-user-drag: none;
      pointer-events: none;
    }

    .iphone-glass-sheen {
      position: absolute;
      top: -20%;
      left: -60%;
      width: 180%;
      height: 160%;
      background: linear-gradient(125deg, transparent 40%, rgba(255, 255, 255, 0.22) 50%, transparent 60%);
      pointer-events: none;
      border-radius: 32px;
      mix-blend-mode: overlay;
    }

    .iphone-3d-ground-shadow {
      position: absolute;
      bottom: -16px;
      left: 10%;
      width: 80%;
      height: 22px;
      background: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.9) 0%, rgba(0, 0, 0, 0.45) 50%, transparent 75%);
      filter: blur(8px);
      pointer-events: none;
      z-index: 1;
    }

    /* Central Info Typography */
    .hero-center-info {
      position: relative;
      z-index: 2;
      margin-bottom: 16px;
    }

    .liquid-glass-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 14px;
      border-radius: 9999px;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.22) 0%, rgba(255, 255, 255, 0.05) 50%, rgba(255, 255, 255, 0.12) 100%);
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border: 1px solid rgba(255, 255, 255, 0.4);
      box-shadow:
        inset 0 1.5px 2px rgba(255, 255, 255, 0.7),
        inset 0 -1.5px 2px rgba(0, 0, 0, 0.35),
        0 8px 20px rgba(0, 0, 0, 0.4);
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.8px;
      color: #ffffff;
      text-transform: uppercase;
      margin-bottom: 8px;
    }

    .liquid-glass-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #30d158;
      box-shadow: 0 0 10px #30d158;
      animation: pulseDot 2s infinite ease-in-out;
    }

    .hero-center-headline {
      font-size: 21px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: #ffffff;
      margin-bottom: 4px;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
    }

    .hero-center-subline {
      font-size: 12px;
      color: var(--text-muted);
      max-width: 290px;
      margin: 0 auto;
    }

    /* Central Liquid Glass Navigation Hub (Buttons directly from the 3D iPhone) */
    .hero-central-glass-nav {
      position: relative;
      z-index: 2;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      width: 100%;
      flex-wrap: wrap;
    }

    .liquid-glass-hub-pill {
      flex: 1;
      min-width: 95px;
      height: 44px;
      padding: 0 14px;
      border-radius: 9999px !important;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.20) 0%, rgba(255, 255, 255, 0.05) 50%, rgba(255, 255, 255, 0.12) 100%) !important;
      backdrop-filter: blur(28px) saturate(200%) !important;
      -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
      border: 1.2px solid rgba(255, 255, 255, 0.42) !important;
      box-shadow:
        inset 0 2px 3px 0 rgba(255, 255, 255, 0.85),
        inset 0 -2px 3px 0 rgba(0, 0, 0, 0.45),
        inset 2px 0 2.5px 0 rgba(255, 255, 255, 0.35),
        inset -2px 0 2.5px 0 rgba(255, 255, 255, 0.2),
        0 12px 28px -4px rgba(0, 0, 0, 0.65),
        0 0 18px rgba(180, 215, 255, 0.14) !important;
      color: #f5f5f7 !important;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: -0.2px;
      cursor: pointer;
      user-select: none;
      transition: all 0.24s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .liquid-glass-hub-pill:active {
      transform: scale(0.95);
    }

    .liquid-glass-hub-pill.active {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.35) 0%, rgba(255, 255, 255, 0.14) 50%, rgba(255, 255, 255, 0.25) 100%) !important;
      border-color: rgba(255, 255, 255, 0.65) !important;
      color: #ffffff !important;
      box-shadow:
        inset 0 2px 4px 0 rgba(255, 255, 255, 0.95),
        inset 0 -2px 3px 0 rgba(0, 0, 0, 0.5),
        0 8px 24px rgba(0, 0, 0, 0.5),
        0 0 26px rgba(200, 230, 255, 0.32) !important;
    }

    /* ========================================================
       AUTHENTIC LIQUID GLASS ACROSS ALL CARDS, PLATES & PILLS
       ======================================================== */
    .ios-inset-card,
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
    }

    /* Floating Capsule Tab Bar (Liquid Glass Style) */
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
    }

    /* Capsule Pill Buttons */
    .btn-save, .btn-add-model, .btn-add-deal, .btn-condition, .btn-region-badge, .save-bar button {
      border-radius: 9999px !important;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.22) 0%, rgba(255, 255, 255, 0.06) 50%, rgba(255, 255, 255, 0.14) 100%) !important;
      backdrop-filter: blur(24px) saturate(190%) !important;
      -webkit-backdrop-filter: blur(24px) saturate(190%) !important;
      border: 1.2px solid rgba(255, 255, 255, 0.42) !important;
      box-shadow:
        inset 0 2px 3px 0 rgba(255, 255, 255, 0.8),
        inset 0 -2px 3px 0 rgba(0, 0, 0, 0.4),
        0 10px 24px rgba(0, 0, 0, 0.5),
        0 0 16px rgba(180, 215, 255, 0.14) !important;
      color: #ffffff !important;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    .btn-save:hover, .btn-add-model:hover, .btn-add-deal:hover, .btn-region-badge:hover {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.32) 0%, rgba(255, 255, 255, 0.12) 50%, rgba(255, 255, 255, 0.22) 100%) !important;
      border-color: rgba(255, 255, 255, 0.6) !important;
      box-shadow:
        inset 0 2px 4px 0 rgba(255, 255, 255, 0.95),
        inset 0 -2px 3px 0 rgba(0, 0, 0, 0.5),
        0 14px 30px rgba(0, 0, 0, 0.6),
        0 0 24px rgba(200, 230, 255, 0.28) !important;
    }

    /* Save Bar floating liquid glass */
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
    }
    """
    html = html.replace("</style>", liquid_glass_css + "\n</style>", 1)

    # 4. Update switchAppTab in JavaScript:
    # Handle both central hub buttons and 3D iPhone orientation
    new_switch_script = """
      // Central 3D iPhone Dynamic Orientation (Single iPhone at ~30 deg)
      const phone3d = document.getElementById('iphone3dDevice');
      function update3DHeroOrientation(tabName) {
        if (!phone3d) return;
        if (tabName === 'catalog') {
          phone3d.style.transform = 'rotateY(-30deg) rotateX(10deg) rotateZ(-2deg)';
        } else if (tabName === 'analytics') {
          phone3d.style.transform = 'rotateY(30deg) rotateX(10deg) rotateZ(2deg)';
        } else if (tabName === 'settings') {
          phone3d.style.transform = 'rotateY(-180deg) rotateX(10deg) rotateZ(0deg)';
        }

        // Sync Central Hub Buttons
        document.querySelectorAll('.liquid-glass-hub-pill').forEach(btn => {
          btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
      }
      update3DHeroOrientation(tab);
"""
    old_switch_sub = r"\/\/ 3D iPhone Dynamic Orientation based on Active Tab[\s\S]*?update3DHeroOrientation\(tab\);"
    html = re.sub(old_switch_sub, new_switch_script, html, count=1)

    # 5. Wire Central Glass Hub Pills in JS and update free 3D Drag / Swivel handler
    wire_hub_js = """
    // Wire Central Liquid Glass Hub Buttons
    document.querySelectorAll('.liquid-glass-hub-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.dataset.tab;
        if (target) switchAppTab(target);
      });
    });

    // Interactive 3D Single iPhone Swivel with Natural Drag Physics
    (function init3DCenteriPhone() {
      const scene = document.getElementById('iphone3dScene');
      const device = document.getElementById('iphone3dDevice');
      if (!scene || !device) return;

      let isDragging = false;
      let startX = 0;
      let startY = 0;
      let baseRotY = -30;
      let baseRotX = 10;
      let curRotY = -30;
      let curRotX = 10;

      function onStart(x, y) {
        isDragging = true;
        startX = x;
        startY = y;
        device.style.transition = 'none';
      }

      function onMove(x, y) {
        if (!isDragging) return;
        const dx = x - startX;
        const dy = y - startY;
        curRotY = baseRotY + (dx * 0.7);
        curRotX = Math.max(-35, Math.min(35, baseRotX - (dy * 0.5)));
        device.style.transform = `rotateY(${curRotY.toFixed(1)}deg) rotateX(${curRotX.toFixed(1)}deg)`;
      }

      function onEnd() {
        if (!isDragging) return;
        isDragging = false;
        device.style.transition = 'transform 0.65s cubic-bezier(0.16, 1, 0.3, 1)';
        const activeTab = currentAppTab || 'catalog';
        if (activeTab === 'catalog') {
          baseRotY = -30; baseRotX = 10;
          device.style.transform = 'rotateY(-30deg) rotateX(10deg) rotateZ(-2deg)';
        } else if (activeTab === 'analytics') {
          baseRotY = 30; baseRotX = 10;
          device.style.transform = 'rotateY(30deg) rotateX(10deg) rotateZ(2deg)';
        } else {
          baseRotY = -180; baseRotX = 10;
          device.style.transform = 'rotateY(-180deg) rotateX(10deg) rotateZ(0deg)';
        }
      }

      scene.addEventListener('mousedown', (e) => onStart(e.clientX, e.clientY));
      window.addEventListener('mousemove', (e) => onMove(e.clientX, e.clientY));
      window.addEventListener('mouseup', onEnd);

      scene.addEventListener('touchstart', (e) => {
        if (e.touches && e.touches[0]) onStart(e.touches[0].clientX, e.touches[0].clientY);
      }, { passive: true });

      window.addEventListener('touchmove', (e) => {
        if (e.touches && e.touches[0]) onMove(e.touches[0].clientX, e.touches[0].clientY);
      }, { passive: true });

      window.addEventListener('touchend', onEnd);
    })();
"""
    # Replace old parallax with the new 3D center swivel & hub wiring
    old_parallax_pat = r"\/\/ 3D iPhone Interactive Parallax & Swivel[\s\S]*?\}\)\(\);"
    html = re.sub(old_parallax_pat, wire_hub_js, html, count=1)

    # Write to webapp/index.html and index.html
    with open("webapp/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Successfully updated webapp/index.html and index.html with Liquid Glass, Radiant Top/Bottom Glow, and Centered 3D iPhone at 30 deg!")

if __name__ == "__main__":
    update()
