/**
 * Remotion Lower Third Template
 * Professional lower third with M3 motion tokens
 *
 * Features:
 * - Responsive typography with min/max constraints
 * - Immediate content start (no dead air)
 * - Video-optimized transition durations
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
  standard: Easing.bezier(0.2, 0, 0, 1),
};

const msToFrames = (ms: number, fps: number) => Math.round((ms / 1000) * fps);

// Video Typography Config for Lower Thirds
const videoTypography = {
  name: { baseSize: 28, minSize: 20 },
  title: { baseSize: 18, minSize: 14 }
};

/**
 * Calculate responsive font size based on video width.
 * Uses 1920px as baseline (1080p).
 */
const getResponsiveSize = (
  baseSize: number,
  minSize: number,
  videoWidth: number
): number => {
  const scale = videoWidth / 1920;
  return Math.max(minSize, Math.round(baseSize * scale));
};

interface LowerThirdProps {
  name: string;
  title?: string;
  accentColor?: string;
  backgroundColor?: string;
  textColor?: string;
  /** Override name font size (uses responsive sizing if not set) */
  nameSize?: number;
  /** Override title font size (uses responsive sizing if not set) */
  titleSize?: number;
  /** Minimum name size (default: 20px) */
  minNameSize?: number;
  /** Minimum title size (default: 14px) */
  minTitleSize?: number;
  /** Start frame for content (default: 0 for immediate start) */
  contentStartFrame?: number;
}

export const LowerThird: React.FC<LowerThirdProps> = ({
  name,
  title,
  accentColor = '#6750A4', // M3 primary
  backgroundColor = 'rgba(0, 0, 0, 0.8)',
  textColor = '#ffffff',
  nameSize,
  titleSize,
  minNameSize = 20,
  minTitleSize = 14,
  contentStartFrame = 0, // Default: immediate start (no dead air)
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width } = useVideoConfig();

  // Calculate responsive font sizes
  const actualNameSize = nameSize ?? getResponsiveSize(
    videoTypography.name.baseSize,
    minNameSize,
    width
  );
  const actualTitleSize = titleSize ?? getResponsiveSize(
    videoTypography.title.baseSize,
    minTitleSize,
    width
  );

  // Animation timing - use video-optimized durations (150ms instead of 300ms)
  const adjustedFrame = Math.max(0, frame - contentStartFrame);
  const enterDuration = msToFrames(150, fps); // video scene-transition (faster than web)
  const exitStart = durationInFrames - contentStartFrame - msToFrames(150, fps);

  // Background bar animation (using adjustedFrame for immediate start)
  const barWidth = interpolate(
    adjustedFrame,
    [0, enterDuration, exitStart, durationInFrames - contentStartFrame],
    [0, 100, 100, 0],
    {
      easing: easing.enter,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  // Accent line animation (reduced delays for video pacing)
  const accentDelay = msToFrames(50, fps); // Reduced from 100ms
  const accentWidth = interpolate(
    adjustedFrame - accentDelay,
    [0, msToFrames(100, fps)], // Reduced from 200ms
    [0, 4],
    {
      easing: easing.enter,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  // Name animation (reduced stagger for faster video pacing)
  const nameDelay = msToFrames(75, fps); // Reduced from 150ms
  const nameOpacity = interpolate(
    adjustedFrame - nameDelay,
    [0, msToFrames(100, fps), exitStart - nameDelay, durationInFrames - contentStartFrame - nameDelay],
    [0, 1, 1, 0],
    {
      easing: easing.enter,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  const nameX = interpolate(
    adjustedFrame - nameDelay,
    [0, msToFrames(100, fps)], // Reduced from 200ms
    [-20, 0],
    {
      easing: easing.enter,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  // Title animation (reduced stagger for faster video pacing)
  const titleDelay = msToFrames(100, fps); // Reduced from 200ms
  const titleOpacity = interpolate(
    adjustedFrame - titleDelay,
    [0, msToFrames(100, fps), exitStart - titleDelay, durationInFrames - contentStartFrame - titleDelay],
    [0, 1, 1, 0],
    {
      easing: easing.enter,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  const titleX = interpolate(
    adjustedFrame - titleDelay,
    [0, msToFrames(100, fps)], // Reduced from 200ms
    [-20, 0],
    {
      easing: easing.enter,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  return (
    <AbsoluteFill>
      <div
        style={{
          position: 'absolute',
          bottom: 80,
          left: 80,
          display: 'flex',
          alignItems: 'stretch',
        }}
      >
        {/* Accent line */}
        <div
          style={{
            width: accentWidth,
            backgroundColor: accentColor,
            marginRight: 16,
          }}
        />

        {/* Content container */}
        <div
          style={{
            backgroundColor,
            padding: '16px 24px',
            width: `${barWidth}%`,
            minWidth: barWidth > 0 ? 300 : 0,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              fontFamily: 'Inter, system-ui, sans-serif',
              fontSize: actualNameSize,
              fontWeight: 600,
              color: textColor,
              opacity: nameOpacity,
              transform: `translateX(${nameX}px)`,
              whiteSpace: 'nowrap',
              lineHeight: 1.3,
            }}
          >
            {name}
          </div>
          {title && (
            <div
              style={{
                fontFamily: 'Inter, system-ui, sans-serif',
                fontSize: actualTitleSize,
                fontWeight: 400,
                color: textColor,
                opacity: titleOpacity * 0.8,
                transform: `translateX(${titleX}px)`,
                marginTop: 4,
                whiteSpace: 'nowrap',
                lineHeight: 1.4,
              }}
            >
              {title}
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default LowerThird;
