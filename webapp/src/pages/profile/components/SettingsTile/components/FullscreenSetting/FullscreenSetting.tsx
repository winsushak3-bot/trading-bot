import { Maximize, Minimize, ChevronRight } from 'lucide-react';
import { useWebApp } from '../../../../../../hooks';
import { useAppStore } from '../../../../../../store';
import { useTranslation } from '../../../../../../i18n';

export const FullscreenSetting = () => {
  const { webApp } = useWebApp();
  const { isFullscreen, setFullscreen } = useAppStore();
  const { t } = useTranslation();

  const toggleFullscreen = () => {
    if (!webApp) return;
    
    try {
      if (isFullscreen) {
        if (webApp.exitFullscreen) {
          webApp.exitFullscreen();
          setFullscreen(false);
        }
      } else {
        if (webApp.requestFullscreen) {
          webApp.requestFullscreen();
          setFullscreen(true);
        }
      }
    } catch (e) {
      console.warn('Fullscreen toggle failed', e);
    }
  };

  const Icon = isFullscreen ? Minimize : Maximize;

  return (
    <button
      onClick={toggleFullscreen}
      className="w-full flex items-center gap-3 px-4 py-3 bg-zinc-900 border-2 border-zinc-700 rounded-xl active:bg-zinc-800 transition-colors text-left"
    >
      <div className="w-9 h-9 rounded-xl bg-white flex items-center justify-center shrink-0">
        <Icon size={18} className="text-black" />
      </div>
      <span className="flex-1 text-white text-base">{t('settings.fullscreen')}</span>
      <span className="text-zinc-500 text-sm mr-1">
        {isFullscreen ? t('common.on') : t('common.off')}
      </span>
      <ChevronRight size={16} className="text-zinc-600 shrink-0" />
    </button>
  );
};
