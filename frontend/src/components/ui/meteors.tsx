import React from 'react';

interface MeteorsProps {
  number?: number;
  minDelay?: number;
  maxDelay?: number;
  minDuration?: number;
  maxDuration?: number;
  className?: string;
}

export const Meteors: React.FC<MeteorsProps> = ({
  number = 20,
  minDelay = 0.2,
  maxDelay = 1.2,
  minDuration = 2,
  maxDuration = 10,
  className = '',
}) => {
  const meteors = Array.from({ length: number }, (_, idx) => ({
    id: idx,
    // Spread meteors across the full width plus some overflow for better coverage
    left: `${Math.random() * 120 - 10}%`, // -10% to 110% for better coverage
    top: `${Math.random() * 100}%`, // Random vertical position
    animationDelay: `${Math.random() * (maxDelay - minDelay) + minDelay}s`,
    animationDuration: `${Math.random() * (maxDuration - minDuration) + minDuration}s`,
  }));

  return (
    <>
      {meteors.map(meteor => (
        <span
          key={meteor.id}
          className={`animate-meteor-effect absolute h-0.5 w-0.5 rounded-[9999px] bg-slate-500 shadow-[0_0_0_1px_#ffffff10] rotate-[215deg] pointer-events-none overflow-visible ${className}`}
          style={{
            top: meteor.top,
            left: meteor.left,
            animationDelay: meteor.animationDelay,
            animationDuration: meteor.animationDuration,
          }}
        >
          {/* Enhanced meteor tail with better mobile visibility */}
          <div className="absolute top-1/2 -z-10 h-[1px] w-[70px] sm:w-[70px] -translate-y-1/2 bg-gradient-to-r from-slate-500 to-transparent" />
          {/* Additional glow effect for better visibility */}
          <div className="absolute top-1/2 -z-20 h-[2px] w-[20px] sm:w-[30px] -translate-y-1/2 bg-gradient-to-r from-slate-400/50 to-transparent blur-[0.5px]" />
        </span>
      ))}
    </>
  );
};
