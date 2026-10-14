/**
 * Remotion M3 Motion Presets
 * Material Design 3 motion tokens for Remotion video rendering
 *
 * IMPORTANT: This file imports values from token files to maintain
 * a single source of truth. See tokens/*.tokens.json for definitions.
 */

import { Easing, interpolate, spring } from 'remotion';

// Import token definitions from JSON files
// Note: In a real build, these would use a JSON import plugin
import durationTokens from '../tokens/duration.tokens.json';
import easingTokens from '../tokens/easing.tokens.json';
import sequencingTokens from '../tokens/sequencing.tokens.json';
import crossFadeTokens from '../tokens/cross-fade.tokens.json';
import entranceTokens from '../tokens/entrance-intensity.tokens.json';
import motionLevels from '../tokens/motion-levels.tokens.json';

// ============================================
// Duration Tokens (milliseconds)
// Imported from tokens/duration.tokens.json
// ============================================

// Parse duration values from token format ("250ms" -> 250)
const parseDuration = (value: string): number => parseInt(value.replace('ms', ''), 10);

export const duration = {
  'short-1': parseDuration(durationTokens.motion.duration['short-1'].$value),
  'short-2': parseDuration(durationTokens.motion.duration['short-2'].$value),
  'short-3': parseDuration(durationTokens.motion.duration['short-3'].$value),
  'short-4': parseDuration(durationTokens.motion.duration['short-4'].$value),
  'medium-1': parseDuration(durationTokens.motion.duration['medium-1'].$value),
  'medium-2': parseDuration(durationTokens.motion.duration['medium-2'].$value),
  'medium-3': parseDuration(durationTokens.motion.duration['medium-3'].$value),
  'medium-4': parseDuration(durationTokens.motion.duration['medium-4'].$value),
  'long-1': parseDuration(durationTokens.motion.duration['long-1'].$value),
  'long-2': parseDuration(durationTokens.motion.duration['long-2'].$value),
  'long-3': parseDuration(durationTokens.motion.duration['long-3'].$value),
  'long-4': parseDuration(durationTokens.motion.duration['long-4'].$value),
} as const;

export type DurationToken = keyof typeof duration;

// ============================================
// Easing Tokens
// Imported from tokens/easing.tokens.json
// ============================================

// Build easing functions from token cubicBezier values
const buildEasing = (bezier: readonly [number, number, number, number]) =>
  Easing.bezier(bezier[0], bezier[1], bezier[2], bezier[3]);

export const easing = {
  standard: buildEasing(easingTokens.motion.easing.standard.$value as [number, number, number, number]),
  emphasized: buildEasing(easingTokens.motion.easing.emphasized.$value as [number, number, number, number]),
  'emphasized-decelerate': buildEasing(easingTokens.motion.easing['emphasized-decelerate'].$value as [number, number, number, number]),
  'emphasized-accelerate': buildEasing(easingTokens.motion.easing['emphasized-accelerate'].$value as [number, number, number, number]),
  'standard-decelerate': buildEasing(easingTokens.motion.easing['standard-decelerate'].$value as [number, number, number, number]),
  'standard-accelerate': buildEasing(easingTokens.motion.easing['standard-accelerate'].$value as [number, number, number, number]),
  linear: buildEasing(easingTokens.motion.easing.linear.$value as [number, number, number, number]),
} as const;

export type EasingToken = keyof typeof easing;

// ============================================
// Spring Tokens
// Imported from tokens/easing.tokens.json (spring section)
// ============================================

export const springConfig = {
  standard: easingTokens.motion.spring['spring-standard'].$value as { damping: number; stiffness: number; mass: number },
  snappy: easingTokens.motion.spring['spring-snappy'].$value as { damping: number; stiffness: number; mass: number },
  bouncy: easingTokens.motion.spring['spring-bouncy'].$value as { damping: number; stiffness: number; mass: number },
  gentle: easingTokens.motion.spring['spring-gentle'].$value as { damping: number; stiffness: number; mass: number },
  enter: easingTokens.motion.spring['spring-enter'].$value as { damping: number; stiffness: number; mass: number },
} as const;

export type SpringToken = keyof typeof springConfig;

// ============================================
// Utility Functions
// ============================================

/**
 * Convert milliseconds to frames
 */
export const msToFrames = (ms: number, fps: number = 30): number => {
  return Math.round((ms / 1000) * fps);
};

/**
 * Get duration in frames from token
 */
export const getDurationFrames = (
  token: DurationToken,
  fps: number = 30
): number => {
  return msToFrames(duration[token], fps);
};

// ============================================
// Interpolation Helpers
// ============================================

interface InterpolateOptions {
  frame: number;
  fps?: number;
  duration?: DurationToken;
  easing?: EasingToken;
  delay?: number;
  from?: number;
  to?: number;
}

/**
 * M3-styled interpolate with tokens
 */
export const m3Interpolate = ({
  frame,
  fps = 30,
  duration: durationToken = 'medium-1',
  easing: easingToken = 'emphasized-decelerate',
  delay = 0,
  from = 0,
  to = 1,
}: InterpolateOptions): number => {
  const durationFrames = getDurationFrames(durationToken, fps);
  const easingFn = easing[easingToken];

  return interpolate(
    frame - delay,
    [0, durationFrames],
    [from, to],
    {
      easing: easingFn,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );
};

/**
 * Fade in animation
 */
export const fadeIn = (
  frame: number,
  fps: number = 30,
  delay: number = 0
): number => {
  return m3Interpolate({
    frame,
    fps,
    duration: 'medium-1',
    easing: 'emphasized-decelerate',
    delay,
    from: 0,
    to: 1,
  });
};

/**
 * Fade out animation
 */
export const fadeOut = (
  frame: number,
  fps: number = 30,
  delay: number = 0
): number => {
  return m3Interpolate({
    frame,
    fps,
    duration: 'short-4',
    easing: 'emphasized-accelerate',
    delay,
    from: 1,
    to: 0,
  });
};

/**
 * Slide up animation
 */
export const slideUp = (
  frame: number,
  fps: number = 30,
  delay: number = 0,
  distance: number = 20
): number => {
  return m3Interpolate({
    frame,
    fps,
    duration: 'medium-1',
    easing: 'emphasized-decelerate',
    delay,
    from: distance,
    to: 0,
  });
};

// ============================================
// Spring Helpers
// ============================================

interface SpringOptions {
  frame: number;
  fps: number;
  config?: SpringToken;
  delay?: number;
  from?: number;
  to?: number;
}

/**
 * M3-styled spring animation
 */
export const m3Spring = ({
  frame,
  fps,
  config: configToken = 'enter',
  delay = 0,
  from = 0,
  to = 1,
}: SpringOptions): number => {
  return spring({
    frame: frame - delay,
    fps,
    config: springConfig[configToken],
    from,
    to,
  });
};

// ============================================
// Stagger Utilities (M3 Compliant)
// ============================================

// M3-compliant stagger values (capped at 20ms for production UI)
const parseStaggerMs = (value: string): number => parseInt(value.replace('ms', ''), 10);

export const staggerMs = {
  micro: parseStaggerMs(sequencingTokens.motion.sequencing.stagger.micro.$value),  // 10ms
  small: parseStaggerMs(sequencingTokens.motion.sequencing.stagger.small.$value),  // 15ms
  medium: parseStaggerMs(sequencingTokens.motion.sequencing.stagger.medium.$value), // 20ms (M3 max)
  large: parseStaggerMs(sequencingTokens.motion.sequencing.stagger.large.$value),   // 20ms (capped)
} as const;

// M3 choreography constants
export const choreography = {
  maxTotalDurationMs: 500, // No sequence exceeds 500ms
  enterExitRatio: 0.7,     // Exit = Enter × 0.7
} as const;

/**
 * Calculate stagger delay for an index (M3 compliant)
 */
export const getStaggerDelay = (
  index: number,
  staggerMs: number = 20, // M3 max
  fps: number = 30
): number => {
  return msToFrames(index * staggerMs, fps);
};

/**
 * Get adaptive stagger based on item count (M3 capped)
 */
export const getAdaptiveStagger = (
  itemCount: number,
  maxTotalMs: number = 500, // M3 max total duration
  fps: number = 30
): number => {
  const minDelayMs = 10;  // M3 micro stagger
  const maxDelayMs = 20;  // M3 max stagger
  const calculatedMs = maxTotalMs / itemCount;
  const delayMs = Math.max(minDelayMs, Math.min(maxDelayMs, calculatedMs));
  return msToFrames(delayMs, fps);
};

// ============================================
// Container Transform Cross-Fade Timing
// ============================================

/**
 * Get cross-fade timing for container transform
 * Old content fades 0-100ms, new content fades 100-300ms
 */
export const containerTransformCrossFade = {
  oldContent: {
    startFrame: (fps: number) => 0,
    endFrame: (fps: number) => msToFrames(100, fps),
    durationFrames: (fps: number) => msToFrames(100, fps),
  },
  newContent: {
    startFrame: (fps: number) => msToFrames(100, fps),
    endFrame: (fps: number) => msToFrames(300, fps),
    durationFrames: (fps: number) => msToFrames(200, fps),
  },
} as const;

// ============================================
// Entrance Intensity Presets
// ============================================

export const entranceIntensity = {
  emphasized: {
    scaleStart: 0,
    scaleEnd: 1,
    opacityStart: 0,
    translateY: 32,
    durationToken: 'medium-2' as DurationToken,
    easingToken: 'emphasized-decelerate' as EasingToken,
  },
  standard: {
    scaleStart: 0.95,
    scaleEnd: 1,
    opacityStart: 0,
    translateY: 8,
    durationToken: 'short-4' as DurationToken,
    easingToken: 'standard-decelerate' as EasingToken,
  },
  subtle: {
    scaleStart: 1,
    scaleEnd: 1,
    opacityStart: 0,
    translateY: 0,
    durationToken: 'short-3' as DurationToken,
    easingToken: 'standard-decelerate' as EasingToken,
  },
} as const;

export type EntranceIntensity = keyof typeof entranceIntensity;

/**
 * Get entrance animation values
 */
export const getEntranceAnimation = (
  frame: number,
  fps: number = 30,
  intensity: EntranceIntensity = 'standard',
  delay: number = 0
) => {
  const config = entranceIntensity[intensity];
  const durationFrames = getDurationFrames(config.durationToken, fps);
  const easingFn = easing[config.easingToken];

  const progress = interpolate(
    frame - delay,
    [0, durationFrames],
    [0, 1],
    { easing: easingFn, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  return {
    opacity: interpolate(progress, [0, 1], [config.opacityStart, 1]),
    scale: interpolate(progress, [0, 1], [config.scaleStart, config.scaleEnd]),
    translateY: interpolate(progress, [0, 1], [config.translateY, 0]),
  };
};

// ============================================
// Platform Motion Levels
// ============================================

export const motionLevelMultiplier = {
  'L1-none': 0,
  'L2-simplified': 0.5,
  'L3-full': 1.0,
  'L4-enhanced': 1.2,
} as const;

export type MotionLevel = keyof typeof motionLevelMultiplier;

/**
 * Apply motion level to duration
 */
export const applyMotionLevel = (
  baseDurationMs: number,
  level: MotionLevel = 'L3-full'
): number => {
  return Math.round(baseDurationMs * motionLevelMultiplier[level]);
};

// ============================================
// Scene Timing Helpers (Fix for beginning gap)
// ============================================

export type IntroType = 'immediate' | 'short' | 'standard';

/**
 * Get the frame where content should start appearing.
 * Default to 'immediate' (0 frames) to avoid dead air at video start.
 */
export const getContentStartFrame = (
  introType: IntroType = 'immediate',
  fps: number = 30
): number => {
  const introFrames: Record<IntroType, number> = {
    immediate: 0,     // No gap - content starts immediately
    short: msToFrames(200, fps),  // 200ms pause (6 frames at 30fps)
    standard: msToFrames(500, fps) // 500ms pause (15 frames at 30fps)
  };
  return introFrames[introType];
};

/**
 * Get recommended intro type based on context
 */
export const getRecommendedIntroType = (context: {
  isFirstScene?: boolean;
  hasPrecedingAudio?: boolean;
  dramaticPause?: boolean;
}): IntroType => {
  // Default to immediate for most content
  if (context.isFirstScene && !context.dramaticPause) {
    return 'immediate';
  }
  if (context.hasPrecedingAudio) {
    return 'short';
  }
  if (context.dramaticPause) {
    return 'standard';
  }
  return 'immediate';
};

// ============================================
// Video-Specific Transition Durations
// ============================================

/**
 * Video transitions are shorter than web transitions for better pacing.
 * Web users wait for responses; video viewers expect quick cuts.
 */
export const videoTransition = {
  crossfade: {
    duration: 100,  // 3 frames at 30fps
    frames: (fps: number = 30) => msToFrames(100, fps),
    overlap: 2      // 2 frames overlap for smooth blend
  },
  cut: {
    duration: 0,    // Instant cut
    frames: () => 0
  },
  dissolve: {
    duration: 150,  // 5 frames at 30fps
    frames: (fps: number = 30) => msToFrames(150, fps),
    type: 'opacity' as const // Pure opacity, NOT pixel dissolve
  },
  wipe: {
    duration: 200,  // 6 frames at 30fps
    frames: (fps: number = 30) => msToFrames(200, fps),
    direction: 'left' as 'left' | 'right' | 'up' | 'down'
  },
  // Scene transition (between distinct scenes)
  scene: {
    duration: 150,
    frames: (fps: number = 30) => msToFrames(150, fps),
    type: 'crossfade' as const
  }
} as const;

/**
 * Get video transition frames - use these instead of web durations
 */
export const getVideoTransitionFrames = (
  type: keyof typeof videoTransition,
  fps: number = 30
): number => {
  return videoTransition[type].frames(fps);
};

// ============================================
// Typography Sizing for Video
// ============================================

export interface VideoTypographyConfig {
  baseSize: number;
  minSize: number;
  scaleWithWidth: boolean;
}

export const videoTypography = {
  title: {
    baseSize: 80,
    minSize: 48,
    scaleWithWidth: true
  },
  subtitle: {
    baseSize: 32,
    minSize: 24,
    scaleWithWidth: true
  },
  lowerThirdName: {
    baseSize: 28,
    minSize: 20,
    scaleWithWidth: true
  },
  lowerThirdTitle: {
    baseSize: 18,
    minSize: 14,
    scaleWithWidth: true
  },
  body: {
    baseSize: 24,
    minSize: 18,
    scaleWithWidth: true
  },
  caption: {
    baseSize: 16,
    minSize: 14,
    scaleWithWidth: false
  }
} as const;

/**
 * Calculate responsive font size based on video dimensions.
 * Uses 1920px as the baseline width (1080p).
 */
export const getResponsiveFontSize = (
  type: keyof typeof videoTypography,
  videoWidth: number = 1920
): number => {
  const config = videoTypography[type];
  const baselineWidth = 1920; // 1080p baseline

  if (!config.scaleWithWidth) {
    return config.baseSize;
  }

  const scale = videoWidth / baselineWidth;
  const scaledSize = Math.round(config.baseSize * scale);

  return Math.max(config.minSize, scaledSize);
};

/**
 * Get all typography sizes for a given video width
 */
export const getVideoTypographySizes = (videoWidth: number = 1920) => ({
  title: getResponsiveFontSize('title', videoWidth),
  subtitle: getResponsiveFontSize('subtitle', videoWidth),
  lowerThirdName: getResponsiveFontSize('lowerThirdName', videoWidth),
  lowerThirdTitle: getResponsiveFontSize('lowerThirdTitle', videoWidth),
  body: getResponsiveFontSize('body', videoWidth),
  caption: getResponsiveFontSize('caption', videoWidth)
});

// ============================================
// Celebration Effect Guards
// ============================================

/**
 * Valid contexts for celebration effects.
 * Celebration should NEVER auto-trigger on scene transitions.
 */
export const celebrationContexts = [
  'milestone',
  'achievement',
  'completion',
  'success',
  'level-up',
  'unlock'
] as const;

export type CelebrationContext = typeof celebrationContexts[number];

/**
 * Check if celebration effect should be triggered.
 * Returns false for anything that's not an explicit celebration context.
 */
export const shouldTriggerCelebration = (
  context: string,
  explicitlyRequested: boolean = false
): boolean => {
  // Only trigger if explicitly requested AND in valid context
  if (!explicitlyRequested) {
    return false;
  }
  return celebrationContexts.includes(context as CelebrationContext);
};
