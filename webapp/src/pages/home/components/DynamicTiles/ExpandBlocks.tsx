import { TAP_BUTTON } from '../../../../shared/animations';
import { useTranslation } from '../../../../i18n';

interface ExpandBlocksProps {
  blocks: { type: string; value: string; label?: string }[];
  actionUrl?: string;
  actionText?: string;
}

export const ExpandBlocks = ({ blocks, actionUrl, actionText }: ExpandBlocksProps) => {
  const { t } = useTranslation();
  return (
  <div className="space-y-3">
    {blocks.map((block, i) => {
      if (block.type === 'text' && block.value) {
        return (
          <p key={i} className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
            {block.value}
          </p>
        );
      }
      if (block.type === 'image' && block.value) {
        return (
          <img
            key={i}
            src={block.value}
            alt=""
            loading="lazy"
            className="w-full rounded-xl object-cover max-h-56"
          />
        );
      }
      if (block.type === 'video' && block.value) {
        return (
          <video
            key={i}
            src={block.value}
            controls
            playsInline
            className="w-full rounded-xl max-h-56"
          />
        );
      }
      if (block.type === 'link' && block.value) {
        return (
          <a
            key={i}
            href={block.value}
            target="_blank"
            rel="noreferrer"
            className={`block w-full text-center py-2.5 bg-zinc-800 border border-zinc-700 text-white font-medium rounded-xl text-sm hover:bg-zinc-700 transition-colors ${TAP_BUTTON}`}
          >
            {block.label || block.value}
          </a>
        );
      }
      return null;
    })}
    {actionUrl && (
      <a
        href={actionUrl}
        target="_blank"
        rel="noreferrer"
        className={`block w-full text-center py-3 bg-white text-black font-bold rounded-xl ${TAP_BUTTON}`}
      >
        {actionText || t('common.goTo')}
      </a>
    )}
  </div>
  );
};
