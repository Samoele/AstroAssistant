import React, { useEffect, useRef, useState } from 'react';
import type { AvatarEmotion, AvatarAnimation } from '../types/avatar';

interface AvatarProps {
  emotion: AvatarEmotion;
  animation: AvatarAnimation;
  width?: number;
  height?: number;
}

const SPRITE_CONFIG = {
  src: '/sprites/penguin-sprites.png',
  frameWidth: 64,
  frameHeight: 64,
  fps: 6,
};

const ROW_MAPPING: Record<AvatarEmotion, number> = {
  neutral: 0,
  happy: 1,
  grumpy: 2,
  excited: 3,
  sad: 4,
  thinking: 5,
};

const ANIMATION_FRAMES: Record<AvatarAnimation, number[]> = {
  idle: [0, 1],
  talking: [0, 2, 3, 2],
  reacting: [0, 1, 2, 3, 2, 1],
};

export default function AvatarCanvas({
  emotion,
  animation,
  width = 144,
  height = 144,
}: AvatarProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [spriteImage, setSpriteImage] = useState<HTMLImageElement | null>(null);

  // 1. Reliable Image Loading with Error Detection
  useEffect(() => {
    const img = new Image();
    img.src = SPRITE_CONFIG.src;

    img.onload = () => {
      console.log('✅ Sprite sheet loaded successfully:', img.naturalWidth, 'x', img.naturalHeight);
      setSpriteImage(img);
    };

    img.onerror = () => {
      console.error(
        `❌ Failed to load sprite sheet from "${SPRITE_CONFIG.src}". Make sure the file exists at frontend/public/penguin-sprites.png`
      );
    };
  }, []);

  // 2. Animation Loop (Only runs once spriteImage is ready)
  useEffect(() => {
    if (!spriteImage) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.imageSmoothingEnabled = false;

    let animationFrameId: number;
    let lastTimestamp = 0;
    let currentFrameIndex = 0;

    const frameSequence = ANIMATION_FRAMES[animation] || [0];
    const targetRow = ROW_MAPPING[emotion] ?? 0;
    const intervalMs = 1000 / SPRITE_CONFIG.fps;

    const render = (timestamp: number) => {
      if (!lastTimestamp) lastTimestamp = timestamp;
      const elapsed = timestamp - lastTimestamp;

      if (elapsed >= intervalMs) {
        currentFrameIndex = (currentFrameIndex + 1) % frameSequence.length;
        lastTimestamp = timestamp - (elapsed % intervalMs);
      }

      const col = frameSequence[currentFrameIndex];
      const sx = col * SPRITE_CONFIG.frameWidth;
      const sy = targetRow * SPRITE_CONFIG.frameHeight;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      ctx.drawImage(
        spriteImage,
        Math.floor(sx),
        Math.floor(sy),
        SPRITE_CONFIG.frameWidth,
        SPRITE_CONFIG.frameHeight,
        0,
        0,
        canvas.width,
        canvas.height
      );

      animationFrameId = requestAnimationFrame(render);
    };

    animationFrameId = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [spriteImage, emotion, animation]);

  return (
    <div
      style={{ width, height }}
      className="relative flex items-center justify-center select-none bg-slate-950/40 rounded-xl border border-slate-800/60"
    >
      <canvas
        ref={canvasRef}
        width={SPRITE_CONFIG.frameWidth}
        height={SPRITE_CONFIG.frameHeight}
        className="w-full h-full [image-rendering:pixelated]"
      />
      {!spriteImage && (
        <span className="absolute text-[10px] text-slate-500 font-mono">
          Loading sprite...
        </span>
      )}
    </div>
  );
}