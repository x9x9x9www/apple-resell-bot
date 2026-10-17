#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os

def build_redesigned_webapp():
    # Always read from clean backup
    with open("webapp/index.html.bak", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update Title & Meta
    html = re.sub(r"<title>.*?БРЕДЛИ ПЕРЕКУПЕР.*?</title>", "<title>БРЕДЛИ ПЕРЕКУПЕР | Apple Resell Pro</title>", html)
    html = re.sub(r'content="⚡️\s*БРЕДЛИ ПЕРЕКУПЕР"', 'content="БРЕДЛИ ПЕРЕКУПЕР | Apple Resell Pro"', html)

    # 2. Update :root CSS Variables to Apple Space Black & Titanium
    old_root_pattern = r":root\s*\{[^}]*--bg-color:[^}]*\}"
    new_root = """:root {
      /* Apple Pro Matte Space Black & Pure Titanium Palette */
      --bg-color: #07080a;
      --bg-secondary: #0f1115;
      --card-bg: rgba(20, 22, 28, 0.65);
      --card-bg-elevated: rgba(28, 30, 38, 0.88);
      --card-border: rgba(255, 255, 255, 0.08);
      --card-border-hover: rgba(255, 255, 255, 0.22);
      --card-specular: inset 0 1px 0 rgba(255, 255, 255, 0.12), inset 0 0.5px 0.5px rgba(255, 255, 255, 0.25);

      /* Apple Pro Titanium Silver & Monochrome Highlights (Zero Saturated Reds) */
      --accent-color: #f5f5f7;
      --accent-highlight: #ffffff;
      --accent-glow: rgba(255, 255, 255, 0.16);
      --accent-subtle: rgba(255, 255, 255, 0.08);
      --accent-border: rgba(255, 255, 255, 0.16);
      --accent-gradient: linear-gradient(135deg, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0.06) 100%);
      --accent-gradient-hover: linear-gradient(135deg, rgba(255, 255, 255, 0.26) 0%, rgba(255, 255, 255, 0.12) 100%);

      /* Apple System Colors */
      --success-color: #30D158;
      --success-subtle: rgba(48, 209, 88, 0.14);
      --success-gradient: linear-gradient(135deg, #30D158 0%, #208738 100%);
      --danger-color: #FF453A;
      --danger-subtle: rgba(255, 69, 58, 0.14);
      --warning-color: #FF9F0A;
      --warning-subtle: rgba(255, 159, 10, 0.14);

      /* Typography & Neutral Shades */
      --text-main: #F5F5F7;
      --text-muted: #8E8E93;
      --text-tertiary: #545458;
      --tag-bg: rgba(255, 255, 255, 0.06);
      --font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', system-ui, sans-serif;

      /* Motion Design */
      --spring-bounce: cubic-bezier(0.175, 0.885, 0.32, 1.275);
      --spring-smooth: cubic-bezier(0.32, 0.72, 0, 1);
      --spring-press: cubic-bezier(0.2, 0, 0, 1);
      --spring-fluid: cubic-bezier(0.16, 1, 0.3, 1);
      --spring-morph: cubic-bezier(0.34, 1.56, 0.64, 1);
      --motion-fast: 150ms;
      --motion-normal: 260ms;
      --motion-slow: 420ms;
    }"""
    html = re.sub(old_root_pattern, new_root, html, count=1)

    # 3. Update Body style for Ambient Top & Bottom Glow
    old_body_pat = r"body\s*\{[^}]*background:[^}]*#050507;[^}]*\}"
    new_body = """body {
      background-color: #07080a;
      background-image:
        radial-gradient(ellipse 110% 48% at 50% -5%, rgba(255, 255, 255, 0.08) 0%, rgba(140, 160, 190, 0.035) 45%, transparent 75%),
        radial-gradient(ellipse 95% 42% at 50% 105%, rgba(150, 175, 210, 0.09) 0%, rgba(255, 255, 255, 0.02) 40%, transparent 75%);
      background-attachment: fixed;
      color: var(--text-main);
      font-family: var(--font-family);
      padding: 0 16px;
      padding-top: calc(14px + env(safe-area-inset-top, 0px));
      padding-bottom: calc(105px + env(safe-area-inset-bottom, 0px));
      min-height: 100vh;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }"""
    html = re.sub(old_body_pat, new_body, html, count=1)

    # 4. Inject 3D Hero and Glassmorphism CSS rules before </style>
    extra_css = """
    /* ========================================================
       APPLE TITANIUM LIQUID GLASS & 3D IPHONE SHOWCASE
       ======================================================== */
    .hero-3d-stage {
      position: relative;
      border-radius: 24px;
      padding: 18px 20px;
      margin-bottom: 16px;
      overflow: hidden;
      perspective: 1200px;
      background: linear-gradient(135deg, rgba(26, 29, 38, 0.75) 0%, rgba(14, 15, 20, 0.85) 100%) !important;
      backdrop-filter: blur(28px) saturate(190%) !important;
      -webkit-backdrop-filter: blur(28px) saturate(190%) !important;
      border: 1px solid rgba(255, 255, 255, 0.1) !important;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.16), 0 16px 40px rgba(0, 0, 0, 0.6) !important;
      transition: border-color 0.3s ease, box-shadow 0.3s ease;
      cursor: grab;
    }
    .hero-3d-stage:active {
      cursor: grabbing;
    }
    .hero-3d-stage:hover {
      border-color: rgba(255, 255, 255, 0.18) !important;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.22), 0 20px 48px rgba(0, 0, 0, 0.7) !important;
    }

    .hero-3d-ambient-glow {
      position: absolute;
      top: -60%;
      right: -20%;
      width: 140%;
      height: 220%;
      background: radial-gradient(circle at 65% 35%, rgba(255, 255, 255, 0.08) 0%, rgba(150, 175, 215, 0.04) 35%, transparent 70%);
      pointer-events: none;
      z-index: 1;
    }

    .hero-3d-content {
      position: relative;
      z-index: 2;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    .hero-3d-info {
      flex: 1;
      min-width: 0;
    }

    .hero-tag-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.08);
      border: 0.5px solid rgba(255, 255, 255, 0.14);
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.6px;
      color: #f5f5f7;
      text-transform: uppercase;
      margin-bottom: 8px;
    }

    .hero-tag-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #30d158;
      box-shadow: 0 0 8px #30d158;
      animation: pulseDot 2s infinite ease-in-out;
    }

    @keyframes pulseDot {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.4); opacity: 0.6; }
    }

    .hero-headline {
      font-size: 19px;
      font-weight: 800;
      line-height: 1.15;
      letter-spacing: -0.5px;
      color: #fff;
      margin-bottom: 5px;
    }

    .hero-headline-gradient {
      background: linear-gradient(135deg, #ffffff 0%, #c4c4c8 45%, #8e8e93 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .hero-subline {
      font-size: 11px;
      line-height: 1.4;
      color: var(--text-muted);
      margin-bottom: 12px;
    }

    .hero-stats-row {
      display: flex;
      gap: 8px;
    }

    .hero-stat-card {
      flex: 1;
      background: rgba(255, 255, 255, 0.05);
      border: 0.5px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 6px 6px;
      text-align: center;
      transition: background 0.2s ease;
    }
    .hero-stat-card:hover {
      background: rgba(255, 255, 255, 0.08);
    }

    .hero-stat-val {
      display: block;
      font-size: 12px;
      font-weight: 700;
      color: #ffffff;
    }

    .hero-stat-label {
      display: block;
      font-size: 9px;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.2px;
      margin-top: 2px;
    }

    .hero-3d-visual {
      position: relative;
      width: 140px;
      height: 140px;
      flex-shrink: 0;
      perspective: 1000px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .hero-3d-phone-container {
      position: relative;
      width: 132px;
      height: 132px;
      display: flex;
      align-items: center;
      justify-content: center;
      transform-style: preserve-3d;
      transform: rotateY(-14deg) rotateX(8deg) rotateZ(-2deg);
      transition: transform 0.65s cubic-bezier(0.16, 1, 0.3, 1);
      will-change: transform;
    }

    .hero-3d-phone-img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      filter: drop-shadow(0 14px 28px rgba(0, 0, 0, 0.75));
      user-select: none;
      -webkit-user-drag: none;
      pointer-events: none;
    }

    .hero-3d-shadow {
      position: absolute;
      bottom: -4px;
      left: 10%;
      width: 80%;
      height: 16px;
      background: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.85) 0%, transparent 75%);
      filter: blur(4px);
      pointer-events: none;
      z-index: 1;
    }

    /* SVG Icons General Styling */
    .svg-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      vertical-align: middle;
      flex-shrink: 0;
    }
    .svg-icon svg {
      width: 100%;
      height: 100%;
    }

    /* Glassmorphism Refinements across UI */
    .ios-inset-card,
    .model-card,
    .kpi-card,
    .deals-section,
    .search-wrapper,
    .master-bot-bar,
    .save-bar,
    .ios-tab-bar,
    .modal-sheet {
      background: rgba(18, 20, 26, 0.65) !important;
      backdrop-filter: blur(28px) saturate(190%) !important;
      -webkit-backdrop-filter: blur(28px) saturate(190%) !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12), 0 12px 32px rgba(0, 0, 0, 0.45) !important;
    }

    .model-card:hover {
      border-color: rgba(255, 255, 255, 0.18) !important;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.16), 0 16px 40px rgba(0, 0, 0, 0.55) !important;
    }

    .btn-save, .btn-add-model, .btn-add-deal {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0.08) 100%) !important;
      border: 1px solid rgba(255, 255, 255, 0.16) !important;
      color: #fff !important;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    }
    .btn-save:hover, .btn-add-model:hover, .btn-add-deal:hover {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.24) 0%, rgba(255, 255, 255, 0.12) 100%) !important;
      border-color: rgba(255, 255, 255, 0.25) !important;
    }

    /* Active Tab Bar Pill in Titanium Style */
    .tab-item.active {
      color: #ffffff !important;
      background: rgba(255, 255, 255, 0.12) !important;
      border: 1px solid rgba(255, 255, 255, 0.18) !important;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25), 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    }
    .tab-item.active .tab-label {
      color: #ffffff !important;
      text-shadow: 0 0 12px rgba(255, 255, 255, 0.3) !important;
    }
    .tab-item.active .tab-icon {
      color: #ffffff !important;
      filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.4));
    }
    """
    html = html.replace("</style>", extra_css + "\n</style>", 1)

    # 5. HTML Header Markup
    old_catalog_header = """      <div class="ios-large-title-row">
        <h1 class="ios-large-title">
          <span>⚡️</span>
          <span>БРЕДЛИ ПЕРЕКУПЕР</span>
        </h1>
        <div class="header-actions">
          <button type="button" class="btn-region-badge" id="btnOpenRegionModal" title="Сменить регион поиска">
            📍 <span id="headerRegionName">Москва</span>
          </button>
          <button class="btn-add-model" id="btnOpenAddModal">
            <span>➕ Модель</span>
          </button>
        </div>
      </div>"""

    new_catalog_header = """      <div class="ios-large-title-row">
        <h1 class="ios-large-title">
          <span class="svg-icon" style="color: #fff; width: 18px; height: 18px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          </span>
          <span>БРЕДЛИ ПЕРЕКУПЕР</span>
        </h1>
        <div class="header-actions">
          <button type="button" class="btn-region-badge" id="btnOpenRegionModal" title="Сменить регион поиска">
            <span class="svg-icon" style="width: 13px; height: 13px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg></span>
            <span id="headerRegionName">Москва</span>
          </button>
          <button class="btn-add-model" id="btnOpenAddModal">
            <span class="svg-icon" style="width: 13px; height: 13px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"/><path d="M12 5v14"/></svg></span>
            <span>Модель</span>
          </button>
        </div>
      </div>"""
    html = html.replace(old_catalog_header, new_catalog_header)

    html = html.replace('<span class="master-bot-text" id="masterBotText">🟢 Поиск активен</span>', '<span class="master-bot-text" id="masterBotText">Поиск активен</span>')

    # 6. Insert 3D Hero Stage
    hero_stage_html = """
    <!-- ==================== 3D IPHONE SHOWCASE HERO ==================== -->
    <div class="hero-3d-stage" id="hero3dStage" title="Потяните для 3D вращения">
      <div class="hero-3d-ambient-glow"></div>
      <div class="hero-3d-content">
        <div class="hero-3d-info">
          <div class="hero-tag-pill">
            <span class="hero-tag-dot"></span>
            <span>APPLE RESELL PRO</span>
          </div>
          <h2 class="hero-headline">Мониторинг <br><span class="hero-headline-gradient">техники Apple</span></h2>
          <p class="hero-subline">Аналитика цен и моментальный выкуп с Авито и Юлы</p>
          <div class="hero-stats-row">
            <div class="hero-stat-card">
              <span class="hero-stat-val" id="heroStatModels">0</span>
              <span class="hero-stat-label">Моделей</span>
            </div>
            <div class="hero-stat-card">
              <span class="hero-stat-val" id="heroStatRegion">Москва</span>
              <span class="hero-stat-label">Регион</span>
            </div>
            <div class="hero-stat-card">
              <span class="hero-stat-val" id="heroStatStatus" style="color: #30d158;">В сети</span>
              <span class="hero-stat-label">Статус</span>
            </div>
          </div>
        </div>
        <div class="hero-3d-visual" id="hero3dVisual">
          <div class="hero-3d-phone-container" id="hero3dPhoneContainer">
            <img src="./iphone_3d.png" alt="3D iPhone Titanium" class="hero-3d-phone-img" id="hero3dPhoneImg">
          </div>
          <div class="hero-3d-shadow"></div>
        </div>
      </div>
    </div>
    """
    html = html.replace('<!-- Поиск -->\n    <div class="search-wrapper">', hero_stage_html + '\n    <!-- Поиск -->\n    <div class="search-wrapper">')

    # Search icon replacement: 🔍 -> SVG
    search_svg = '<span class="search-icon svg-icon" style="width: 15px; height: 15px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg></span>'
    html = re.sub(r'<span class="search-icon">🔍</span>', search_svg, html)

    # 7. Analytics View Header & Buttons
    old_analytics_header = """        <h1 class="ios-large-title">
          <span>📊</span>
          <span>АНАЛИТИКА</span>
        </h1>
        <div class="header-actions">
          <button class="btn-add-deal" id="btnOpenAddDealModal">
            <span>➕ Сделка</span>
          </button>
        </div>"""
    new_analytics_header = """        <h1 class="ios-large-title">
          <span class="svg-icon" style="width: 18px; height: 18px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg></span>
          <span>АНАЛИТИКА</span>
        </h1>
        <div class="header-actions">
          <button class="btn-add-deal" id="btnOpenAddDealModal">
            <span class="svg-icon" style="width: 13px; height: 13px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"/><path d="M12 5v14"/></svg></span>
            <span>Сделка</span>
          </button>
        </div>"""
    html = html.replace(old_analytics_header, new_analytics_header)

    html = html.replace('🔄 Демо', '<span class="svg-icon" style="width: 12px; height: 12px; margin-right: 4px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg></span> Демо')
    html = html.replace('<span>📝 Недавние продажи</span>', '<span style="display:flex; align-items:center; gap:6px;"><span class="svg-icon" style="width: 14px; height: 14px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg></span><span>Недавние продажи</span></span>')
    html = html.replace('➕ Записать', '<span class="svg-icon" style="width: 11px; height: 11px; margin-right: 3px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"/><path d="M12 5v14"/></svg></span> Записать')

    # 8. Settings View
    old_settings_header = """        <h1 class="ios-large-title">
          <span>⚙️</span>
          <span>НАСТРОЙКИ</span>
        </h1>"""
    new_settings_header = """        <h1 class="ios-large-title">
          <span class="svg-icon" style="width: 18px; height: 18px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg></span>
          <span>НАСТРОЙКИ</span>
        </h1>"""
    html = html.replace(old_settings_header, new_settings_header)

    # Badges in settings
    html = html.replace('<div class="ios-icon-badge" style="background: rgba(4, 194, 127, 0.15); color: #04c27f;">🟢</div>', '<div class="ios-icon-badge" style="background: rgba(255, 255, 255, 0.08); color: #30d158;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" x2="22" y1="12" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg></div>')
    html = html.replace('<div class="ios-icon-badge" style="background: rgba(186, 104, 200, 0.15); color: #ba68c8;">🟣</div>', '<div class="ios-icon-badge" style="background: rgba(255, 255, 255, 0.08); color: #bf5af2;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/></svg></div>')
    html = html.replace('<div class="ios-icon-badge" style="background: rgba(255, 59, 48, 0.15); color: #ff3b30;">🔄</div>', '<div class="ios-icon-badge" style="background: rgba(255, 69, 58, 0.14); color: #ff453a;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg></div>')
    html = html.replace('<div class="ios-icon-badge" style="background: rgba(255, 149, 0, 0.15); color: #ff9500;">📍</div>', '<div class="ios-icon-badge" style="background: rgba(255, 255, 255, 0.08); color: #ff9f0a;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg></div>')
    html = html.replace('<div class="ios-icon-badge" style="background: rgba(52, 199, 89, 0.15); color: #34c759;">🔋</div>', '<div class="ios-icon-badge" style="background: rgba(48, 209, 88, 0.14); color: #30d158;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="16" height="10" x="2" y="7" rx="2" ry="2"/><line x1="22" x2="22" y1="11" y2="13"/></svg></div>')
    html = html.replace('<div class="ios-icon-badge" style="background: rgba(255, 214, 10, 0.15); color: #ffd60a;">💸</div>', '<div class="ios-icon-badge" style="background: rgba(255, 214, 10, 0.14); color: #ffd60a;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" x2="5" y1="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg></div>')
    html = html.replace('<div class="ios-icon-badge" style="background: rgba(175, 82, 222, 0.15); color: #af52de;">👤</div>', '<div class="ios-icon-badge" style="background: rgba(191, 90, 242, 0.14); color: #bf5af2;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M9 9h.01"/><path d="M15 9h.01"/><path d="M10 13a2 2 0 0 0 4 0"/><path d="M8 17a5 5 0 0 0 8 0"/></svg></div>')
    html = html.replace('<div class="ios-icon-badge" style="background: rgba(255, 69, 58, 0.15); color: #ff453a;">🔒</div>', '<div class="ios-icon-badge" style="background: rgba(255, 69, 58, 0.14); color: #ff453a;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>')

    html = html.replace('<span>💾 Применить настройки в бота</span>', '<span style="display:inline-flex; align-items:center; gap:6px;"><span class="svg-icon" style="width:15px; height:15px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg></span><span>Применить настройки</span></span>')

    # 9. Save Bar
    html = html.replace('<span>💾 Применить в бота</span>', '<span style="display:inline-flex; align-items:center; gap:6px;"><span class="svg-icon" style="width:15px; height:15px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg></span><span>Применить в бота</span></span>')

    # 10. Bottom Navigation Tab Bar (SVG Icons instead of emojis)
    old_tab_bar = """  <!-- iOS Bottom Navigation Tab Bar -->
  <nav class="ios-tab-bar" id="iosTabBar">
    <button type="button" class="tab-item active" id="tabCatalog" data-tab="catalog">
      <span class="tab-icon">🏷️</span>
      <span class="tab-label">Прайс-лист</span>
    </button>
    <button type="button" class="tab-item" id="tabAnalytics" data-tab="analytics">
      <span class="tab-icon">📊</span>
      <span class="tab-label">Аналитика</span>
    </button>
    <button type="button" class="tab-item" id="tabSettings" data-tab="settings">
      <span class="tab-icon">⚙️</span>
      <span class="tab-label">Настройки</span>
    </button>
  </nav>"""

    new_tab_bar = """  <!-- iOS Bottom Navigation Tab Bar (Liquid Titanium Glass) -->
  <nav class="ios-tab-bar" id="iosTabBar">
    <button type="button" class="tab-item active" id="tabCatalog" data-tab="catalog">
      <span class="tab-icon svg-icon" style="width: 20px; height: 20px;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"/><circle cx="7" cy="7" r=".5" fill="currentColor"/></svg>
      </span>
      <span class="tab-label">Прайс-лист</span>
    </button>
    <button type="button" class="tab-item" id="tabAnalytics" data-tab="analytics">
      <span class="tab-icon svg-icon" style="width: 20px; height: 20px;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
      </span>
      <span class="tab-label">Аналитика</span>
    </button>
    <button type="button" class="tab-item" id="tabSettings" data-tab="settings">
      <span class="tab-icon svg-icon" style="width: 20px; height: 20px;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
      </span>
      <span class="tab-label">Настройки</span>
    </button>
  </nav>"""
    html = html.replace(old_tab_bar, new_tab_bar)

    # 11. Modals: clean SVG headers and buttons
    html = html.replace('<h3 class="modal-title">💰 Записать сделку</h3>', '<h3 class="modal-title"><span class="svg-icon" style="width:16px; height:16px; margin-right:6px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg></span>Записать сделку</h3>')
    html = html.replace('<h3 class="modal-title">📍 Регион поиска лотов</h3>', '<h3 class="modal-title"><span class="svg-icon" style="width:16px; height:16px; margin-right:6px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg></span>Регион поиска лотов</h3>')
    html = html.replace('🔥 Популярные регионы', 'Популярные регионы')
    html = html.replace('<h3 class="modal-title">📁 Добавить папку / Бренд</h3>', '<h3 class="modal-title"><span class="svg-icon" style="width:16px; height:16px; margin-right:6px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg></span>Добавить папку / Бренд</h3>')
    html = html.replace('⚡️ Готовые категории (добавить в 1 клик):', 'Готовые категории (добавить в 1 клик):')
    html = html.replace('🔗 Ссылка на поиск для всей папки (опционально):', 'Ссылка на поиск для всей папки (опционально):')
    html = html.replace('💡 Бот будет отслеживать поток объявлений по этой точной ссылке.', 'Бот будет отслеживать поток объявлений по этой точной ссылке.')
    html = html.replace('<span>✅ Создать свою папку</span>', '<span>Создать свою папку</span>')
    html = html.replace('<h3 class="modal-title" id="presetModalTitle">⚡️ Добавление папки</h3>', '<h3 class="modal-title" id="presetModalTitle">Добавление папки</h3>')
    html = html.replace('<span id="btnConfirmPresetLabel">✅ Добавить выбранные модели</span>', '<span id="btnConfirmPresetLabel">Добавить выбранные модели</span>')
    html = html.replace('📁 Создать только пустую папку', 'Создать только пустую папку')
    html = html.replace('<h3 class="modal-title">⚙️ Управление папкой</h3>', '<h3 class="modal-title">Управление папкой</h3>')
    html = html.replace('⚡️ Добавить популярные модели бренда...', 'Добавить популярные модели бренда...')
    html = html.replace('<span>💾 Сохранить изменения</span>', '<span>Сохранить изменения</span>')
    html = html.replace('🗑 Удалить / скрыть папку', 'Удалить / скрыть папку')
    html = html.replace('<h3 class="modal-title">➕ Добавить модель</h3>', '<h3 class="modal-title">Добавить модель</h3>')
    html = html.replace('<h3 class="modal-title">⚙️ Управление каталогом</h3>', '<h3 class="modal-title">Управление каталогом</h3>')

    close_svg = '<span class="svg-icon" style="width: 12px; height: 12px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></span>'
    html = re.sub(r'<button class="btn-close-modal"([^>]*)>✕</button>', f'<button class="btn-close-modal"\\1>{close_svg}</button>', html)
    html = html.replace('>✕ Закрыть</button>', f'>{close_svg} Закрыть</button>')
    html = html.replace('<span>✅ Сохранить сделку</span>', '<span>Сохранить сделку</span>')

    # Category chips in Add Folder & Manage Folder Modals
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

    # Clean dropdown options
    html = html.replace('<option value="iphone">📱 iPhone</option>', '<option value="iphone">iPhone</option>')
    html = html.replace('<option value="macbook">💻 Mac</option>', '<option value="macbook">Mac</option>')
    html = html.replace('<option value="samsung">📱 Samsung</option>', '<option value="samsung">Samsung</option>')
    html = html.replace('<option value="pixel">📱 Pixel</option>', '<option value="pixel">Pixel</option>')
    html = html.replace('<option value="ipad">📟 iPad</option>', '<option value="ipad">iPad</option>')
    html = html.replace('<option value="consoles">🎮 Консоли</option>', '<option value="consoles">Консоли</option>')
    html = html.replace('<option value="__new__">➕ Создать новую папку...</option>', '<option value="__new__">Создать новую папку...</option>')

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

    html = re.sub(r'<div class="dynamic-toast-icon" id="dynamicToastIcon">.*?</div>',
                  '<div class="dynamic-toast-icon svg-icon" id="dynamicToastIcon" style="width:16px; height:16px; color:#fff;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg></div>',
                  html)

    # 12. JavaScript Updates: find main application <script> (not the telegram script)
    main_script_pattern = r"(<script>\s*\(function\s*\(\)\s*\{)"
    svg_icons_js = """<script>
    // Apple SF Symbol Style SVG Icons Library (No Emojis)
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
      watch: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="7"/><polyline points="12 9 12 12 13.5 13.5"/><path d="M16.51 17.35l-.35 3.83a2 2 0 0 1-2 1.82H9.83a2 2 0 0 1-2-1.82l-.35-3.83m.01-10.7.35-3.83A2 2 0 0 1 9.83 1h4.34a2 2 0 0 1 2 1.82l.35 3.83"/></svg>`,
      battery: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="10" x="2" y="7" rx="2" ry="2"/><line x1="22" x2="22" y1="11" y2="13"/></svg>`,
      discount: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" x2="5" y1="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>`,
      faceId: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M9 9h.01"/><path d="M15 9h.01"/><path d="M10 13a2 2 0 0 0 4 0"/><path d="M8 17a5 5 0 0 0 8 0"/></svg>`,
      shieldLock: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
      wallet: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg>`,
      trendingUp: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>`,
      deals: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg>`,
      spark: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/></svg>`,
      bolt: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`,
      globe: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" x2="22" y1="12" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>`,
      chevronRight: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>`
    };
    (function () {
    """
    html = re.sub(main_script_pattern, svg_icons_js, html, count=1)

    # 13. JS Helpers: getCategoryIconSvg & getDeviceIcon
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
    old_device_icon_pattern = r"function getDeviceIcon\(name, series\)\s*\{[^}]*return '📱';\s*\}"
    html = re.sub(old_device_icon_pattern, icon_helpers_js, html, count=1)

    # 14. In renderSeriesBar:
    html = html.replace("titleSpan.textContent = `${cat.icon || '📁'} ${cat.name}`;",
                        "titleSpan.innerHTML = `<span class=\"svg-icon\" style=\"width:13px; height:13px; margin-right:4px; opacity:0.85;\">${getCategoryIconSvg(cat.icon)}</span>${escapeHtml(cat.name)}`;")
    html = html.replace("editBtn.textContent = '✏️';", "editBtn.innerHTML = AppIcons.edit;")
    html = html.replace("addBtn.innerHTML = '<span>➕ Папка</span>';", "addBtn.innerHTML = `<span class=\"svg-icon\" style=\"width:11px; height:11px; margin-right:3px;\">${AppIcons.plus}</span><span>Папка</span>`;")
    html = html.replace("btnToggle.innerHTML = '⏸ Выкл. всё';", "btnToggle.innerHTML = 'Выкл. всё';")
    html = html.replace("btnToggle.innerHTML = '▶️ Вкл. всё';", "btnToggle.innerHTML = 'Вкл. всё';")

    # 15. In renderCards:
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

    # 16. In KPI Cards:
    html = html.replace('<div class="kpi-icon-badge">💰</div>', '<div class="kpi-icon-badge" style="background:rgba(255,255,255,0.08); color:#f5f5f7;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/></svg></div>')
    html = html.replace('<div class="kpi-icon-badge">📱</div>', '<div class="kpi-icon-badge" style="background:rgba(255,255,255,0.08); color:#f5f5f7;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg></div>')
    html = html.replace('<div class="kpi-icon-badge">🎯</div>', '<div class="kpi-icon-badge" style="background:rgba(255,255,255,0.08); color:#f5f5f7;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg></div>')
    html = html.replace('<p style="font-size: 28px; margin-bottom: 6px;">📭</p>', '<div class="svg-icon" style="width: 32px; height: 32px; margin: 0 auto 8px; color: var(--text-tertiary);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg></div>')

    # Deals items
    html = html.replace('<span>📱 ${d.model}</span>', '<span>${d.model}</span>')
    html = html.replace('<span>📅 ${dDate}</span>', '<span>${dDate}</span>')
    html = html.replace('<span>• 💬 ${d.note}</span>', '<span>• ${d.note}</span>')
    html = html.replace('➔', '→')
    html = html.replace('<button type="button" class="btn-delete-deal" data-id="${d.id}" title="Удалить сделку">✕</button>',
                        '<button type="button" class="btn-delete-deal" data-id="${d.id}" title="Удалить сделку"><span class="svg-icon" style="width:11px; height:11px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></span></button>')

    # Templates Grid
    html = html.replace("chip.innerHTML = `${tpl.icon} <span>${tpl.name}</span>${isAdded ? ' ✓' : ' ➕'}`;",
                        "chip.innerHTML = `<span class=\"svg-icon\" style=\"width:13px; height:13px; margin-right:4px;\">${getCategoryIconSvg(tpl.icon)}</span> <span>${tpl.name}</span>${isAdded ? ' ✓' : ''}`;")
    html = html.replace("document.getElementById('presetModalTitle').textContent = `${tpl.icon} Добавить: ${tpl.name}`;",
                        "document.getElementById('presetModalTitle').innerHTML = `<span class=\"svg-icon\" style=\"width:16px; height:16px; margin-right:6px;\">${getCategoryIconSvg(tpl.icon)}</span>Добавить: ${tpl.name}`;")

    # 17. 3D iPhone Dynamic Orientation based on switchAppTab
    old_switch_tab = """      if (tab === 'catalog') {
        if (catalogView) {
          catalogView.style.display = 'block';
          triggerKeynoteEntrance(catalogView);
        }
        if (saveBar) saveBar.style.display = 'flex';
        tabCatalog?.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else if (tab === 'analytics') {
        if (analyticsView) {
          analyticsView.style.display = 'block';
          triggerKeynoteEntrance(analyticsView);
        }
        tabAnalytics?.classList.add('active');
        renderAnalyticsDashboard();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else if (tab === 'settings') {
        if (settingsView) {
          settingsView.style.display = 'block';
          triggerKeynoteEntrance(settingsView);
        }
        tabSettings?.classList.add('active');
        syncSettingsTabUI();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }"""

    new_switch_tab = """      // 3D iPhone Dynamic Orientation based on Active Tab
      const phone3d = document.getElementById('hero3dPhoneContainer');
      function update3DHeroOrientation(tabName) {
        if (!phone3d) return;
        if (tabName === 'catalog') {
          phone3d.style.transform = 'rotateY(-14deg) rotateX(8deg) rotateZ(-2deg) scale(1)';
        } else if (tabName === 'analytics') {
          phone3d.style.transform = 'rotateY(24deg) rotateX(10deg) rotateZ(3deg) scale(0.96)';
        } else if (tabName === 'settings') {
          phone3d.style.transform = 'rotateY(-24deg) rotateX(-8deg) rotateZ(-3deg) scale(0.96)';
        }
      }
      update3DHeroOrientation(tab);

      // Update 3D Hero Metrics
      try {
        const heroStatModels = document.getElementById('heroStatModels');
        const heroStatRegion = document.getElementById('heroStatRegion');
        const heroStatStatus = document.getElementById('heroStatStatus');
        const activeModels = Object.values(priceMatrix || {}).filter(m => m.active !== false).length;
        if (heroStatModels) heroStatModels.textContent = activeModels || '0';
        if (heroStatRegion) heroStatRegion.textContent = selectedRegion || 'Москва';
        const isMasterActive = document.getElementById('toggleGlobalSearch')?.checked;
        if (heroStatStatus) {
          heroStatStatus.textContent = isMasterActive ? 'В сети' : 'Пауза';
          heroStatStatus.style.color = isMasterActive ? '#30d158' : '#8e8e93';
        }
      } catch (e) {}

      if (tab === 'catalog') {
        if (catalogView) {
          catalogView.style.display = 'block';
          triggerKeynoteEntrance(catalogView);
        }
        if (saveBar) saveBar.style.display = 'flex';
        tabCatalog?.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else if (tab === 'analytics') {
        if (analyticsView) {
          analyticsView.style.display = 'block';
          triggerKeynoteEntrance(analyticsView);
        }
        tabAnalytics?.classList.add('active');
        renderAnalyticsDashboard();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else if (tab === 'settings') {
        if (settingsView) {
          settingsView.style.display = 'block';
          triggerKeynoteEntrance(settingsView);
        }
        tabSettings?.classList.add('active');
        syncSettingsTabUI();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }"""
    html = html.replace(old_switch_tab, new_switch_tab)

    # 18. Append Parallax & Swivel Interactivity at the very END of the file (before </body>)
    parallax_js = """
    // 3D iPhone Interactive Parallax & Swivel
    (function init3DHeroParallax() {
      const stage = document.getElementById('hero3dStage');
      const phone = document.getElementById('hero3dPhoneContainer');
      if (!stage || !phone) return;

      function handleMove(clientX, clientY) {
        const rect = stage.getBoundingClientRect();
        const x = (clientX - rect.left) / rect.width - 0.5; // -0.5 to 0.5
        const y = (clientY - rect.top) / rect.height - 0.5;

        const rotY = -14 + (x * 40); // Base -14deg +/- 20deg
        const rotX = 8 - (y * 30);   // Base 8deg +/- 15deg
        phone.style.transform = `rotateY(${rotY.toFixed(1)}deg) rotateX(${rotX.toFixed(1)}deg) rotateZ(${(x * -4).toFixed(1)}deg) scale(1.04)`;
      }

      stage.addEventListener('mousemove', (e) => {
        handleMove(e.clientX, e.clientY);
      });

      stage.addEventListener('mouseleave', () => {
        const activeTab = currentAppTab || 'catalog';
        if (activeTab === 'catalog') {
          phone.style.transform = 'rotateY(-14deg) rotateX(8deg) rotateZ(-2deg) scale(1)';
        } else if (activeTab === 'analytics') {
          phone.style.transform = 'rotateY(24deg) rotateX(10deg) rotateZ(3deg) scale(0.96)';
        } else {
          phone.style.transform = 'rotateY(-24deg) rotateX(-8deg) rotateZ(-3deg) scale(0.96)';
        }
      });

      stage.addEventListener('touchmove', (e) => {
        if (e.touches && e.touches[0]) {
          handleMove(e.touches[0].clientX, e.touches[0].clientY);
        }
      }, { passive: true });

      stage.addEventListener('touchend', () => {
        phone.style.transform = 'rotateY(-14deg) rotateX(8deg) rotateZ(-2deg) scale(1)';
      });
    })();
  </script>
</body>
"""
    # Replace the closing </script>\n</body>
    html = re.sub(r"<\/script>\s*<\/body>", parallax_js, html, count=1)

    # Write to webapp/index.html
    with open("webapp/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    # Also keep root index.html synchronized!
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Master redesign applied cleanly to both webapp/index.html and index.html!")

if __name__ == "__main__":
    build_redesigned_webapp()
