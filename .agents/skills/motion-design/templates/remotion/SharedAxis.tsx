/**
 * Remotion Shared Axis Transition Template
 * M3 transition pattern for directional navigation
 *
 * Token References:
 * - Duration: {motion.duration.medium-2} (300ms)
 * - Enter Easing: {motion.easing.emphasized-decelerate}
 * - Exit Easing: {motion.easing.emphasized-accelerate}
 *
 * @see https://m3.material.io/styles/motion/transitions/transition-patterns
 */

import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from 'remotion';

// M3 Motion Tokens
const easing = {
  enter: Easing.bezier(0.05, 0.7, 0.1, 1),
  exit: Easing.bezier(0.3, 0, 0.8, 0.15),
};

const msToFrames = (ms: number, fps: number) => Math.round((ms / 1000) * fps);

type Axis = 'x' | 'y' | 'z';
type Direction = 'forward' | 'backward';

interface SharedAxisProps {
  /** Axis of motion: x (horizontal), y (vertical), z (depth) */
  axis?: Axis;
  /** Direction: forward or backward along the axis */
  direction?: Direction;
  /** Duration of transition in milliseconds (default: 300ms) */
  durationMs?: number;
  /** Outgoing content */
  outgoing: React.ReactNode;
  /** Incoming content */
  incoming: React.ReactNode;
  /** Frame at which transition begins (default: 0) */
  transitionStart?: number;
}

/**
 * Shared Axis Transition
 *
 * M3 pattern where elements move along a shared spatial axis.
 * Creates a sense of navigation direction (forward/back, up/down).
 *
 * - X axis: horizontal navigation (forward = right, backward = left)
 * - Y axis: vertical navigation (forward = up, backward = down)
 * - Z axis: depth navigation (forward = zoom in, backward = zoom out)
 *
 * Use for: navigation hierarchy, stepper progress, list detail views
 */
export const SharedAxis: React.FC<SharedAxisProps> = ({
  axis = 'x',
  direction = 'forward',
  durationMs = 300,
  outgoing,
  incoming,
  transitionStart = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const transitionFrames = msToFrames(durationMs, fps);
  const localFrame = frame - transitionStart;
  const directionMultiplier = direction === 'forward' ? 1 : -1;

  // Calculate movement distance based on axis
  const getTransform = (progress: number, isOutgoing: boolean) => {
    const offset = isOutgoing
      ? interpolate(progress, [0, 1], [0, -30 * directionMultiplier])
      : interpolate(progress, [0, 1], [30 * directionMultiplier, 0]);

    const scale = isOutgoing
      ? interpolate(progress, [0, 1], [1, 0.8])
      : interpolate(progress, [0, 1], [1.1, 1]);

    switch (axis) {
      case 'x':
        return `translateX(${offset}px)`;
      case 'y':
        return `translateY(${offset}px)`;
      case 'z':
        return `scale(${scale})`;
      default:
        return 'none';
    }
  };

  // Outgoing element
  const outProgress = interpolate(
    localFrame,
    [0, transitionFrames * 0.35],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const outOpacity = interpolate(
    localFrame,
    [0, transitionFrames * 0.35],
    [1, 0],
    {
      easing: easing.exit,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  // Incoming element
  const inProgress = interpolate(
    localFrame,
    [transitionFrames * 0.35, transitionFrames],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const inOpacity = interpolate(
    localFrame,
    [transitionFrames * 0.35, transitionFrames],
    [0, 1],
    {
      easing: easing.enter,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  return (
    <AbsoluteFill>
      {/* Outgoing content */}
      <AbsoluteFill
        style={{
          opacity: outOpacity,
          transform: getTransform(outProgress, true),
        }}
      >
        {outgoing}
      </AbsoluteFill>

      {/* Incoming content */}
      <AbsoluteFill
        style={{
          opacity: inOpacity,
          transform: getTransform(inProgress, false),
        }}
      >
        {incoming}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export default SharedAxis;
