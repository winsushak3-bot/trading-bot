import { Clock } from 'lucide-react';
import { useTranslation } from '../../../../i18n';
import { TAP_TILE } from '../../../../shared/animations';

interface NewsItemProps {
  title: string;
  source: string;
  time: string;
  readTime: string;
  image?: string;
  onClick?: () => void;
  isUnread?: boolean;
}

export const NewsItem = ({ title, source, time, readTime, image, onClick, isUnread }: NewsItemProps) => {
  const { t } = useTranslation();

  return (
    <div 
      onClick={onClick}
      className={`p-4 bg-zinc-900 border-2 border-zinc-700 rounded-2xl ${TAP_TILE} cursor-pointer relative overflow-hidden`}
    >
      <div className="absolute top-0 left-0 w-20 h-20 bg-gradient-to-br from-white/5 to-transparent rounded-br-full pointer-events-none" />
      {isUnread && (
        <div className="absolute top-3 right-3 w-2 h-2 bg-white rounded-full z-10" />
      )}
      {image && (
        <img
          src={image}
          alt=""
          loading="lazy"
          className="w-full h-36 object-cover rounded-xl mb-3"
          onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
        />
      )}
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-zinc-100 flex items-center justify-center text-black font-bold text-[10px]">
              {source[0]}
          </div>
          <span className="text-xs font-medium text-zinc-400">{source}</span>
        </div>
        <span className="text-[10px] text-zinc-600">{time}</span>
      </div>
      <h3 className="text-[15px] font-bold text-zinc-100 leading-tight mb-2">
        {title}
      </h3>
      <div className="flex items-center gap-4 text-xs text-zinc-500">
          <span className="flex items-center gap-1">
              <Clock size={12} /> {readTime} {t('home.readTime')}
          </span>
      </div>
    </div>
  );
};
