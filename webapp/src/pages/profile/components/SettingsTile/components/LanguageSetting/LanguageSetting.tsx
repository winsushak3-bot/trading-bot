import { Globe, ChevronRight } from 'lucide-react';
import { useTranslation } from '../../../../../../i18n';

interface LanguageSettingProps {
  onOpenPicker: () => void;
}

export const LanguageSetting = ({ onOpenPicker }: LanguageSettingProps) => {
  const { t, language } = useTranslation();

  return (
    <button
      onClick={onOpenPicker}
      className="w-full flex items-center gap-3 px-4 py-3 bg-zinc-900 border-2 border-zinc-700 rounded-xl active:bg-zinc-800 transition-colors text-left"
    >
      <div className="w-9 h-9 rounded-xl bg-white flex items-center justify-center shrink-0">
        <Globe size={18} className="text-black" />
      </div>
      <span className="flex-1 text-white text-base">{t('settings.language')}</span>
      <span className="text-zinc-500 text-sm mr-1">{t(`settings.languages.${language}`)}</span>
      <ChevronRight size={16} className="text-zinc-600 shrink-0" />
    </button>
  );
};
