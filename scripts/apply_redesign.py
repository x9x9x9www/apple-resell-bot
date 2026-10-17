#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

def update_webapp():
    with open("webapp/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update Title & Meta
    html = re.sub(r"<title>.*?БРЕДЛИ ПЕРЕКУПЕР.*?</title>", "<title>БРЕДЛИ ПЕРЕКУПЕР | Apple Resell Pro</title>", html)
    html = re.sub(r'content="⚡️\s*БРЕДЛИ ПЕРЕКУПЕР"', 'content="БРЕДЛИ ПЕРЕКУПЕР | Apple Resell Pro"', html)

    # 2. Update CSS Variables in :root
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

      /* Apple Pro Titanium Silver & Monochrome Highlights (No Saturated Reds) */
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

    with open("webapp/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("CSS updated successfully")

if __name__ == "__main__":
    update_webapp()
