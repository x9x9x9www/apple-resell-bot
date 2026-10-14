/**
 * GSAP M3 Motion Presets
 * Material Design 3 motion tokens for GSAP animations
 *
 * IMPORTANT: This file imports values from token files to maintain
 * a single source of truth. See tokens/*.tokens.json for definitions.
 */

// Import token definitions from JSON files
// Note: Requires bundler with JSON support (webpack, vite, etc.)
import durationTokens from '../tokens/duration.tokens.json';
import easingTokens from '../tokens/easing.tokens.json';
import sequencingTokens from '../tokens/sequencing.tokens.json';
import stateLayerTokens from '../tokens/state-layer.tokens.json';
import entranceTokens from '../tokens/entrance-intensity.tokens.json';
import motionLevels from '../tokens/motion-levels.tokens.json';

// ============================================
// Duration Tokens (seconds for GSAP)
// Imported from tokens/duration.tokens.json
// ============================================

// Parse duration from "250ms" to 0.25 seconds
const parseDurationToSeconds = (value) => parseInt(value.replace('ms', ''), 10) / 1000;

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
};

// ============================================
// Easing Tokens (CSS cubic-bezier strings)
// Imported from tokens/easing.tokens.json
// ============================================

// Convert [0.2, 0, 0, 1] to "cubic-bezier(0.2, 0, 0, 1)"
const toCubicBezier = (bezier) => `cubic-bezier(${bezier.join(', ')})`;

export const easing = {
  standard: toCubicBezier(easingTokens.motion.easing.standard.$value),
  emphasized: toCubicBezier(easingTokens.motion.easing.emphasized.$value),
  'emphasized-decelerate': toCubicBezier(easingTokens.motion.easing['emphasized-decelerate'].$value),
  'emphasized-accelerate': toCubicBezier(easingTokens.motion.easing['emphasized-accelerate'].$value),
  'standard-decelerate': toCubicBezier(easingTokens.motion.easing['standard-decelerate'].$value),
  'standard-accelerate': toCubicBezier(easingTokens.motion.easing['standard-accelerate'].$value),
  linear: 'none',
};

// ============================================
// GSAP Power Equivalents
// ============================================

export const gsapEasing = {
  standard: 'power2.out',
  enter: 'power3.out',
  exit: 'power2.in',
  linear: 'none',
};

// ============================================
// Preset Animations
// ============================================

/**
 * Fade in animation config
 */
export const fadeIn = {
  opacity: 0,
  duration: duration['medium-1'],
  ease: easing['emphasized-decelerate'],
};

/**
 * Fade out animation config
 */
export const fadeOut = {
  opacity: 0,
  duration: duration['short-4'],
  ease: easing['emphasized-accelerate'],
};

/**
 * Slide up + fade in
 */
export const slideUpIn = {
  opacity: 0,
  y: 20,
  duration: duration['medium-1'],
  ease: easing['emphasized-decelerate'],
};

/**
 * Slide down + fade out
 */
export const slideDownOut = {
  opacity: 0,
  y: 20,
  duration: duration['short-4'],
  ease: easing['emphasized-accelerate'],
};

/**
 * Scale in
 */
export const scaleIn = {
  opacity: 0,
  scale: 0.95,
  duration: duration['medium-1'],
  ease: easing['emphasized-decelerate'],
};

/**
 * Scale out
 */
export const scaleOut = {
  opacity: 0,
  scale: 0.95,
  duration: duration['short-4'],
  ease: easing['emphasized-accelerate'],
};

// ============================================
// Stagger Configurations (M3 Compliant)
// Imported from tokens/sequencing.tokens.json
// ============================================

const parseStaggerMs = (value) => parseInt(value.replace('ms', ''), 10) / 1000;

export const stagger = {
  micro: parseStaggerMs(sequencingTokens.motion.sequencing.stagger.micro.$value),  // 10ms
  small: parseStaggerMs(sequencingTokens.motion.sequencing.stagger.small.$value),  // 15ms
  medium: parseStaggerMs(sequencingTokens.motion.sequencing.stagger.medium.$value), // 20ms (M3 max)
  large: parseStaggerMs(sequencingTokens.motion.sequencing.stagger.large.$value),   // 20ms (capped)
};

// M3 choreography constants
export const choreography = {
  maxTotalDuration: 0.5, // 500ms max total sequence
  enterExitRatio: sequencingTokens.motion.sequencing.choreography['enter-exit-ratio'].$value, // 0.7
};

// ============================================
// State Layer Configurations
// Imported from tokens/state-layer.tokens.json
// ============================================

export const stateLayer = {
  opacity: {
    hover: stateLayerTokens.motion['state-layer'].opacity.hover.$value,   // 0.08
    focus: stateLayerTokens.motion['state-layer'].opacity.focus.$value,   // 0.12
    press: stateLayerTokens.motion['state-layer'].opacity.press.$value,   // 0.12
    drag: stateLayerTokens.motion['state-layer'].opacity.drag.$value,     // 0.16
  },
  ripple: {
    duration: parseStaggerMs(stateLayerTokens.motion['state-layer'].ripple.duration.$value),
    opacityStart: stateLayerTokens.motion['state-layer'].ripple['opacity-start'].$value,
    scaleEnd: stateLayerTokens.motion['state-layer'].ripple['scale-end'].$value,
  },
};

// ============================================
// Entrance Intensity Presets
// Imported from tokens/entrance-intensity.tokens.json
// ============================================

export const entranceIntensity = {
  emphasized: {
    scale: entranceTokens.motion.entrance.emphasized.scale.start.$value, // 0
    opacity: 0,
    y: 32,
    duration: duration['medium-2'],
    ease: easing['emphasized-decelerate'],
  },
  standard: {
    scale: entranceTokens.motion.entrance.standard.scale.start.$value, // 0.95
    opacity: 0,
    y: 8,
    duration: duration['short-4'],
    ease: easing['standard-decelerate'],
  },
  subtle: {
    opacity: 0,
    duration: duration['short-3'],
    ease: easing['standard-decelerate'],
  },
};

// ============================================
// Platform Motion Level
// ============================================

export const getMotionLevel = () => {
  if (typeof window === 'undefined') return 'L3-full';

  // Check reduced motion preference
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return 'L1-none';
  }

  // Check for low power mode (if available)
  if (navigator.getBattery) {
    navigator.getBattery().then(battery => {
      if (battery.level < 0.2) return 'L2-simplified';
    });
  }

  return 'L3-full';
};

export const motionLevelMultiplier = {
  'L1-none': 0,
  'L2-simplified': 0.5,
  'L3-full': 1.0,
  'L4-enhanced': 1.2,
};

/**
 * Get adaptive stagger based on item count
 */
export const getAdaptiveStagger = (itemCount, maxTotal = 0.8) => {
  const minDelay = 0.025;
  const maxDelay = 0.05;
  const calculated = maxTotal / itemCount;
  return Math.max(minDelay, Math.min(maxDelay, calculated));
};

// ============================================
// Timeline Presets
// ============================================

/**
 * Create a staggered entrance timeline
 * @param {gsap} gsap - GSAP instance
 * @param {string} selector - CSS selector for elements
 * @param {object} options - Animation options
 */
export const createEntranceTimeline = (gsap, selector, options = {}) => {
  const {
    staggerDelay = stagger.normal,
    distance = 20,
    duration: dur = duration['medium-1'],
  } = options;

  return gsap.from(selector, {
    opacity: 0,
    y: distance,
    duration: dur,
    ease: easing['emphasized-decelerate'],
    stagger: staggerDelay,
  });
};

/**
 * Create a staggered exit timeline
 */
export const createExitTimeline = (gsap, selector, options = {}) => {
  const {
    staggerDelay = stagger.fast,
    distance = 20,
    duration: dur = duration['short-4'],
  } = options;

  return gsap.to(selector, {
    opacity: 0,
    y: -distance,
    duration: dur,
    ease: easing['emphasized-accelerate'],
    stagger: staggerDelay,
  });
};

// ============================================
// Reduced Motion Support
// ============================================

export const prefersReducedMotion =
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/**
 * Get animation config respecting reduced motion
 */
export const getMotionSafeConfig = (fullConfig, reducedConfig = {}) => {
  if (prefersReducedMotion) {
    return {
      opacity: fullConfig.opacity ?? 0,
      duration: 0.1,
      ease: 'none',
      ...reducedConfig,
    };
  }
  return fullConfig;
};
