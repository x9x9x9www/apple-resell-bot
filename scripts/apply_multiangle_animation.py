#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

def update_multiangle_animation():
    with open("webapp/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Replace the iphone-3d-scene with the multi-angle 3D animation viewport
    old_scene_pattern = r'<div class="iphone-3d-scene" id="iphone3dScene"[\s\S]*?<!-- 3D Ground Shadow -->[\s\S]*?<\/div>[\s\S]*?<\/div>'
    
    new_scene_markup = """<div class="iphone-multiangle-stage" id="iphoneMultiStage" title="Проведите пальцем для смены ракурса">
        <div class="iphone-angle-layers" id="iphoneAngleLayers">
          <img src="./assets/angles/angle_a_45.png" class="angle-frame active" id="angleA" data-angle="a" alt="iPhone 45° Экран">
          <img src="./assets/angles/angle_b_30.png" class="angle-frame" id="angleB" data-angle="b" alt="iPhone 30° Задняя панель">
          <img src="./assets/angles/angle_c_60.png" class="angle-frame" id="angleC" data-angle="c" alt="iPhone 60° Грани">
          <img src="./assets/angles/angle_d_15.png" class="angle-frame" id="angleD" data-angle="d" alt="iPhone 15° Кинематографичный">
        </div>
        <!-- Liquid Glass Specular Shine across phone -->
        <div class="iphone-dynamic-sheen" id="iphoneDynamicSheen"></div>
        <!-- 3D Ground Shadow that morphs with angle -->
        <div class="iphone-dynamic-shadow" id="iphoneDynamicShadow"></div>
      </div>

      <!-- Quick Angle Indicator Pills (Interactive 360 Selector) -->
      <div class="angle-picker-pills" id="anglePickerPills">
        <button type="button" class="angle-pill active" data-target="a" title="Ракурс А: 45° Экран">45° Экран</button>
        <button type="button" class="angle-pill" data-target="b" title="Ракурс Б: 30° Титан">30° Титан</button>
        <button type="button" class="angle-pill" data-target="c" title="Ракурс В: 60° Грани">60° Грани</button>
        <button type="button" class="angle-pill" data-target="d" title="Ракурс Г: 15° Студия">15° Студия</button>
      </div>"""

    html = re.sub(old_scene_pattern, new_scene_markup, html, count=1)

    # 2. Add Multi-angle CSS styles before </style>
    multi_css = """
    /* ========================================================
       MULTI-ANGLE 3D IPHONE ANIMATION SYSTEM (APPLE KEYNOTE)
       ======================================================== */
    .iphone-multiangle-stage {
      position: relative;
      width: 250px;
      height: 270px;
      perspective: 1200px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 4px auto 10px;
      cursor: grab;
      touch-action: pan-y;
      z-index: 2;
    }
    .iphone-multiangle-stage:active {
      cursor: grabbing;
    }

    .iphone-angle-layers {
      position: relative;
      width: 230px;
      height: 250px;
      display: flex;
      align-items: center;
      justify-content: center;
      transform-style: preserve-3d;
      transition: transform 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .angle-frame {
      position: absolute;
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      opacity: 0;
      transform: scale(0.92) translateZ(-15px) rotateY(-5deg);
      filter: drop-shadow(0 14px 28px rgba(0, 0, 0, 0.85));
      transition: opacity 0.42s cubic-bezier(0.16, 1, 0.3, 1), transform 0.45s cubic-bezier(0.16, 1, 0.3, 1);
      pointer-events: none;
      user-select: none;
      -webkit-user-drag: none;
    }

    .angle-frame.active {
      opacity: 1;
      transform: scale(1) translateZ(0px) rotateY(0deg);
      filter: drop-shadow(0 22px 42px rgba(0, 0, 0, 0.95));
    }

    .iphone-dynamic-sheen {
      position: absolute;
      top: -10%;
      left: -20%;
      width: 140%;
      height: 120%;
      border-radius: 36px;
      background: linear-gradient(130deg, transparent 35%, rgba(255, 255, 255, 0.35) 48%, transparent 62%);
      pointer-events: none;
      opacity: 0;
      transform: translateX(-60px);
      transition: opacity 0.25s ease, transform 0.5s ease;
      mix-blend-mode: overlay;
      z-index: 3;
    }
    .iphone-dynamic-sheen.flash {
      opacity: 1;
      transform: translateX(60px);
    }

    .iphone-dynamic-shadow {
      position: absolute;
      bottom: -10px;
      left: 10%;
      width: 80%;
      height: 24px;
      background: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.92) 0%, rgba(0, 0, 0, 0.4) 45%, transparent 75%);
      filter: blur(8px);
      pointer-events: none;
      z-index: 1;
      transition: all 0.45s ease;
    }

    /* Angle Picker Pills (Interactive Multi-Angle Switcher) */
    .angle-picker-pills {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 4px 6px;
      border-radius: 9999px;
      background: rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(24px) saturate(190%);
      -webkit-backdrop-filter: blur(24px) saturate(190%);
      border: 1.2px solid rgba(255, 255, 255, 0.32);
      box-shadow:
        inset 0 1.5px 2px rgba(255, 255, 255, 0.7),
        inset 0 -1.5px 2px rgba(0, 0, 0, 0.4),
        0 8px 20px rgba(0, 0, 0, 0.5);
      margin-bottom: 14px;
      z-index: 2;
    }

    .angle-pill {
      padding: 4px 10px;
      border-radius: 9999px;
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: -0.1px;
      cursor: pointer;
      user-select: none;
      transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .angle-pill:active {
      transform: scale(0.94);
    }

    .angle-pill.active {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.35) 0%, rgba(255, 255, 255, 0.12) 100%);
      border-color: rgba(255, 255, 255, 0.65);
      color: #ffffff;
      box-shadow:
        inset 0 1.5px 2px rgba(255, 255, 255, 0.9),
        0 4px 12px rgba(0, 0, 0, 0.4),
        0 0 16px rgba(200, 230, 255, 0.28);
    }
    """
    html = html.replace("</style>", multi_css + "\n</style>", 1)

    # 3. Update JavaScript logic for angle switching and swipe/drag controls
    multi_js = """
    // Multi-Angle 3D iPhone Keynote Animation Controller
    let currentIphoneAngle = 'a';
    const angleOrder = ['a', 'b', 'c', 'd'];

    function setIphoneAngle(targetAngle) {
      if (!targetAngle || currentIphoneAngle === targetAngle) return;
      currentIphoneAngle = targetAngle;

      const frames = {
        a: document.getElementById('angleA'),
        b: document.getElementById('angleB'),
        c: document.getElementById('angleC'),
        d: document.getElementById('angleD'),
      };

      Object.keys(frames).forEach(k => {
        if (frames[k]) {
          frames[k].classList.toggle('active', k === targetAngle);
        }
      });

      // Update Angle Pills
      document.querySelectorAll('.angle-pill').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.target === targetAngle);
      });

      // Trigger specular light flash
      const sheen = document.getElementById('iphoneDynamicSheen');
      if (sheen) {
        sheen.classList.remove('flash');
        void sheen.offsetWidth;
        sheen.classList.add('flash');
      }

      // Dynamic shadow adjustments
      const shadow = document.getElementById('iphoneDynamicShadow');
      if (shadow) {
        if (targetAngle === 'd') {
          shadow.style.width = '95%';
          shadow.style.height = '18px';
          shadow.style.bottom = '-4px';
        } else if (targetAngle === 'c') {
          shadow.style.width = '65%';
          shadow.style.height = '24px';
          shadow.style.bottom = '-10px';
        } else {
          shadow.style.width = '80%';
          shadow.style.height = '24px';
          shadow.style.bottom = '-10px';
        }
      }

      if (tg?.HapticFeedback) tg.HapticFeedback.selectionChanged();
    }

    // Wire Angle Picker Buttons
    document.querySelectorAll('.angle-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.dataset.target;
        if (target) setIphoneAngle(target);
      });
    });

    // Sync angle with Tab switching
    function syncAngleWithAppTab(tab) {
      if (tab === 'catalog') {
        setIphoneAngle('a'); // 45° Экран
      } else if (tab === 'analytics') {
        setIphoneAngle('b'); // 30° Титан
      } else if (tab === 'settings') {
        setIphoneAngle('c'); // 60° Грани
      }
    }

    // Wire Swipe / Drag Gesture across the 3D stage
    (function initMultiAngleDrag() {
      const stage = document.getElementById('iphoneMultiStage');
      if (!stage) return;

      let startX = 0;
      let isDragging = false;

      function onStart(x) {
        startX = x;
        isDragging = true;
      }

      function onEnd(endX) {
        if (!isDragging) return;
        isDragging = false;
        const diffX = endX - startX;
        if (Math.abs(diffX) > 35) {
          const currentIdx = angleOrder.indexOf(currentIphoneAngle);
          if (diffX < 0) {
            // swipe left -> next angle
            const nextIdx = (currentIdx + 1) % angleOrder.length;
            setIphoneAngle(angleOrder[nextIdx]);
          } else {
            // swipe right -> prev angle
            const prevIdx = (currentIdx - 1 + angleOrder.length) % angleOrder.length;
            setIphoneAngle(angleOrder[prevIdx]);
          }
        }
      }

      stage.addEventListener('mousedown', (e) => onStart(e.clientX));
      window.addEventListener('mouseup', (e) => onEnd(e.clientX));

      stage.addEventListener('touchstart', (e) => {
        if (e.touches && e.touches[0]) onStart(e.touches[0].clientX);
      }, { passive: true });

      stage.addEventListener('touchend', (e) => {
        if (e.changedTouches && e.changedTouches[0]) onEnd(e.changedTouches[0].clientX);
      });
    })();
    """

    # Replace the previous update3DHeroOrientation call in switchAppTab
    html = re.sub(
        r"update3DHeroOrientation\(tab\);",
        "update3DHeroOrientation(tab);\n      syncAngleWithAppTab(tab);",
        html,
        count=1
    )

    # Insert multi-angle controller before </body>
    html = html.replace("</script>\n</body>", multi_js + "\n</script>\n</body>")

    with open("webapp/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Multi-angle animation system successfully implemented in webapp/index.html and index.html!")

if __name__ == "__main__":
    update_multiangle_animation()
