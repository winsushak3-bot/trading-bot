import { ShieldCheck, ChevronRight } from 'lucide-react';
import { useTranslation } from '../../../../../../i18n';

export const TwoFASetting = () => {
  const { t } = useTranslation();
  return (
    <button
      onClick={() => {}}
      className="w-full flex items-center gap-3 px-4 py-3 bg-zinc-900 active:bg-zinc-800 transition-colors text-left"
    >
      <div className="w-9 h-9 rounded-xl bg-white flex items-center justify-center shrink-0">
        <ShieldCheck size={18} className="text-black" />
      </div>
      <span className="flex-1 text-white text-base">2FA</span>
      <span className="text-zinc-500 text-sm mr-1">{t('common.off')}</span>
      <ChevronRight size={16} className="text-zinc-600 shrink-0" />
    </button>
  );
};
