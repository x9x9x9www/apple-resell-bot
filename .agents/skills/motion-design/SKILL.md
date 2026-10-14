---
name: motion-design
description: Create animations and motion graphics using industry standards. Use when asked to animate UI elements, create video content, implement transitions, or build motion systems. Implements W3C Design Tokens, Material Design 3 baseline, and Lottie specification compliance.
---

# Motion Design Agent

Motion design specialist grounded in industry standards. Creates animations by composing knowledge from specialized sub-skills and standardized token libraries.

## Standards Compliance

This agent implements:
- **W3C Design Tokens (2025.10)** for token interchange
- **Material Design 3** as primary motion baseline
- **Lottie Spec v1.0** for animation export
- **WCAG 2.1** for accessibility

## Industry Context

Material Design 3 serves as the baseline because:
1. Most comprehensive public motion specification
2. Widely adopted across industry (referenced by Klarna, others)
3. Clear token naming conventions
4. Well-documented transition patterns

Cross-reference other systems when:
- Building for Windows/Office → Fluent 2
- Building for Apple platforms → Apple HIG
- Building enterprise apps → Carbon (IBM)

## Workflow

1. **Parse** — Identify animation type, platform, constraints
2. **Select tokens** — Load from `tokens/*.tokens.json`
3. **Apply principles** — Consult `skills/motion-principles/`
4. **Choose pattern** — Reference `skills/transitions/` or `skills/entrance-patterns/`
5. **Implement** — Use appropriate tool (Remotion, GSAP, Framer Motion, Lottie)
6. **Verify accessibility** — Check `skills/accessibility/`

## Token Library

All motion values are stored in W3C DTCG format (44 token files):

```
tokens/
├── motion.tokens.json         # Complete token set
├── easing.tokens.json         # Easing curves + springs
├── duration.tokens.json       # Duration scale
├── spring.tokens.json         # Spring physics
│
├── # Transform tokens
├── position.tokens.json       # Position and translation
├── scale.tokens.json          # Scale transforms
├── rotation.tokens.json       # Rotation and spin
├── skew.tokens.json           # Skew and slant
├── transform-origin.tokens.json # Transform origins
│
├── # Visibility tokens
├── opacity.tokens.json        # Opacity and fade
├── reveal.tokens.json         # Reveal patterns
├── blur.tokens.json           # Blur effects
│
├── # Orchestration tokens
├── sequencing.tokens.json     # Stagger and cascade
├── looping.tokens.json        # Loop patterns
├── procedural.tokens.json     # Procedural motion
│
├── # Disney principle tokens
├── anticipation.tokens.json   # Disney: anticipation
├── squash-stretch.tokens.json # Disney: squash-stretch
├── follow-through.tokens.json # Disney: follow-through
├── exaggeration.tokens.json   # Disney: exaggeration
│
├── # Effect tokens
├── particles.tokens.json      # Particle systems
├── distortion.tokens.json     # Glitch and distortion
├── glow-shadow.tokens.json    # Glow and shadow
├── reflection.tokens.json     # Reflections
├── texture.tokens.json        # Texture effects
├── motion-blur.tokens.json    # Motion blur
├── motion-path.tokens.json    # Motion paths
├── depth.tokens.json          # 3D depth
│
├── # Space and camera tokens
├── camera.tokens.json         # Camera movements
│
├── # Shape and path tokens
├── morphing.tokens.json       # Shape morphing
├── stroke.tokens.json         # Stroke animation
├── masks.tokens.json          # Mask animation
│
├── # Specialized tokens
├── typography.tokens.json     # Text animation
├── stylization.tokens.json    # Artistic styles
├── audio.tokens.json          # Audio-reactive
├── character.tokens.json      # Character animation
├── compositing.tokens.json    # Layer compositing
├── cinematic.tokens.json      # Cinematic effects
├── color.tokens.json          # Color animation
├── physics.tokens.json        # Physics simulation
├── playback.tokens.json       # Playback control
│
├── # Semantic tokens
├── emotion.tokens.json        # Emotion mapping
├── components.tokens.json     # UI components
├── recipes.tokens.json        # Animation recipes
└── export.tokens.json         # Export settings
```

Token references use W3C DTCG syntax: `{motion.duration.medium-1}`

Load tokens programmatically or reference by path in skill files.

## Sub-Skill Index

### Foundation Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Motion philosophy | `skills/motion-principles/` | M3, Carbon, Fluent |
| Easing curves | `skills/easing/` | W3C DTCG, M3, CSS, Apple HIG |
| Duration/timing | `skills/duration/` | W3C DTCG, M3, Apple HIG |

### Disney Principle Skills

| Principle | Skill | Use Case |
|-----------|-------|----------|
| Anticipation | `skills/anticipation/` | Preparation before action |
| Squash & Stretch | `skills/squash-stretch/` | Weight and flexibility |
| Follow-Through | `skills/follow-through/` | Motion after main action |
| Secondary Action | `skills/secondary-action/` | Supporting animations |
| Exaggeration | `skills/exaggeration/` | Amplified motion |
| Arc Motion | `skills/arc-motion/` | Natural curved paths |

### Emotion Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Emotion-to-animation mapping | `skills/emotion-mapping/` | Arousal-valence model |
| Emotion token selection | `skills/emotion-selection/` | Token guidance |

### Pattern Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Page transitions | `skills/transitions/` | M3 transition patterns |
| Entrances | `skills/entrance-patterns/` | M3 |
| Exits | `skills/exit-patterns/` | M3 |
| Scroll animations | `skills/scroll-animations/` | GSAP ScrollTrigger |

### Component Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| UI component animations | `skills/component-animations/` | M3 components |
| Pre-built recipes | `skills/animation-recipes/` | All patterns |
| Loading indicators | `skills/loading-states/` | WCAG 2.1 |
| Touch/gesture motion | `skills/gesture-motion/` | Platform HIG |

### Implementation Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Lottie export | `skills/lottie/` | LAC Lottie Spec v1.0 |
| Remotion video | `skills/remotion/` | Remotion docs |
| Code generation | `skills/code-generation/` | Platform-specific |
| Tool selection | `skills/tools/` | GSAP, Framer Motion, Rive |
| Export settings | `skills/export/` | Format, resolution, quality |

### Transform Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Position/translation | `skills/position/` | M3, CSS transforms |
| Scale transforms | `skills/scale/` | M3, squash-stretch |
| Rotation/spin | `skills/rotation/` | 2D/3D rotation |
| Skew/slant | `skills/skew/` | CSS skew |

### Visibility Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Opacity/fade | `skills/opacity/` | M3 |
| Reveal patterns | `skills/reveals/` | Mask reveals, wipes |
| Blur effects | `skills/blur/` | Motion blur, focus |

### Orchestration Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Stagger/cascade | `skills/sequencing/` | M3 stagger |
| Loops/oscillation | `skills/looping/` | Loop patterns |
| Procedural motion | `skills/procedural/` | Noise, wiggle |

### Effect Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Particles | `skills/particles/` | Confetti, snow, sparks |
| Distortion | `skills/distortion/` | Glitch, wave, ripple |
| Glow/shadow | `skills/glow-shadow/` | Neon, elevation |
| Reflections | `skills/reflection/` | Floor, water, glass |
| Textures | `skills/texture/` | Grain, noise, patterns |

### Space & Camera Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Camera movements | `skills/camera/` | Pan, tilt, dolly |
| Depth/3D space | `skills/depth/` | Z-axis, perspective |

### Shape & Path Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Shape morphing | `skills/morphing/` | Path interpolation |
| Stroke animation | `skills/stroke/` | Draw-on, dash |
| Mask animation | `skills/masks/` | Reveals, wipes |

### Specialized Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Kinetic typography | `skills/typography/` | Text animation |
| Micro-interactions | `skills/ui-micro/` | Buttons, toggles |
| Scroll storytelling | `skills/scrollytelling/` | Parallax, narrative |
| Attention direction | `skills/attention/` | Pulses, badges |
| Artistic styles | `skills/stylization/` | Vintage, minimalist |
| Audio-reactive | `skills/audio-reactive/` | Beat sync, visualizer |
| Character animation | `skills/character/` | Walk cycles, expressions |

### Production Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Layer compositing | `skills/compositing/` | Blend modes |
| Cinematic effects | `skills/cinematic/` | Letterbox, fades |

### Color & Physics Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Color animation | `skills/color/` | Hue, saturation, brightness |
| Physics simulation | `skills/physics/` | Gravity, bounce, springs |

### Control Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Playback control | `skills/playback-control/` | Speed, direction, scrubbing |

### Advanced Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| 3D transforms | `skills/3d-transforms/` | CSS 3D, WebGL |
| Motion blur | `skills/motion-blur/` | Performance-aware |
| Frame timing | `skills/frame-timing/` | Video standards |

### Quality Skills

| Need | Skill | Standards Reference |
|------|-------|---------------------|
| Accessibility | `skills/accessibility/` | WCAG 2.1 |
| Animation auditing | `skills/motion-audit/` | Performance, a11y |
| Testing patterns | `skills/testing-patterns/` | Testing frameworks |
| Platform adaptation | `skills/platform-adaptation/` | Cross-platform |

## Decision Framework

### Easing Selection (M3 Baseline)
```
ENTERING → emphasized-decelerate: cubic-bezier(0.05, 0.7, 0.1, 1)
EXITING  → emphasized-accelerate: cubic-bezier(0.3, 0, 0.8, 0.15)
MOVING   → standard: cubic-bezier(0.2, 0, 0, 1)
LOOPING  → linear: cubic-bezier(0, 0, 1, 1)
```

### Duration Selection (M3 Baseline)
```
Micro-interaction  → short1-short2 (50-100ms)
Small component    → short3-short4 (150-200ms)
Medium component   → medium1-medium2 (250-300ms)
Large transition   → medium3-medium4 (350-400ms)
Page transition    → long1-long2 (450-500ms)
```

### Tool Selection
```
Pre-designed playback    → Lottie
Interactive/stateful     → Rive
Complex JS sequences     → GSAP
React declarative        → Framer Motion
Video rendering          → Remotion
Lightweight web          → CSS / Motion One
Scroll-triggered/linked  → GSAP ScrollTrigger or Intersection Observer
```

## Reduced Motion Strategy

Standardized fallback taxonomy for all animations:

| Animation Type | Reduced Motion Fallback |
|----------------|------------------------|
| Entrance (fade + transform) | Instant opacity to 1, no transform |
| Exit (fade out) | Instant opacity to 0 |
| State change (hover, press) | Instant state or opacity shift (0.9) |
| Loading (shimmer, pulse) | Static state, no animation |
| Error (shake) | Border/color indicator only |
| Celebration (particles, bounce) | Simple opacity fade |
| Page transition | Instant cut or cross-fade only |

### Platform Implementation

```css
/* CSS */
@media (prefers-reduced-motion: reduce) {
  .animated { animation: none; transition: opacity 100ms ease; }
}
```

```javascript
// JavaScript
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
```

```typescript
// Framer Motion
import { useReducedMotion } from 'framer-motion';
const shouldReduce = useReducedMotion();
```

## Output Requirements

All implementations must:
1. Use token names from `tokens/` (not raw values)
2. Include reduced motion alternative
3. Specify which standard informed the decision
4. Provide code that imports from token files

## Version History

- **v2.1.0** — Comprehensive motion design coverage
  - Added 11 new skills: color, physics, stylization, playback-control, reflection, skew, depth, texture, audio-reactive, character, export
  - Added 11 new token files for all new skills
  - New categories: color, physics, control
  - Total: 64 skills, 44 token files

- **v2.0.0** — Major expansion
  - Added 21 new skills across 8 new categories
  - Added 19 new token files (transforms, visibility, orchestration, effects, shape-path, specialized, production)
  - Added orchestrator skill for autonomous animation generation
  - Categories: transforms, visibility, orchestration, effects, space-camera, shape-path, specialized, production
  - Total: 53 skills, 33 token files

- **v1.2.0** — Cohesion & breadth improvements
  - Added manifest.json for skill/token discovery
  - Converted 19 flat skills to proper SKILL.md format
  - Added Apple HIG cross-references to easing/duration tokens
  - Refactored presets to import from token files
  - Added W3C DTCG token alias syntax
  - New skills: emotion-selection
  - New templates: FadeThrough, SharedAxis, StaggeredList (Remotion), spring-approximation, stagger-pattern, reduced-motion (CSS), loading-spinner, success-checkmark (Lottie)
  - Added skill-relationships.md for dependency mapping
  - Total: 30 skills, 14 token files, 3 presets, 12+ templates

- **v1.1.0** — Emotion springs, template variables, platform adapters, reduced motion strategy

- **v1.0.0** — Initial release with 14 skills and 8 token files
