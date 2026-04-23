import { useState, useCallback } from 'react';
import { AnimatePresence } from 'framer-motion';
import { AboutModal } from './AboutModal';
import { TAP_TILE } from '../../../../shared/animations';
import { useTranslation } from '../../../../i18n';

export const AboutTile = () => {
  const { t } = useTranslation();
  const [showModal, setShowModal] = useState(false);
  const handleClose = useCallback(() => setShowModal(false), []);

  return (
    <>
      <button 
        onClick={() => setShowModal(true)}
        className={`bg-zinc-900 border-2 border-zinc-700 rounded-xl p-2 ${TAP_TILE} relative overflow-hidden`}
      >
        <div className="absolute top-0 left-0 w-12 h-12 bg-gradient-to-br from-white/5 to-transparent rounded-br-full pointer-events-none" />
        <p className="text-zinc-400 text-xs font-bold relative z-10">{t('profile.about')}</p>
      </button>

      <AnimatePresence>
        {showModal && <AboutModal onClose={handleClose} />}
      </AnimatePresence>
    </>
  );
};
