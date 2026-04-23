import { motion } from 'framer-motion';
import { Smartphone, X } from 'lucide-react';
import type { HomeTile } from '../../../../api/client';

interface LivePreviewProps {
  tiles: HomeTile[];
  onClose: () => void;
}

export const LivePreview = ({ tiles, onClose }: LivePreviewProps) => {
  const activeTiles = tiles.filter(t => t.is_active);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="relative z-10 flex flex-col items-center"
      >
        {/* Header */}
        <div className="flex items-center gap-2 mb-4">
          <Smartphone size={16} className="text-zinc-400" />
          <span className="text-zinc-400 text-sm font-medium">Как видит пользователь</span>
          <button onClick={onClose} className="ml-4 text-zinc-500 hover:text-white transition-colors">
            <X size={18} />
          </button>
        </div>

        {/* Phone frame */}
        <div className="w-[375px] bg-black rounded-[2.5rem] border-2 border-zinc-700 p-3 shadow-2xl">
          <div className="bg-black rounded-[2rem] overflow-hidden">
            {/* Status bar */}
            <div className="h-12 bg-black flex items-center justify-center">
              <div className="w-20 h-5 bg-zinc-900 rounded-full" />
            </div>

            {/* Content area */}
            <div className="px-3 pb-20 min-h-[500px]">
              {/* Tab bar mock */}
              <div className="flex gap-2 mb-4">
                <div className="px-4 py-1.5 bg-white text-black rounded-full text-xs font-bold">New</div>
                <div className="px-4 py-1.5 bg-zinc-900 text-zinc-400 rounded-full text-xs font-medium">Forex</div>
                <div className="px-4 py-1.5 bg-zinc-900 text-zinc-400 rounded-full text-xs font-medium">Crypto</div>
              </div>

              {/* Tiles grid */}
              {activeTiles.length === 0 ? (
                <div className="text-center py-16 text-zinc-600 text-xs">
                  Нет активных тайлов
                </div>
              ) : (
                <div className="grid grid-cols-4 gap-1.5" style={{ gridAutoRows: '60px' }}>
                  {activeTiles.map((tile) => {
                    const cs = tile.content?.colSpan || 2;
                    const rs = tile.content?.rowSpan || 1;
                    const bg = tile.content?.bg_color || '#18181b';
                    const isWhite = bg === '#ffffff';
                    const op = (tile.content?.bg_opacity ?? 100) / 100;
                    const bgImg = tile.content?.bg_image;
                    const isCube = tile.type === 'cube' || tile.type === 'cube_banner';
                    const cubeImgs = tile.content?.bg_images as string[] | undefined;

                    return (
                      <div
                        key={tile.id}
                        className="rounded-xl overflow-hidden flex flex-col border border-zinc-700/50 relative"
                        style={{
                          gridColumn: `span ${cs}`,
                          gridRow: `span ${rs}`,
                        }}
                      >
                        <div className="absolute inset-0 rounded-[10px]" style={{ backgroundColor: bg, opacity: op }} />
                        {bgImg && !isCube && (
                          <div className="absolute inset-0 rounded-[10px] bg-cover bg-center" style={{ backgroundImage: `url(${bgImg})`, opacity: op }} />
                        )}
                        {isCube && cubeImgs && cubeImgs.length > 0 && (
                          <div className="absolute inset-0 rounded-[10px] bg-cover bg-center" style={{ backgroundImage: `url(${cubeImgs[0]})` }} />
                        )}
                        <div className="relative z-10 p-2.5 flex flex-col h-full">
                          {!isCube && tile.content?.title && (
                            <h3 className={`font-bold leading-tight mb-0.5 ${cs > 2 && rs > 1 ? 'text-sm' : 'text-[10px]'} ${isWhite && !bgImg ? 'text-black' : 'text-white'}`}
                              style={bgImg ? { textShadow: '0 1px 3px rgba(0,0,0,0.7)' } : undefined}
                            >
                              {tile.content.title}
                            </h3>
                          )}
                          {!isCube && tile.content?.description && rs > 1 && (
                            <p className={`line-clamp-2 ${cs > 2 ? 'text-[10px]' : 'text-[9px]'} ${isWhite && !bgImg ? 'text-zinc-600' : 'text-zinc-300'}`}>
                              {tile.content.description}
                            </p>
                          )}
                          {!isCube && tile.content?.image_url && !bgImg && rs > 1 && (
                            <div className="mt-auto pt-1 flex-1 flex flex-col justify-end">
                              <img
                                src={tile.content.image_url}
                                alt=""
                                className="rounded-lg w-full object-cover max-h-12"
                                onError={(e) => (e.currentTarget.style.display = 'none')}
                              />
                            </div>
                          )}
                          {isCube && cubeImgs && cubeImgs.length > 1 && (
                            <div className="flex items-end justify-center h-full">
                              <div className="flex gap-0.5">
                                {cubeImgs.slice(0, 4).map((_: string, i: number) => (
                                  <div key={i} className={`w-1 h-1 rounded-full ${i === 0 ? 'bg-white' : 'bg-white/40'}`} />
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Bottom nav mock */}
            <div className="h-16 bg-zinc-900/95 border-t border-zinc-800 flex items-center justify-around px-4">
              {['Главная', 'Кошелек', 'Торговля', 'Поддержка', 'Профиль'].map((l) => (
                <div key={l} className="flex flex-col items-center gap-0.5">
                  <div className="w-5 h-5 rounded bg-zinc-800" />
                  <span className="text-[8px] text-zinc-500">{l}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};
