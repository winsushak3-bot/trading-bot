import { GripVertical, Pencil, Eye, EyeOff, Copy } from 'lucide-react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import type { HomeTile } from '../../../../api/client';

interface GridTileProps {
  tile: HomeTile;
  onEdit: (t: HomeTile) => void;
  onToggleActive: (t: HomeTile) => void;
  onDuplicate: (t: HomeTile) => void;
}

export const GridTile = ({ tile, onEdit, onToggleActive, onDuplicate }: GridTileProps) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: tile.id });
  const cs = tile.content?.colSpan || 2;
  const rs = tile.content?.rowSpan || 1;
  const bg = tile.content?.bg_color || '#18181b';
  const isWhite = bg === '#ffffff';
  const bgImg = tile.content?.bg_image;
  const isCube = tile.type === 'cube' || tile.type === 'cube_banner';
  const cubeImgs = tile.content?.bg_images;

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    gridColumn: `span ${cs}`,
    gridRow: `span ${rs}`,
    opacity: isDragging ? 0.3 : tile.is_active ? 1 : 0.45,
    zIndex: isDragging ? 50 : undefined,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`group relative rounded-2xl overflow-hidden border-2 transition-all ${
        isDragging ? 'border-blue-500 shadow-2xl' : tile.is_active ? 'border-zinc-700 hover:border-zinc-500' : 'border-zinc-800'
      }`}
    >
      {/* BG layer */}
      <div className="absolute inset-0" style={{ backgroundColor: bg }} />
      {bgImg && !isCube && (
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${bgImg})` }} />
      )}
      {isCube && cubeImgs && cubeImgs.length > 0 && (
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${cubeImgs[0]})` }} />
      )}
      <div className="absolute inset-0 bg-black/30" />

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full p-3">
        {!isCube && tile.content?.title && (
          <h3 className={`font-bold leading-tight mb-0.5 truncate ${cs > 2 && rs > 1 ? 'text-base' : 'text-xs'} ${isWhite && !bgImg ? 'text-black' : 'text-white'}`}>
            {tile.content.title}
          </h3>
        )}
        {!isCube && tile.content?.description && rs > 1 && (
          <p className={`line-clamp-2 text-[10px] ${isWhite && !bgImg ? 'text-zinc-600' : 'text-zinc-300'}`}>
            {tile.content.description}
          </p>
        )}
        {isCube && cubeImgs && cubeImgs.length > 1 && (
          <div className="flex items-end justify-center h-full">
            <div className="flex gap-0.5">
              {cubeImgs.slice(0, 4).map((_: string, i: number) => (
                <div key={i} className={`w-1.5 h-1.5 rounded-full ${i === 0 ? 'bg-white' : 'bg-white/40'}`} />
              ))}
            </div>
          </div>
        )}

        {/* Type badge */}
        <div className="mt-auto flex items-end justify-between">
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-black/50 text-white/70 uppercase font-medium backdrop-blur">
            {tile.type} · {cs}×{rs}
          </span>
          {!tile.is_active && (
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-red-500/30 text-red-300 font-medium backdrop-blur">
              скрыт
            </span>
          )}
        </div>
      </div>

      {/* Click area — whole tile opens editor */}
      <div
        className="absolute inset-0 z-10 cursor-pointer"
        onClick={() => onEdit(tile)}
      />

      {/* Hover overlay with actions */}
      <div className="absolute inset-0 z-20 bg-black/0 group-hover:bg-black/50 transition-colors flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 pointer-events-none">
        <button
          {...attributes}
          {...listeners}
          className="pointer-events-auto p-2 rounded-xl bg-zinc-800/80 backdrop-blur text-zinc-300 hover:text-white hover:bg-zinc-700 transition-colors cursor-grab active:cursor-grabbing touch-none"
          title="Перетащить"
        >
          <GripVertical size={16} />
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onEdit(tile); }}
          className="pointer-events-auto p-2 rounded-xl bg-zinc-800/80 backdrop-blur text-zinc-300 hover:text-white hover:bg-zinc-700 transition-colors"
          title="Редактировать"
        >
          <Pencil size={16} />
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onToggleActive(tile); }}
          className="pointer-events-auto p-2 rounded-xl bg-zinc-800/80 backdrop-blur text-zinc-300 hover:text-white hover:bg-zinc-700 transition-colors"
          title={tile.is_active ? 'Скрыть' : 'Показать'}
        >
          {tile.is_active ? <Eye size={16} /> : <EyeOff size={16} />}
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onDuplicate(tile); }}
          className="pointer-events-auto p-2 rounded-xl bg-zinc-800/80 backdrop-blur text-zinc-300 hover:text-white hover:bg-zinc-700 transition-colors"
          title="Дублировать"
        >
          <Copy size={16} />
        </button>
      </div>
    </div>
  );
};
