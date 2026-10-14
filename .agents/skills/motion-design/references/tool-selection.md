# Animation Tool Selection Guide

## Quick Decision Matrix

| Tool | Best For | Bundle Size | Learning |
|------|----------|-------------|----------|
| CSS | Simple transitions | 0kb | Low |
| GSAP | Complex sequences | ~60kb | Medium |
| Framer Motion | React apps | ~30kb | Medium |
| Motion One | Lightweight web | ~3kb | Low |
| Lottie | Pre-designed playback | ~50kb | Low |
| Rive | Interactive/stateful | ~150kb | Medium |
| Remotion | Video rendering | N/A | Medium |

## Decision Tree

```
START
│
├─ Is it a simple hover/transition?
│   └─ YES → CSS
│
├─ Is it pre-designed from After Effects?
│   └─ YES → Lottie
│
├─ Does it need complex state logic?
│   └─ YES → Rive
│
├─ Is it a complex sequence with precise timing?
│   └─ YES → GSAP
│
├─ Is it a React app with declarative needs?
│   └─ YES → Framer Motion
│
├─ Do you need smallest bundle size?
│   └─ YES → Motion One or CSS
│
└─ Are you rendering video?
    └─ YES → Remotion
```

## Tool Strengths

### CSS
- Zero bundle cost
- Hardware accelerated
- Best for: hover states, simple fades, transforms

### GSAP
- Timeline-based sequencing
- ScrollTrigger for scroll animations
- Best for: marketing pages, complex sequences

### Framer Motion
- Declarative React API
- AnimatePresence for exit animations
- Best for: React SPAs, component animations

### Motion One
- Tiny footprint (~3kb)
- Web Animations API based
- Best for: performance-critical sites

### Lottie
- Designer-to-developer workflow
- After Effects integration
- Best for: icons, illustrations, micro-interactions

### Rive
- State machine support
- Smallest file sizes
- Best for: interactive elements, games

### Remotion
- React-based video rendering
- Programmatic video generation
- Best for: dynamic video content, social media

## When NOT to Use Each Tool

| Tool | Avoid When |
|------|-----------|
| CSS | Complex sequences, scroll-based |
| GSAP | Simple transitions, bundle-sensitive |
| Framer Motion | Non-React projects |
| Motion One | Need timeline sequencing |
| Lottie | Need interactivity, state logic |
| Rive | Simple playback, After Effects workflow |
| Remotion | Real-time web animations |
