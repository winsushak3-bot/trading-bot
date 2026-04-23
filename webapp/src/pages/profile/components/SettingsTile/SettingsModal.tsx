import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useBackButton } from '../../../../hooks';
import { slideFromRight } from '../../../../shared/animations';
import { FullscreenSetting, LanguageSetting, LanguagePickerScreen } from './components';

interface SettingsModalProps {
  onClose: () => void;
}

export const SettingsModal = ({ onClose }: SettingsModalProps) => {
  const [showLangPicker, setShowLangPicker] = useState(false);
  const closeLangPicker = useCallback(() => setShowLangPicker(false), []);

  useBackButton(showLangPicker ? closeLangPicker : onClose);

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <motion.div
        variants={slideFromRight}
        initial="hidden"
        animate="visible"
        exit="hidden"
        className="absolute inset-0 bg-black flex flex-col"
      >
        <div className="flex-1 overflow-y-auto px-2 space-y-2" style={{ paddingTop: 'calc(24px + var(--safe-top, 0px))', paddingBottom: 'calc(80px + var(--safe-bottom, 0px))' }}>
          <LanguageSetting onOpenPicker={() => setShowLangPicker(true)} />
          <FullscreenSetting />
        </div>
      </motion.div>

      <AnimatePresence>
        {showLangPicker && (
          <LanguagePickerScreen key="lang-picker" onClose={closeLangPicker} />
        )}
      </AnimatePresence>
    </div>
  );
};
