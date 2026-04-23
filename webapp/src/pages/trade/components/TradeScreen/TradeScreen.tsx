import { motion } from 'framer-motion';
import { useBackButton } from '../../../../hooks';
import { slideFromRight } from '../../../../shared/animations';

interface TradeScreenProps {
  market: 'crypto' | 'forex' | 'screener';
  onClose: () => void;
}

export const TradeScreen = ({ market, onClose }: TradeScreenProps) => {
  useBackButton(onClose);

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <motion.div
        variants={slideFromRight}
        initial="hidden"
        animate="visible"
        exit="hidden"
        className="absolute inset-0 bg-black flex flex-col items-center justify-center"
      >
        <div
          className="flex-1 flex items-center justify-center w-full"
          style={{
            paddingTop: 'calc(16px + var(--safe-top, 0px))',
            paddingBottom: 'calc(80px + var(--safe-bottom, 0px))',
          }}
        >
          <p className="text-zinc-500 text-sm">{market === 'crypto' ? 'Crypto' : market === 'forex' ? 'Forex' : 'Screener'}</p>
        </div>
      </motion.div>
    </div>
  );
};
