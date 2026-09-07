import { useEffect, useRef, useState } from 'react';
import { motion, useAnimationControls } from 'framer-motion';
import type { AvatarEmotion, AvatarAnimation } from '../types/avatar';

interface AvatarCanvasProps {
  emotion: AvatarEmotion;
  animation: AvatarAnimation;
  width?: number;
  height?: number;
}

const ANIMATION_ROW_MAP: Record<AvatarAnimation, number> = {
  idle: 0,
  talking: 1,
  reacting: 2,
};

const COLS = 4;
const ROWS = 3;
// Last column of every row is a dedicated closed-eye frame in the sheet;
// body motion cycles the rest so blinking can be timed independently.
const BLINK_COL = COLS - 1;
const BODY_COLS = COLS - 1;
const FPS = 4;
const BLINK_HOLD_MS = 160;
const BLINK_MIN_GAP_MS = 2200;
const BLINK_MAX_GAP_MS = 5000;

function randomBetween(min: number, max: number) {
  return min + Math.random() * (max - min);
}

export default function AvatarCanvas({
  emotion,
  animation,
  width = 256,
  height = 256,
}: AvatarCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isBlinking, setIsBlinking] = useState(false);
  const popControls = useAnimationControls();

  const spriteSrc = `/sprites/${emotion}.png`;

  useEffect(() => {
    setIsLoaded(false);
    const img = new Image();
    img.src = spriteSrc;

    img.onload = () => {
      imageRef.current = img;
      setIsLoaded(true);
    };

    img.onerror = () => {
      if (img.src !== `${window.location.origin}/sprites/neutral.png`) {
        img.src = '/sprites/neutral.png';
      }
    };
  }, [spriteSrc]);

  // A quick "pop" on state changes reads as a reaction instead of an instant snap.
  useEffect(() => {
    popControls.start({
      scale: [1, 1.06, 1],
      transition: { duration: 0.35, ease: 'easeOut' },
    });
  }, [emotion, animation, popControls]);

  // Blink on its own randomized clock so it lands like a natural tic rather
  // than the fixed once-per-loop cadence the raw frame cycle would produce.
  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;
    let holdId: ReturnType<typeof setTimeout>;

    const scheduleBlink = () => {
      timeoutId = setTimeout(() => {
        setIsBlinking(true);
        holdId = setTimeout(() => {
          setIsBlinking(false);
          scheduleBlink();
        }, BLINK_HOLD_MS);
      }, randomBetween(BLINK_MIN_GAP_MS, BLINK_MAX_GAP_MS));
    };

    scheduleBlink();
    return () => {
      clearTimeout(timeoutId);
      clearTimeout(holdId);
    };
  }, []);

  useEffect(() => {
    if (!isLoaded) return;

    let animationFrameId: number;
    let currentFrame = 0;
    let lastTimestamp = performance.now();
    const frameInterval = 1000 / FPS;

    const render = (now: number) => {
      const canvas = canvasRef.current;
      const ctx = canvas?.getContext('2d');
      const img = imageRef.current;

      if (canvas && ctx && img && img.naturalWidth > 0 && img.naturalHeight > 0) {
        const frameWidth = img.naturalWidth / COLS;
        const frameHeight = img.naturalHeight / ROWS;

        const elapsed = now - lastTimestamp;
        if (elapsed >= frameInterval) {
          currentFrame = (currentFrame + 1) % BODY_COLS;
          lastTimestamp = now - (elapsed % frameInterval);
        }

        const col = isBlinking ? BLINK_COL : currentFrame;
        const sx = col * frameWidth;
        const sy = ANIMATION_ROW_MAP[animation] * frameHeight;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.imageSmoothingEnabled = false;

        ctx.drawImage(
          img,
          Math.floor(sx),
          Math.floor(sy),
          Math.floor(frameWidth),
          Math.floor(frameHeight),
          0,
          0,
          canvas.width,
          canvas.height
        );
      }

      animationFrameId = requestAnimationFrame(render);
    };

    animationFrameId = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isLoaded, animation, isBlinking]);

  return (
    <motion.div
      className="flex items-center justify-center bg-transparent"
      animate={animation === 'idle' ? { y: [0, -3, 0] } : { y: 0 }}
      transition={
        animation === 'idle'
          ? { duration: 2.2, repeat: Infinity, ease: 'easeInOut' }
          : { duration: 0.2 }
      }
    >
      <motion.canvas
        ref={canvasRef}
        animate={popControls}
        width={width}
        height={height}
        style={{
          imageRendering: 'pixelated',
          background: 'transparent',
          opacity: isLoaded ? 1 : 0,
          transition: 'opacity 150ms ease-out',
        }}
      />
    </motion.div>
  );
}
