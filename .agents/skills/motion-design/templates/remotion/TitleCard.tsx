/**
 * Remotion Title Card Template
 * Uses M3 motion tokens for professional title animations
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
};

const msToFrames = (ms: number, fps: number) => Math.round((ms / 1000) * fps);

// Video Typography Config
const videoTypography = {
  title: { baseSize: 80, minSize: 48 },
  subtitle: { baseSize: 32, minSize: 24 }
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

interface TitleCardProps {
  title: string;
  subtitle?: string;
  backgroundColor?: string;
  textColor?: string;
  /** Override title font size (uses responsive sizing if not set) */
  titleSize?: number;
  /** Override subtitle font size (uses responsive sizing if not set) */
  subtitleSize?: number;
  /** Minimum title size (default: 48px) */
  minTitleSize?: number;
  /** Minimum subtitle size (default: 24px) */
  minSubtitleSize?: number;
  /** Start frame for content (default: 0 for immediate start) */
  contentStartFrame?: number;
}

export const TitleCard: React.FC<TitleCardProps> = ({
  title,
  subtitle,
  backgroundColor = '#1a1a1a',
  textColor = '#ffffff',
  titleSize,
  subtitleSize,
  minTitleSize = 48,
  minSubtitleSize = 24,
  contentStartFrame = 0, // Default: immediate start (no dead air)
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width } = useVideoConfig();

  // Calculate responsive font sizes
  const actualTitleSize = titleSize ?? getResponsiveSize(
    videoTypography.title.baseSize,
    minTitleSize,
    width
  );
  const actualSubtitleSize = subtitleSize ?? getResponsiveSize(
    videoTypography.subtitle.baseSize,
    minSubtitleSize,
    width
  );

  // Animation timing (M3 tokens) - start from contentStartFrame
  const adjustedFrame = Math.max(0, frame - contentStartFrame);
  const enterDuration = msToFrames(250, fps); // medium-1
  const exitStart = durationInFrames - contentStartFrame - msToFrames(200, fps); // short-4 before end

  // Title animation (uses adjustedFrame for immediate start)
  const titleOpacity = interpolate(
    adjustedFrame,
    [0, enterDuration, exitStart, durationInFrames - contentStartFrame],
    [0, 1, 1, 0],
    {
      easing: easing.enter,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  const titleY = interpolate(
    adjustedFrame,
    [0, enterDuration],
    [20, 0],
    {
      easing: easing.enter,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  // Subtitle animation (staggered by 50ms)
  const subtitleDelay = msToFrames(50, fps);
  const subtitleOpacity = interpolate(
    adjustedFrame - subtitleDelay,
    [0, enterDuration, exitStart - subtitleDelay, durationInFrames - contentStartFrame - subtitleDelay],
    [0, 1, 1, 0],
    {
      easing: easing.enter,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  const subtitleY = interpolate(
    adjustedFrame - subtitleDelay,
    [0, enterDuration],
    [16, 0],
    {
      easing: easing.enter,
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 16,
        }}
      >
        <h1
          style={{
            fontFamily: 'Inter, system-ui, sans-serif',
            fontSize: actualTitleSize,
            fontWeight: 700,
            color: textColor,
            margin: 0,
            opacity: titleOpacity,
            transform: `translateY(${titleY}px)`,
            // Ensure minimum readable size
            lineHeight: 1.2,
          }}
        >
          {title}
        </h1>
        {subtitle && (
          <p
            style={{
              fontFamily: 'Inter, system-ui, sans-serif',
              fontSize: actualSubtitleSize,
              fontWeight: 400,
              color: textColor,
              margin: 0,
              opacity: subtitleOpacity,
              transform: `translateY(${subtitleY}px)`,
              // Ensure minimum readable size
              lineHeight: 1.4,
            }}
          >
            {subtitle}
          </p>
        )}
      </div>
    </AbsoluteFill>
  );
};

export default TitleCard;
