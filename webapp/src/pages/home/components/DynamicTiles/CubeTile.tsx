import { useState, useEffect, useRef, useCallback } from 'react';

interface CubeTileProps {
  images: string[];
  interval: number;
  autoRotate?: boolean;
  colSpan: number;
  rowSpan: number;
  onClick?: () => void;
}

export const CubeTile = ({ images, interval, autoRotate = true, colSpan, rowSpan, onClick }: CubeTileProps) => {
  const count = images.length;
  const containerRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Snapped angle (multiples of 90°)
  const [snappedAngle, setSnappedAngle] = useState(0);
  // Drag offset in degrees (realtime during touch)
  const [dragOffset, setDragOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  // Animating = CSS transition active (snap or auto-rotate)
  const [animating, setAnimating] = useState(false);
  const [size, setSize] = useState({ w: 0, h: 0 });

  // Touch tracking refs
  const touchStartX = useRef(0);
  const touchCurrentX = useRef(0);
  const touchStartTime = useRef(0);
  const hasMoved = useRef(false);

  // Measure container so we know translateZ depth
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const measure = () => setSize({ w: el.offsetWidth, h: el.offsetHeight });
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const half = size.w / 2; // depth for Y-axis rotation

  // Snap to nearest 90° face based on current total angle
  const snapToNearest = useCallback((totalAngle: number) => {
    const snapped = Math.round(totalAngle / 90) * 90;
    setSnappedAngle(snapped);
    setDragOffset(0);
    setIsDragging(false);
    setAnimating(true);
  }, []);

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const startTimer = useCallback(() => {
    clearTimer();
    if (!autoRotate || count < 2) return;
    timerRef.current = setInterval(() => {
      setAnimating(true);
      setSnappedAngle(prev => prev - 90);
    }, interval * 1000);
  }, [autoRotate, count, interval, clearTimer]);

  // Auto-rotate
  useEffect(() => {
    startTimer();
    return clearTimer;
  }, [startTimer, clearTimer]);

  const handleTransitionEnd = () => setAnimating(false);

  // --- Touch handlers: drag-follow ---
  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
    touchCurrentX.current = e.touches[0].clientX;
    touchStartTime.current = Date.now();
    hasMoved.current = false;
    clearTimer();
    setIsDragging(true);
    setDragOffset(0);
    setAnimating(false);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging || size.w === 0) return;
    touchCurrentX.current = e.touches[0].clientX;
    const dx = touchCurrentX.current - touchStartX.current;
    if (Math.abs(dx) > 3) hasMoved.current = true;
    // Map pixel movement to degrees: full width = 90°
    const angleDelta = (dx / size.w) * 90;
    setDragOffset(angleDelta);
  };

  const handleTouchEnd = () => {
    if (!isDragging) return;
    const dx = touchCurrentX.current - touchStartX.current;
    const dt = Date.now() - touchStartTime.current;
    const velocity = Math.abs(dx) / Math.max(dt, 1); // px/ms

    const currentTotal = snappedAngle + dragOffset;

    // Fast swipe (velocity > 0.3 px/ms) → go full face in swipe direction
    if (velocity > 0.3 && Math.abs(dx) > 15) {
      const dir = dx > 0 ? 90 : -90;
      snapToNearest(snappedAngle + dir);
    } else {
      // Slow drag — snap to nearest face
      snapToNearest(currentTotal);
    }

    startTimer();
  };

  // Handle click: only fire if not dragged
  const handleClick = () => {
    if (!hasMoved.current && onClick) onClick();
  };

  // Map angle to image index (works for any direction, wraps correctly)
  const faceIndex = (faceAngle: number) => (((-faceAngle / 90) % count) + count) % count;

  // We always render 4 faces of the cube (front, right, back, left)
  const faces = [
    { ry: 0,   label: 'front' },
    { ry: 90,  label: 'right' },
    { ry: 180, label: 'back'  },
    { ry: 270, label: 'left'  },
  ];

  // Total displayed angle
  const displayAngle = snappedAngle + dragOffset;

  // Current face index for dot indicator (use snapped for stable indicator)
  const activeIndex = faceIndex(isDragging ? Math.round(displayAngle / 90) * 90 : snappedAngle);

  // Transition: only during snap/auto-rotate, not during drag
  const useTransition = animating && !isDragging;

  return (
    <div
      ref={containerRef}
      onClick={handleClick}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className="border-2 border-zinc-700 rounded-2xl relative overflow-hidden cursor-pointer shadow-xl select-none"
      style={{
        gridColumn: `span ${colSpan}`,
        gridRow: `span ${rowSpan}`,
        perspective: size.w * 2.5 || 600,
        touchAction: 'pan-y',
      }}
    >
      {half > 0 && (
        <div
          className="absolute inset-0"
          style={{
            transformStyle: 'preserve-3d',
            transition: useTransition ? 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)' : 'none',
            transform: `translateZ(-${half}px) rotateY(${displayAngle}deg)`,
          }}
          onTransitionEnd={handleTransitionEnd}
        >
          {faces.map((face) => {
            const idx = faceIndex(-face.ry);
            const imgIdx = idx % count;
            return (
              <div
                key={face.label}
                className="absolute inset-0 bg-cover bg-center"
                style={{
                  backgroundImage: `url(${images[imgIdx]})`,
                  backfaceVisibility: 'hidden',
                  transform: `rotateY(${face.ry}deg) translateZ(${half}px)`,
                }}
              />
            );
          })}
        </div>
      )}

      {/* Dot indicators */}
      {count > 1 && (
        <div className="absolute bottom-2 left-0 right-0 flex justify-center gap-1.5 z-20">
          {images.map((_, i) => (
            <div
              key={i}
              className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
                i === activeIndex ? 'bg-white scale-125' : 'bg-white/40'
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
};
