# Skill Relationships

Dependency map and cross-references between motion design skills (v2.1.0 - 64 skills).

## Dependency Graph

```
motion-design (root orchestrator)
├── orchestrator (autonomous generation)
│
├── Foundation Layer
│   ├── motion-principles ←→ Disney principles
│   ├── easing ← duration
│   └── duration
│
├── Disney Principles Layer
│   ├── anticipation → squash-stretch, follow-through
│   ├── squash-stretch → exaggeration
│   ├── follow-through → secondary-action
│   ├── secondary-action
│   ├── exaggeration → arc-motion
│   └── arc-motion
│
├── Transform Layer (v2.0)
│   ├── position ← easing, duration
│   ├── scale ← easing, squash-stretch
│   ├── rotation ← easing
│   └── skew ← easing (v2.1)
│
├── Visibility Layer (v2.0)
│   ├── opacity ← easing, duration
│   ├── reveals ← opacity, masks
│   └── blur ← duration
│
├── Orchestration Layer (v2.0)
│   ├── sequencing ← duration
│   ├── looping ← duration, easing
│   └── procedural ← duration
│
├── Effect Layer (v2.0, expanded v2.1)
│   ├── particles ← position, opacity
│   ├── distortion ← duration
│   ├── glow-shadow ← opacity
│   ├── reflection ← opacity, blur (v2.1)
│   └── texture ← procedural (v2.1)
│
├── Space & Camera Layer (v2.0)
│   ├── camera ← position, easing
│   └── depth ← position, blur (v2.1)
│
├── Shape & Path Layer (v2.0)
│   ├── morphing ← easing
│   ├── stroke ← duration
│   └── masks ← opacity, reveals
│
├── Specialized Layer (v2.0, expanded v2.1)
│   ├── typography ← sequencing, opacity
│   ├── ui-micro ← scale, opacity
│   ├── scrollytelling ← scroll-animations, camera
│   ├── attention ← opacity, scale, glow-shadow
│   ├── stylization ← color, texture (v2.1)
│   ├── audio-reactive ← scale, opacity, color (v2.1)
│   └── character ← position, rotation, scale (v2.1)
│
├── Production Layer (v2.0)
│   ├── compositing ← opacity, blur
│   └── cinematic ← camera, opacity
│
├── Color & Physics Layer (v2.1)
│   ├── color ← duration, easing
│   └── physics ← position, duration
│
├── Control Layer (v2.1)
│   └── playback-control ← duration, looping
│
├── Emotion Layer
│   ├── emotion-mapping ← Disney principles, easing, duration
│   └── emotion-selection ← emotion-mapping
│
├── Pattern Layer
│   ├── transitions ← easing, duration
│   ├── entrance-patterns ← anticipation, easing
│   ├── exit-patterns ← follow-through, easing
│   └── scroll-animations ← transitions
│
├── Component Layer
│   ├── component-animations ← patterns, emotion
│   ├── animation-recipes ← all above
│   ├── loading-states ← duration
│   └── gesture-motion ← duration, physics
│
├── Implementation Layer
│   ├── lottie ← patterns, Disney principles
│   ├── remotion ← patterns, duration
│   ├── code-generation ← all skills
│   ├── tools ← implementation requirements
│   └── export ← all formats (v2.1)
│
├── Advanced Layer
│   ├── 3d-transforms ← rotation, depth
│   ├── motion-blur ← duration, frame-timing
│   └── frame-timing ← duration
│
└── Quality Layer
    ├── accessibility ← all skills (required output)
    ├── motion-audit ← accessibility
    ├── testing-patterns ← all skills
    └── platform-adaptation ← all skills
```

## Skill Categories

### Foundation Skills (3 skills)

Core building blocks that other skills depend on.

| Skill | Dependencies | Dependents |
|-------|--------------|------------|
| `motion-principles` | None | All pattern and component skills |
| `easing` | None | All animation skills |
| `duration` | None | All animation skills |

### Disney Principle Skills (6 skills)

Animation principles that inform natural motion.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `anticipation` | motion-principles | squash-stretch, exaggeration |
| `squash-stretch` | motion-principles | anticipation, follow-through |
| `follow-through` | motion-principles | secondary-action, exit-patterns |
| `secondary-action` | motion-principles | follow-through, component-animations |
| `exaggeration` | motion-principles | emotion-mapping, animation-recipes |
| `arc-motion` | motion-principles | gesture-motion, 3d-transforms |

### Transform Skills (4 skills)

Core transform animations.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `position` | easing, duration | entrance-patterns, camera |
| `scale` | easing, squash-stretch | ui-micro, attention |
| `rotation` | easing | 3d-transforms, character |
| `skew` | easing | typography, stylization |

### Visibility Skills (3 skills)

Visibility and reveal animations.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `opacity` | easing, duration | entrance-patterns, exit-patterns |
| `reveals` | opacity, masks | transitions, scrollytelling |
| `blur` | duration | depth, cinematic |

### Orchestration Skills (3 skills)

Animation coordination.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `sequencing` | duration | entrance-patterns, typography |
| `looping` | duration, easing | loading-states, procedural |
| `procedural` | duration | particles, texture |

### Effect Skills (5 skills)

Visual effects.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `particles` | position, opacity | attention, stylization |
| `distortion` | duration | glitch effects, stylization |
| `glow-shadow` | opacity | attention, ui-micro |
| `reflection` | opacity, blur | depth, cinematic |
| `texture` | procedural | stylization, cinematic |

### Space & Camera Skills (2 skills)

Spatial and camera effects.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `camera` | position, easing | cinematic, scrollytelling |
| `depth` | position, blur | 3d-transforms, camera |

### Shape & Path Skills (3 skills)

Shape and path animations.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `morphing` | easing | reveals, typography |
| `stroke` | duration | reveals, typography |
| `masks` | opacity | reveals, compositing |

### Specialized Skills (7 skills)

Domain-specific animations.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `typography` | sequencing, opacity | scrollytelling, attention |
| `ui-micro` | scale, opacity | component-animations |
| `scrollytelling` | scroll-animations, camera | typography, reveals |
| `attention` | opacity, scale, glow-shadow | ui-micro, loading-states |
| `stylization` | color, texture | cinematic, typography |
| `audio-reactive` | scale, opacity, color | particles, visualizations |
| `character` | position, rotation, scale | lottie, animation-recipes |

### Production Skills (2 skills)

Production and cinematic.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `compositing` | opacity, blur | cinematic, stylization |
| `cinematic` | camera, opacity | compositing, stylization |

### Color & Physics Skills (2 skills)

Color and physics animations.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `color` | duration, easing | stylization, transitions |
| `physics` | position, duration | character, particles |

### Control Skills (1 skill)

Playback control.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `playback-control` | duration, looping | lottie, remotion |

### Pattern Skills (4 skills)

Reusable animation patterns.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `transitions` | easing, duration | entrance-patterns, exit-patterns |
| `entrance-patterns` | anticipation, easing | transitions, component-animations |
| `exit-patterns` | follow-through, easing | transitions, component-animations |
| `scroll-animations` | transitions | entrance-patterns, gesture-motion |

### Component Skills (4 skills)

UI component-specific animations.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `component-animations` | patterns, emotion | animation-recipes |
| `animation-recipes` | all patterns, emotion | code-generation |
| `loading-states` | duration, accessibility | component-animations |
| `gesture-motion` | duration, physics | component-animations |

### Implementation Skills (5 skills)

Tool and format-specific implementations.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `lottie` | patterns | export, code-generation |
| `remotion` | patterns, duration | export, code-generation |
| `code-generation` | all skills | tools |
| `tools` | implementation needs | code-generation |
| `export` | all formats | lottie, remotion |

### Quality Skills (4 skills)

Quality assurance and compliance.

| Skill | Required By | Validates |
|-------|-------------|-----------|
| `accessibility` | All animations | WCAG 2.1 compliance |
| `motion-audit` | Quality checks | Performance, accessibility |
| `testing-patterns` | All implementations | Animation correctness |
| `platform-adaptation` | Cross-platform work | Platform consistency |

### Emotion Skills (2 skills)

Emotion-driven animation.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `emotion-mapping` | Disney principles, easing | component-animations |
| `emotion-selection` | emotion-mapping | animation-recipes |

### Advanced Skills (3 skills)

Advanced techniques.

| Skill | Primary Depends On | Commonly Used With |
|-------|-------------------|-------------------|
| `3d-transforms` | rotation, depth | camera, cinematic |
| `motion-blur` | duration, frame-timing | cinematic, camera |
| `frame-timing` | duration | remotion, export |

## Common Skill Combinations

### UI Animation Flow

```
User request → motion-principles
            → emotion-selection (if emotional context)
            → animation-recipes
            → code-generation
            → accessibility (verification)
```

### Physics-Based Animation (v2.1)

```
physics + position + squash-stretch
→ character or particles
→ stylization (optional)
→ export
```

### Audio-Reactive Visualization (v2.1)

```
audio-reactive + color + scale + opacity
→ particles (optional)
→ stylization
→ export
```

### Cinematic Production

```
camera + depth + color + blur
→ compositing
→ cinematic
→ stylization
→ export
```

### Character Animation (v2.1)

```
character + physics + position + rotation + scale
→ squash-stretch + follow-through
→ lottie or remotion
→ export
```

### Interactive Animation

```
gesture-motion + physics + arc-motion + duration
→ component-animations
→ testing-patterns
```

## Cross-Reference Requirements

All SKILL.md files should include a "Cross-References" section that references:

1. **Direct dependencies** - Skills this skill builds upon
2. **Common companions** - Skills frequently used together
3. **Downstream skills** - Skills that depend on this one

### Example Cross-References Section

```markdown
## Cross-References

- See `easing/` for timing curves
- See `duration/` for animation timing
- See `physics/` for realistic motion
- See `accessibility/` for reduced motion alternatives
```
