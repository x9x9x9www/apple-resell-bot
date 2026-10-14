/**
 * Remotion Fade Through Transition Template
 * M3 transition pattern where both elements fade simultaneously
 *
 * Token References:
 * - Duration: {motion.duration.medium-2} (300ms)
 * - Easing: {motion.easing.standard}
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
  standard: Easing.bezier(0.2, 0, 0, 1),
};

const msToFrames = (ms: number, fps: number) => Math.round((ms / 1000) * fps);

interface FadeThroughProps {
  /** Duration of transition in milliseconds (default: 300ms / medium-2) */
  durationMs?: number;
  /** Outgoing content */
  outgoing: React.ReactNode;
  /** Incoming content */
  incoming: React.ReactNode;
  /** Frame at which transition begins (default: 0) */
  transitionStart?: number;
}

/**
 * Fade Through Transition
 *
 * M3 pattern where the outgoing element fades out while the incoming
 * element fades in. Both elements cross at 35% opacity (not 50%) for
 * a smoother visual transition.
 *
 * Use for: route changes, tab switches, carousel content
 */
export const FadeThrough: React.FC<FadeThroughProps> = ({
  durationMs = 300,
  outgoing,
  incoming,
  transitionStart = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const transitionFrames = msToFrames(durationMs, fps);
  const localFrame = frame - transitionStart;

  // Outgoing: fades out completely in first 35% of transition
  const outgoingOpacity = interpolate(
    localFrame,
    [0, transitionFrames * 0.35],
    [1, 0],
    {
      easing: easing.standard,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  // Incoming: fades in from 35% to 100% of transition
  const incomingOpacity = interpolate(
    localFrame,
    [transitionFrames * 0.35, transitionFrames],
    [0, 1],
    {
      easing: easing.standard,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  // Scale: incoming starts slightly smaller
  const incomingScale = interpolate(
    localFrame,
    [transitionFrames * 0.35, transitionFrames],
    [0.92, 1],
    {
      easing: easing.standard,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  return (
    <AbsoluteFill>
      {/* Outgoing content */}
      <AbsoluteFill style={{ opacity: outgoingOpacity }}>
        {outgoing}
      </AbsoluteFill>

      {/* Incoming content */}
      <AbsoluteFill
        style={{
          opacity: incomingOpacity,
          transform: `scale(${incomingScale})`,
        }}
      >
        {incoming}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export default FadeThrough;
