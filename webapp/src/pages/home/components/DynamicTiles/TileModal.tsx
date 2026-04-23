import { motion } from 'framer-motion';
import { simpleFade, popupSlide, TAP_BUTTON } from '../../../../shared/animations';
import { ExpandBlocks } from './ExpandBlocks';
import { useTranslation } from '../../../../i18n';

interface TileModalProps {
  tile: any;
  onClose: () => void;
}

export const TileModal = ({ tile, onClose }: TileModalProps) => {
  const { t } = useTranslation();
  return (
  <div className="fixed inset-0 z-50">
    <motion.div
      variants={simpleFade}
      initial="hidden"
      animate="visible"
      exit="hidden"
      className="absolute inset-0 bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    />

    <motion.div
      variants={popupSlide}
      initial="hidden"
      animate="visible"
      exit="hidden"
      className="absolute inset-x-4 bg-zinc-900/90 backdrop-blur-xl rounded-3xl border-2 border-zinc-700 p-6 z-10 max-w-md mx-auto max-h-[70vh] overflow-y-auto shadow-2xl flex flex-col"
      style={{ top: 'calc(96px + var(--safe-top, 0px))' }}
    >
      {tile.content?.image_url && (
        <div className="mb-5 -mt-2 -mx-2 rounded-2xl overflow-hidden shadow-lg">
          <img src={tile.content.image_url} alt="" loading="lazy" className="w-full h-auto object-cover max-h-48" />
        </div>
      )}

      {tile.content?.title && (
        <h3 className="text-2xl font-bold text-white leading-tight mb-3">
          {tile.content.title}
        </h3>
      )}

      {tile.content?.description && (
        <p className="text-zinc-300 text-sm leading-relaxed whitespace-pre-wrap">
          {tile.content.description}
        </p>
      )}

      {/* Expand blocks inside modal too */}
      {tile.content?.expandable && tile.content?.expand_blocks?.length > 0 && (
        <div className="mt-4">
          <ExpandBlocks
            blocks={tile.content.expand_blocks}
            actionUrl={tile.content?.action_url}
            actionText={tile.content?.action_text}
          />
        </div>
      )}

      {/* Action link (only if no expand blocks) */}
      {tile.content?.action_url && !(tile.content?.expandable && tile.content?.expand_blocks?.length > 0) && (
        <a
          href={tile.content.action_url}
          target="_blank"
          rel="noreferrer"
          className={`mt-6 w-full block text-center py-3 bg-white text-black font-bold rounded-xl ${TAP_BUTTON}`}
        >
          {tile.content.action_text || t('common.goTo')}
        </a>
      )}
    </motion.div>
  </div>
  );
};
