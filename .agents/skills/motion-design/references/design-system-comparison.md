# Design System Motion Comparison

## Principles Comparison

| System | Categories |
|--------|------------|
| **M3** | Informative, Focused, Expressive |
| **Fluent** | Functional, Natural, Consistent, Appealing |
| **Carbon** | Productive, Expressive |
| **Apple** | Purpose, Continuity, Fluidity |

## Easing Comparison

| Purpose | M3 | Fluent | Carbon |
|---------|-----|--------|--------|
| Standard | (0.2, 0, 0, 1) | (0.1, 0.9, 0.2, 1) | (0.2, 0, 0.38, 0.9) |
| Enter | (0.05, 0.7, 0.1, 1) | (0.1, 0.9, 0.2, 1) | (0, 0, 0.38, 0.9) |
| Exit | (0.3, 0, 0.8, 0.15) | (0.9, 0.1, 1, 0.2) | (0.2, 0, 1, 0.9) |
| Linear | (0, 0, 1, 1) | (0, 0, 1, 1) | (0, 0, 1, 1) |

## Duration Comparison

| Use Case | M3 | Fluent | Carbon |
|----------|-----|--------|--------|
| Micro | 50ms (short-1) | 50ms (ultra-fast) | 70ms (fast-01) |
| Small | 150ms (short-3) | 150ms (fast) | 150ms (moderate-01) |
| Medium | 300ms (medium-2) | 300ms (slow) | 240ms (moderate-02) |
| Large | 500ms (long-2) | 500ms (ultra-slow) | 400ms (slow-01) |
| Expressive | - | - | 700ms (slow-02) |

## When to Use Which System

| Platform/Context | Primary System | Secondary |
|------------------|----------------|-----------|
| Android | M3 | - |
| iOS | Apple HIG | M3 for reference |
| Windows | Fluent 2 | M3 for reference |
| Web (general) | M3 | Any |
| Enterprise | Carbon | M3 |
| Cross-platform | M3 | Platform-specific adjustments |

## Mapping Table

When translating between systems:

| M3 Token | Fluent Equivalent | Carbon Equivalent |
|----------|-------------------|-------------------|
| `standard` | `decelerate` | `productive-standard` |
| `emphasized-decelerate` | `decelerate` | `productive-entrance` |
| `emphasized-accelerate` | `accelerate` | `productive-exit` |
| `short-1` (50ms) | `ultra-fast` | `fast-01` (70ms) |
| `short-4` (200ms) | `normal` | - |
| `medium-2` (300ms) | `slow` | `moderate-02` (240ms) |
| `long-2` (500ms) | `ultra-slow` | `slow-01` (400ms) |
