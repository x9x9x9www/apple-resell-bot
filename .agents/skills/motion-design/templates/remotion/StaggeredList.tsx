/**
 * Remotion Staggered List Template
 * M3 pattern for sequential item entrances
 *
 * Token References:
 * - Duration per item: {motion.duration.medium-1} (250ms)
 * - Stagger delay: 50ms (adaptive based on count)
 * - Easing: {motion.easing.emphasized-decelerate}
 *
 * @see https://m3.material.io/styles/motion/choreography
 */

import React from 'react';
import {
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from 'remotion';

// M3 Motion Tokens
const easing = {
  enter: Easing.bezier(0.05, 0.7, 0.1, 1),
};

const msToFrames = (ms: number, fps: number) => Math.round((ms / 1000) * fps);

interface StaggeredListProps {
  /** Array of items to render */
  items: React.ReactNode[];
  /** Duration per item in milliseconds (default: 250ms / medium-1) */
  itemDurationMs?: number;
  /** Base stagger delay between items in milliseconds (default: 50ms) */
  staggerMs?: number;
  /** Maximum total stagger time in milliseconds (default: 800ms) */
  maxTotalStaggerMs?: number;
  /** Frame at which animation begins (default: 0) */
  startFrame?: number;
  /** Animation direction: 'up', 'down', 'left', 'right', 'scale' */
  direction?: 'up' | 'down' | 'left' | 'right' | 'scale';
  /** Distance to travel in pixels (default: 16) */
  distance?: number;
  /** Custom render function for each item */
  renderItem?: (item: React.ReactNode, index: number, style: React.CSSProperties) => React.ReactNode;
}

/**
 * Staggered List Animation
 *
 * M3 choreography pattern where list items enter sequentially with
 * overlapping animations. Uses adaptive stagger that adjusts delay
 * based on item count to maintain consistent total animation time.
 *
 * Adaptive stagger formula:
 * delay = min(50ms, max(25ms, maxTotalMs / itemCount))
 *
 * Use for: list views, grid items, navigation menus, card collections
 */
export const StaggeredList: React.FC<StaggeredListProps> = ({
  items,
  itemDurationMs = 250,
  staggerMs = 50,
  maxTotalStaggerMs = 800,
  startFrame = 0,
  direction = 'up',
  distance = 16,
  renderItem,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Calculate adaptive stagger
  const minDelay = 25;
  const maxDelay = staggerMs;
  const calculatedDelay = maxTotalStaggerMs / items.length;
  const adaptiveStagger = Math.max(minDelay, Math.min(maxDelay, calculatedDelay));
  const staggerFrames = msToFrames(adaptiveStagger, fps);
  const itemDurationFrames = msToFrames(itemDurationMs, fps);

  // Get transform based on direction
  const getInitialTransform = () => {
    switch (direction) {
      case 'up': return { x: 0, y: distance, scale: 1 };
      case 'down': return { x: 0, y: -distance, scale: 1 };
      case 'left': return { x: distance, y: 0, scale: 1 };
      case 'right': return { x: -distance, y: 0, scale: 1 };
      case 'scale': return { x: 0, y: 0, scale: 0.9 };
      default: return { x: 0, y: distance, scale: 1 };
    }
  };

  const initial = getInitialTransform();

  return (
    <>
      {items.map((item, index) => {
        const itemStart = startFrame + (index * staggerFrames);
        const localFrame = frame - itemStart;

        const opacity = interpolate(
          localFrame,
          [0, itemDurationFrames],
          [0, 1],
          {
            easing: easing.enter,
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }
        );

        const x = interpolate(
          localFrame,
          [0, itemDurationFrames],
          [initial.x, 0],
          {
            easing: easing.enter,
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }
        );

        const y = interpolate(
          localFrame,
          [0, itemDurationFrames],
          [initial.y, 0],
          {
            easing: easing.enter,
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }
        );

        const scale = interpolate(
          localFrame,
          [0, itemDurationFrames],
          [initial.scale, 1],
          {
            easing: easing.enter,
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }
        );

        const style: React.CSSProperties = {
          opacity,
          transform: `translate(${x}px, ${y}px) scale(${scale})`,
        };

        if (renderItem) {
          return renderItem(item, index, style);
        }

        return (
          <div key={index} style={style}>
            {item}
          </div>
        );
      })}
    </>
  );
};

/**
 * Helper hook to get stagger delay for a specific index
 */
export const useStaggerDelay = (
  index: number,
  itemCount: number,
  staggerMs: number = 50,
  maxTotalMs: number = 800,
  fps: number = 30
): number => {
  const minDelay = 25;
  const calculatedDelay = maxTotalMs / itemCount;
  const adaptiveStagger = Math.max(minDelay, Math.min(staggerMs, calculatedDelay));
  return msToFrames(index * adaptiveStagger, fps);
};

export default StaggeredList;
