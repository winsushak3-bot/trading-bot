import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { useTranslation } from '../../../../../../i18n';
import type { Language } from '../../../../../../i18n';
import { slideFromRight } from '../../../../../../shared/animations';

const LANGUAGES: { code: Language; native: string }[] = [
  { code: 'ru', native: 'Русский' },
  { code: 'en', native: 'English' },
  { code: 'ua', native: 'Українська' },
];

interface LanguagePickerScreenProps {
  onClose: () => void;
}

export const LanguagePickerScreen = ({ onClose }: LanguagePickerScreenProps) => {
  const { language, setLanguage } = useTranslation();
  const handleSelect = (code: Language) => {
    setLanguage(code);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[60] overflow-hidden">
      <motion.div
        variants={slideFromRight}
        initial="hidden"
        animate="visible"
        exit="hidden"
        className="absolute inset-0 bg-black flex flex-col"
      >
        <div
          className="flex-1 overflow-y-auto px-2 space-y-2"
          style={{
            paddingTop: 'calc(24px + var(--safe-top, 0px))',
            paddingBottom: 'calc(80px + var(--safe-bottom, 0px))',
          }}
        >
          {LANGUAGES.map((lang) => {
            const isActive = language === lang.code;
            return (
              <button
                key={lang.code}
                onClick={() => handleSelect(lang.code)}
                className="w-full flex items-center gap-3 px-4 py-3 bg-zinc-900 border-2 border-zinc-700 rounded-xl active:bg-zinc-800 transition-colors text-left"
              >
                <span className="flex-1 text-white text-base">{lang.native}</span>
                {isActive && <Check size={18} className="text-white shrink-0" />}
              </button>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
};
