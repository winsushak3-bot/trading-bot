import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from '../../i18n';
import { contentFade, slideUp } from '../animations';

interface LoadingScreenProps {
  onComplete: () => void;
}

export const LoadingScreen = ({ onComplete }: LoadingScreenProps) => {
  const [progress, setProgress] = useState(0);
  const { t } = useTranslation();
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => onCompleteRef.current(), 150);
          return 100;
        }
        const increment = Math.floor(Math.random() * 10) + 10;
        return Math.min(prev + increment, 100);
      });
    }, 50);

    return () => clearInterval(interval);
  }, []);

  // Сглаженный паттерн "голова и плечи" с кривыми Безье
  const pathDefinition = "M0,100 C10,85 15,70 20,60 C25,50 30,75 35,90 C40,105 45,40 50,20 C55,40 60,105 65,90 C70,75 75,50 80,60 C85,70 90,85 100,100";

  return (
    <motion.div 
      variants={contentFade(0.25)}
      initial="hidden"
      animate="visible"
      exit="hidden"
      className="fixed inset-0 z-50 bg-black flex flex-col items-center justify-center overflow-hidden"
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-zinc-900/40 via-black to-black opacity-50" />
      
      <div className="relative w-full max-w-sm px-10 h-64 flex items-center justify-center z-10">
        <svg 
            className="w-full h-full overflow-visible" 
            viewBox="0 0 100 120" 
            preserveAspectRatio="none"
        >
            <motion.path
                d={pathDefinition}
                fill="none"
                stroke="white"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                initial={{ pathLength: 0, opacity: 0.3 }}
                animate={{ 
                  pathLength: progress / 100, 
                  opacity: [0.3, 1, 0.9, 1],
                }}
                transition={{ 
                  pathLength: { type: "spring", stiffness: 50, damping: 20 },
                  opacity: { duration: 0.8, times: [0, 0.3, 0.6, 1] }
                }}
            />

            <motion.path
                d={`${pathDefinition} L100,150 L0,150 Z`}
                fill="url(#chartGradient)"
                stroke="none"
                initial={{ opacity: 0 }}
                animate={{ opacity: (progress / 100) * 0.6 }}
                transition={{ duration: 0.5 }}
            />

            <defs>
                <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="white" stopOpacity="0.15" />
                    <stop offset="100%" stopColor="white" stopOpacity="0" />
                </linearGradient>
            </defs>
        </svg>
      </div>

      <div className="absolute bottom-16 left-0 right-0 flex flex-col items-center z-20">
          <div className="flex items-baseline gap-1">
            <motion.span 
                className="text-7xl font-thin text-white tracking-tighter tabular-nums leading-none"
                variants={slideUp}
                initial="hidden"
                animate="visible"
            >
                {progress}
            </motion.span>
            <span className="text-xl font-light text-zinc-600">%</span>
          </div>
          
          <motion.div 
            variants={contentFade(0.15, 0.3)}
            initial="hidden"
            animate="visible"
            className="h-px w-24 bg-zinc-800 mt-6 mb-3 relative overflow-hidden"
          >
              <motion.div 
                className="absolute inset-0 bg-white" 
                initial={{ x: '-100%' }}
                animate={{ x: '100%' }}
                transition={{ repeat: Infinity, duration: 1.8, ease: "easeInOut" }}
              />
          </motion.div>
          
          <p className="text-[10px] uppercase tracking-[0.3em] text-zinc-600 font-medium">
            {t('loading.marketData')}
          </p>
      </div>
    </motion.div>
  );
};
