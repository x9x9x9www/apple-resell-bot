/**
 * Framer Motion M3 Presets
 * Material Design 3 motion tokens for Framer Motion
 *
 * IMPORTANT: This file imports values from token files to maintain
 * a single source of truth. See tokens/*.tokens.json for definitions.
 */

import type { Transition, Variants } from 'framer-motion';

// Import token definitions from JSON files
// Note: Requires bundler with JSON support and resolveJsonModule in tsconfig
import durationTokens from '../tokens/duration.tokens.json';
import easingTokens from '../tokens/easing.tokens.json';

// ============================================
// Duration Tokens (seconds)
// Imported from tokens/duration.tokens.json
// ============================================

// Parse duration from "250ms" to 0.25 seconds
const parseDurationToSeconds = (value: string): number =>
  parseInt(value.replace('ms', ''), 10) / 1000;

export const duration = {
  'short-1': parseDurationToSeconds(durationTokens.motion.duration['short-1'].$value),
  'short-2': parseDurationToSeconds(durationTokens.motion.duration['short-2'].$value),
  'short-3': parseDurationToSeconds(durationTokens.motion.duration['short-3'].$value),
  'short-4': parseDurationToSeconds(durationTokens.motion.duration['short-4'].$value),
  'medium-1': parseDurationToSeconds(durationTokens.motion.duration['medium-1'].$value),
  'medium-2': parseDurationToSeconds(durationTokens.motion.duration['medium-2'].$value),
  'medium-3': parseDurationToSeconds(durationTokens.motion.duration['medium-3'].$value),
  'medium-4': parseDurationToSeconds(durationTokens.motion.duration['medium-4'].$value),
  'long-1': parseDurationToSeconds(durationTokens.motion.duration['long-1'].$value),
  'long-2': parseDurationToSeconds(durationTokens.motion.duration['long-2'].$value),
  'long-3': parseDurationToSeconds(durationTokens.motion.duration['long-3'].$value),
  'long-4': parseDurationToSeconds(durationTokens.motion.duration['long-4'].$value),
} as const;

export type DurationToken = keyof typeof duration;

// ============================================
// Easing Tokens (cubic-bezier arrays)
// Imported from tokens/easing.tokens.json
// ============================================

export const easing = {
  standard: easingTokens.motion.easing.standard.$value as readonly [number, number, number, number],
  emphasized: easingTokens.motion.easing.emphasized.$value as readonly [number, number, number, number],
  'emphasized-decelerate': easingTokens.motion.easing['emphasized-decelerate'].$value as readonly [number, number, number, number],
  'emphasized-accelerate': easingTokens.motion.easing['emphasized-accelerate'].$value as readonly [number, number, number, number],
  'standard-decelerate': easingTokens.motion.easing['standard-decelerate'].$value as readonly [number, number, number, number],
  'standard-accelerate': easingTokens.motion.easing['standard-accelerate'].$value as readonly [number, number, number, number],
  linear: easingTokens.motion.easing.linear.$value as readonly [number, number, number, number],
} as const;

export type EasingToken = keyof typeof easing;

// ============================================
// Spring Configs
// Imported from tokens/easing.tokens.json (spring section)
// ============================================

type SpringConfig = { damping: number; stiffness: number; mass: number };

export const springConfig = {
  standard: easingTokens.motion.spring['spring-standard'].$value as SpringConfig,
  snappy: easingTokens.motion.spring['spring-snappy'].$value as SpringConfig,
  bouncy: easingTokens.motion.spring['spring-bouncy'].$value as SpringConfig,
  gentle: easingTokens.motion.spring['spring-gentle'].$value as SpringConfig,
  enter: easingTokens.motion.spring['spring-enter'].$value as SpringConfig,
} as const;

export type SpringToken = keyof typeof springConfig;

// ============================================
// Transition Presets
// ============================================

export const transition = {
  enter: {
    duration: duration['medium-1'],
    ease: easing['emphasized-decelerate'],
  } as Transition,

  exit: {
    duration: duration['short-4'],
    ease: easing['emphasized-accelerate'],
  } as Transition,

  standard: {
    duration: duration['short-4'],
    ease: easing.standard,
  } as Transition,

  springEnter: {
    type: 'spring',
    ...springConfig.enter,
  } as Transition,

  springBouncy: {
    type: 'spring',
    ...springConfig.bouncy,
  } as Transition,
};

// ============================================
// Variant Presets
// ============================================

/**
 * Fade variants
 */
export const fadeVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: transition.enter,
  },
  exit: {
    opacity: 0,
    transition: transition.exit,
  },
};

/**
 * Slide up + fade variants
 */
export const slideUpVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transition.enter,
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: transition.exit,
  },
};

/**
 * Scale + fade variants
 */
export const scaleVariants: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: transition.enter,
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: transition.exit,
  },
};

/**
 * Spring scale variants
 */
export const springScaleVariants: Variants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: transition.springEnter,
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    transition: transition.exit,
  },
};

// ============================================
// Container Variants (for stagger)
// ============================================

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.03,
      staggerDirection: -1,
    },
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transition.enter,
  },
  exit: {
    opacity: 0,
    y: -8,
    transition: transition.exit,
  },
};

// ============================================
// Gesture Presets
// ============================================

export const hoverScale = {
  whileHover: { scale: 1.05 },
  whileTap: { scale: 0.95 },
  transition: { duration: duration['short-3'] },
};

export const hoverLift = {
  whileHover: { y: -4, boxShadow: '0 8px 30px rgba(0,0,0,0.12)' },
  transition: { duration: duration['short-3'] },
};

// ============================================
// Reduced Motion Helpers
// ============================================

/**
 * Get reduced motion safe variants
 */
export const getReducedMotionVariants = (
  fullVariants: Variants,
  reducedMotion: boolean
): Variants => {
  if (!reducedMotion) return fullVariants;

  return {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { duration: 0.1 },
    },
    exit: {
      opacity: 0,
      transition: { duration: 0.1 },
    },
  };
};

/**
 * Create stagger variants with reduced motion support
 */
export const createStaggerVariants = (
  staggerDelay: number = 0.05,
  reducedMotion: boolean = false
): { container: Variants; item: Variants } => {
  if (reducedMotion) {
    return {
      container: {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { duration: 0.1 } },
      },
      item: {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { duration: 0.1 } },
      },
    };
  }

  return {
    container: {
      hidden: { opacity: 0 },
      visible: {
        opacity: 1,
        transition: {
          staggerChildren: staggerDelay,
        },
      },
    },
    item: {
      hidden: { opacity: 0, y: 16 },
      visible: {
        opacity: 1,
        y: 0,
        transition: transition.enter,
      },
    },
  };
};
