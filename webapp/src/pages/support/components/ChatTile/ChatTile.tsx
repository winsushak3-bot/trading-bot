import { MessageCircle } from 'lucide-react';
import { useTranslation } from '../../../../i18n';

interface ChatTileProps {
  onClick: () => void;
}

export const ChatTile = ({ onClick }: ChatTileProps) => {
  const { t } = useTranslation();
  return (
    <div className="bg-zinc-900 border-2 border-zinc-700 rounded-2xl p-5 relative overflow-hidden w-full">
      <div className="absolute top-0 left-0 w-20 h-20 bg-gradient-to-br from-white/5 to-transparent rounded-br-full pointer-events-none" />
      
      <div className="flex items-center gap-3 mb-3 relative z-10">
        <div className="p-2 bg-white rounded-xl">
          <MessageCircle size={20} className="text-black" />
        </div>
        <h3 className="font-bold text-white text-left">{t('support.chatTitle')}</h3>
      </div>
      
      <p className="text-sm text-zinc-400 mb-4 relative z-10">
        {t('support.chatSubtitle')}
      </p>
      
      <button 
        onClick={onClick}
        className="w-full bg-white text-black py-3 rounded-xl font-bold text-sm relative z-10 transition-transform duration-100 active:scale-[0.97]"
      >
        {t('support.writeMessage')}
      </button>
    </div>
  );
};
