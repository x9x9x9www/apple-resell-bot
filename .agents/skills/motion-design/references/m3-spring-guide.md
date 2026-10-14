# M3 Spring Physics Guide

Material Design 3 uses a physics-based motion system that replaces traditional easing/duration with spring dynamics. This guide explains the spatial/effects distinction and how to select the right spring.

## The M3 Spring System

M3 defines **6 spring configurations** in a 3×2 matrix:

| Speed | Spatial (damping 0.9) | Effects (damping 1.0) |
|-------|----------------------|----------------------|
| **Fast** | stiffness: 1400 | stiffness: 3800 |
| **Default** | stiffness: 700 | stiffness: 1600 |
| **Slow** | stiffness: 300 | stiffness: 800 |

## Spatial vs Effects

### Spatial Springs (damping: 0.9)

Used for properties that can naturally overshoot:
- **Position** (x, y, z translation)
- **Scale** (size changes)
- **Rotation** (angular transforms)

The 0.9 damping ratio allows slight overshoot, giving motion a natural, physical feel.

### Effects Springs (damping: 1.0)

Used for properties that should NOT overshoot:
- **Opacity** (fade in/out)
- **Color** (background, border, text color)
- **Filter** (blur, brightness, contrast)

The 1.0 damping ratio is "critically damped" - no overshoot, clean settle.

## Selection Decision Tree

```
What property are you animating?
│
├── Position (x, y, translateX, translateY, left, top, etc.)
│   └── Use: SPATIAL
│
├── Scale (scaleX, scaleY, scale, width, height)
│   └── Use: SPATIAL
│
├── Rotation (rotate, rotateX, rotateY, rotateZ)
│   └── Use: SPATIAL
│
├── Opacity
│   └── Use: EFFECTS
│
├── Color (color, backgroundColor, borderColor, fill, stroke)
│   └── Use: EFFECTS
│
└── Filter (blur, brightness, contrast, grayscale, etc.)
    └── Use: EFFECTS


What is the size/prominence of the element?
│
├── Small component (button, switch, icon, chip)
│   └── Use: FAST
│
├── Medium element (card, dialog, partial-screen)
│   └── Use: DEFAULT
│
└── Large element (full-screen, page transition, hero)
    └── Use: SLOW
```

## Quick Reference

| Animation | Spring Token |
|-----------|--------------|
| Button press feedback | `fast.spatial` |
| Button color change | `fast.effects` |
| Card expand | `default.spatial` |
| Card fade in | `default.effects` |
| Page slide | `slow.spatial` |
| Page fade | `slow.effects` |
| Icon bounce | `fast.spatial` |
| Icon color | `fast.effects` |
| Modal enter | `default.spatial` |
| Modal scrim | `default.effects` |

## Why Spatial/Effects Matters

### Without distinction (wrong):

```jsx
// Opacity can overshoot to > 1.0 or < 0.0
// This causes visual glitches!
<motion.div
  animate={{ opacity: 1 }}
  transition={{ type: "spring", damping: 0.9, stiffness: 700 }}
/>
```

### With distinction (correct):

```jsx
// Position can overshoot naturally
<motion.div
  animate={{ x: 100 }}
  transition={{ type: "spring", damping: 0.9, stiffness: 700 }}
/>

// Opacity uses critically damped spring - no overshoot
<motion.div
  animate={{ opacity: 1 }}
  transition={{ type: "spring", damping: 1.0, stiffness: 1600 }}
/>
```

## Platform Implementation

### Framer Motion / Motion

```tsx
const m3Springs = {
  fast: {
    spatial: { damping: 0.9, stiffness: 1400, mass: 1 },
    effects: { damping: 1.0, stiffness: 3800, mass: 1 }
  },
  default: {
    spatial: { damping: 0.9, stiffness: 700, mass: 1 },
    effects: { damping: 1.0, stiffness: 1600, mass: 1 }
  },
  slow: {
    spatial: { damping: 0.9, stiffness: 300, mass: 1 },
    effects: { damping: 1.0, stiffness: 800, mass: 1 }
  }
};

// Usage
<motion.div
  animate={{ x: 100, opacity: 1 }}
  transition={{
    x: { type: "spring", ...m3Springs.default.spatial },
    opacity: { type: "spring", ...m3Springs.default.effects }
  }}
/>
```

### React Spring

```tsx
import { useSpring, animated } from '@react-spring/web';

const m3Config = {
  fast: {
    spatial: { damping: 0.9, frequency: 1400 / (2 * Math.PI) },
    effects: { damping: 1.0, frequency: 3800 / (2 * Math.PI) }
  },
  default: {
    spatial: { damping: 0.9, frequency: 700 / (2 * Math.PI) },
    effects: { damping: 1.0, frequency: 1600 / (2 * Math.PI) }
  },
  slow: {
    spatial: { damping: 0.9, frequency: 300 / (2 * Math.PI) },
    effects: { damping: 1.0, frequency: 800 / (2 * Math.PI) }
  }
};
```

### Android (Compose)

```kotlin
// M3 springs are built into Material 3 Compose
import androidx.compose.material3.MaterialTheme

// Access via MaterialTheme.motion
val fastSpatial = MaterialTheme.motion.fastSpatial
val defaultEffects = MaterialTheme.motion.defaultEffects

// Or define manually
val fastSpatialSpec = spring<Float>(
    dampingRatio = 0.9f,
    stiffness = 1400f
)
```

### CSS (Web Animations API)

```javascript
// CSS doesn't natively support spring physics
// Use WAAPI with custom spring solver

function springAnimation(element, property, toValue, spring) {
  const { damping, stiffness, mass } = spring;

  // Calculate spring parameters
  const omega = Math.sqrt(stiffness / mass);
  const zeta = damping / (2 * Math.sqrt(stiffness * mass));

  // Generate keyframes from spring physics
  const keyframes = generateSpringKeyframes(omega, zeta, toValue);

  return element.animate(
    keyframes.map(v => ({ [property]: v })),
    { duration: calculateSpringDuration(omega, zeta) }
  );
}
```

### GSAP

```javascript
// GSAP doesn't have native spring support
// Use CustomWiggle or physics plugins

// Option 1: Approximate with CustomEase
gsap.registerPlugin(CustomEase);

// Fast spatial approximation
CustomEase.create("m3FastSpatial", "M0,0 C0.12,0.52 0.32,1.08 0.54,1 0.76,0.92 1,1 1,1");

// Option 2: Use physics plugin for true spring
gsap.registerPlugin(Physics2DPlugin);
```

## Damping Ratio Explained

| Damping | Behavior | Use |
|---------|----------|-----|
| < 1.0 | Under-damped, oscillates | Spatial properties |
| = 1.0 | Critically damped, no overshoot | Effects properties |
| > 1.0 | Over-damped, sluggish | Generally avoid |

### Visual:

```
Position with damping 0.9 (spatial):
───────────────────────────
       ╭───╮
      ╱     ╲
─────╱       ╲────────────── target
    ╱         ╰────────────
   ╱
──╱

Opacity with damping 1.0 (effects):
───────────────────────────
                   ╭───────
                  ╱
                 ╱
                ╱
               ╱
──────────────╱─────────── target
```

## Migration from Legacy Springs

| Legacy Token | M3 Replacement |
|--------------|----------------|
| `spring.standard` | `spring.default.spatial` |
| `spring.snappy` | `spring.fast.spatial` |
| `spring.gentle` | `spring.slow.spatial` |
| `spring.enter` | `spring.default.spatial` |

## When NOT to Use Springs

1. **Continuous animations** (spinners, progress) - Use linear
2. **Instant feedback** (<50ms) - Use no transition
3. **Reduced motion users** - Use instant or very short duration
4. **Performance-critical** - Springs are more CPU-intensive than beziers

## References

- [M3 Motion Overview](https://m3.material.io/styles/motion/overview)
- [Material Components Android Motion](https://github.com/material-components/material-components-android/blob/master/docs/theming/Motion.md)
- [Spring Physics Explained](https://www.joshwcomeau.com/animation/a-friendly-introduction-to-spring-physics/)
