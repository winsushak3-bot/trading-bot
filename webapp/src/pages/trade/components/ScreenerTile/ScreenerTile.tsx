import { ScanSearch } from 'lucide-react';
import { useTranslation } from '../../../../i18n';
import { TAP_TILE } from '../../../../shared/animations';

interface ScreenerTileProps {
  onClick?: () => void;
}

export const ScreenerTile = ({ onClick }: ScreenerTileProps) => {
  const { t } = useTranslation();
  return (
    <button
      onClick={onClick}
      className={`bg-zinc-900 border-2 border-zinc-700 rounded-xl p-3 ${TAP_TILE} relative overflow-hidden w-full text-left`}
    >
      <div className="absolute top-0 left-0 w-12 h-12 bg-gradient-to-br from-white/5 to-transparent rounded-br-full pointer-events-none" />
      <div className="flex items-center gap-3 relative z-10">
        <div className="p-2 bg-white/10 rounded-lg">
          <ScanSearch size={18} className="text-white" />
        </div>
        <div>
          <p className="text-white text-sm font-bold">Screener</p>
          <p className="text-zinc-500 text-[11px]">{t('trade.screener')}</p>
        </div>
      </div>
    </button>
  );
};
