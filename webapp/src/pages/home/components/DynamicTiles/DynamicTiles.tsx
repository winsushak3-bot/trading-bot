import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { api } from '../../../../api/client';
import { useAppStore } from '../../../../store';
import { useBackButton } from '../../../../hooks';
import { accordion, rotate180, TAP_TILE } from '../../../../shared/animations';
import { CubeTile } from './CubeTile';
import { ExpandBlocks } from './ExpandBlocks';
import { TileModal } from './TileModal';
import { useTranslation } from '../../../../i18n';

export const DynamicTiles = () => {
  const { homeTiles, setHomeTiles } = useAppStore();
  const { t } = useTranslation();
  const [isLoading, setIsLoading] = useState(!homeTiles);
  const [selectedTile, setSelectedTile] = useState<any>(null);
  const [expandedTileId, setExpandedTileId] = useState<number | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const loadTiles = async () => {
      try {
        const data = await api.home.getLayout();
        if (!controller.signal.aborted) setHomeTiles(data);
      } catch (e) {
        if (!controller.signal.aborted) console.error('Failed to load tiles', e);
      } finally {
        if (!controller.signal.aborted) setIsLoading(false);
      }
    };
    loadTiles();
    return () => controller.abort();
  }, [setHomeTiles]);

  const handleCloseModal = useCallback(() => setSelectedTile(null), []);
  useBackButton(selectedTile ? handleCloseModal : null);

  if (isLoading && !homeTiles) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin opacity-50" />
      </div>
    );
  }

  const tilesToRender = homeTiles || [];

  if (tilesToRender.length === 0 && !isLoading) {
    return (
      <div className="text-center py-12 text-zinc-600 text-sm">
        {t('home.noTiles')}
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-4 gap-2" style={{ gridAutoRows: 'minmax(80px, auto)' }}>
        {tilesToRender.map((tile) => {
          const colSpan = tile.content?.colSpan || 2;
          const rowSpan = tile.content?.rowSpan || 1;
          const isCube = tile.type === 'cube' || tile.type === 'cube_banner';

          if (isCube && tile.content?.bg_images && tile.content.bg_images.length > 0) {
            return (
              <CubeTile
                key={tile.id}
                images={tile.content.bg_images}
                interval={tile.content.rotation_interval || 3}
                autoRotate={tile.content.auto_rotate !== false}
                colSpan={colSpan}
                rowSpan={rowSpan}
                onClick={tile.content?.action_url ? () => window.open(tile.content!.action_url!, '_blank', 'noreferrer') : undefined}
              />
            );
          }

          const bgColor = tile.content?.bg_color || '#18181b';
          const isWhiteBg = bgColor === '#ffffff';
          const bgOpacity = (tile.content?.bg_opacity ?? 100) / 100;
          const bgImage = tile.content?.bg_image;
          const isExpandable = tile.content?.expandable && tile.content?.expand_blocks?.length > 0;
          const isExpanded = expandedTileId === tile.id;

          const handleTileClick = () => {
            if (tile.type === 'promo' && tile.content?.action_url) {
              window.open(tile.content.action_url, '_blank', 'noreferrer');
              return;
            }
            if (isExpandable) {
              setExpandedTileId(isExpanded ? null : tile.id);
              return;
            }
            if (tile.type === 'info') return;
            setSelectedTile(tile);
          };

          return (
            <div
              key={tile.id}
              className={`border-2 border-zinc-700 rounded-2xl relative shadow-xl transition-all ${
                isExpanded ? '' : 'overflow-hidden'
              } ${
                isExpandable ? 'cursor-pointer hover:border-zinc-600' : tile.type === 'info' ? '' : `cursor-pointer hover:border-zinc-600 ${TAP_TILE}`
              }`}
              style={{
                gridColumn: isExpanded ? '1 / -1' : `span ${colSpan}`,
                gridRow: isExpanded ? 'auto' : `span ${rowSpan}`,
              }}
            >
              {/* Main tile area */}
              <div onClick={handleTileClick} className="relative" style={{ minHeight: isExpanded ? undefined : `${rowSpan * 80}px` }}>
                <div
                  className="absolute inset-0 rounded-[14px]"
                  style={{ backgroundColor: bgColor, opacity: bgOpacity }}
                />
                {bgImage && (
                  <div
                    className="absolute inset-0 rounded-[14px] bg-cover bg-center"
                    style={{ backgroundImage: `url(${bgImage})`, opacity: bgOpacity }}
                  />
                )}

                <div className="relative z-10 flex flex-col h-full w-full p-4" style={{ minHeight: `${rowSpan * 80 - 4}px` }}>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      {tile.content?.title && (
                        <h3
                          className={`font-bold leading-tight mb-1 ${colSpan > 2 && rowSpan > 1 ? 'text-2xl' : 'text-sm'} ${isWhiteBg && !bgImage ? 'text-black' : 'text-white'}`}
                          style={bgImage ? { textShadow: '0 1px 4px rgba(0,0,0,0.7)' } : undefined}
                        >
                          {tile.content.title}
                        </h3>
                      )}
                    </div>
                    {isExpandable && (
                      <motion.div variants={rotate180(isExpanded)} animate="animate" className="shrink-0 mt-0.5">
                        <ChevronDown size={18} className={`${isWhiteBg && !bgImage ? 'text-black/50' : 'text-white/50'}`} />
                      </motion.div>
                    )}
                  </div>

                  {tile.content?.description && rowSpan > 1 && (
                    <p
                      className={`line-clamp-3 ${colSpan > 2 ? 'text-sm' : 'text-xs'} ${isWhiteBg && !bgImage ? 'text-zinc-600' : 'text-zinc-300'}`}
                      style={bgImage ? { textShadow: '0 1px 3px rgba(0,0,0,0.6)' } : undefined}
                    >
                      {tile.content.description}
                    </p>
                  )}

                  {tile.content?.image_url && !bgImage && (
                    <div className="mt-auto pt-3 flex-1 flex flex-col justify-end">
                      <img src={tile.content.image_url} alt="" loading="lazy" className="rounded-xl w-full object-cover max-h-full" />
                    </div>
                  )}
                </div>
              </div>

              {/* Expandable accordion content */}
              <AnimatePresence>
                {isExpandable && isExpanded && (
                  <motion.div variants={accordion} initial="hidden" animate="visible" exit="hidden" className="overflow-hidden">
                    <div className="px-4 pb-4 pt-1">
                      <div className="border-t border-zinc-700/50 pt-3">
                        <ExpandBlocks
                          blocks={tile.content.expand_blocks}
                          actionUrl={tile.content?.action_url}
                          actionText={tile.content?.action_text}
                        />
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>

      <AnimatePresence>
        {selectedTile && (
          <TileModal key="tile-modal" tile={selectedTile} onClose={handleCloseModal} />
        )}
      </AnimatePresence>
    </>
  );
};
