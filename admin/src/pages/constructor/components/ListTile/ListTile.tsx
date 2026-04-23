import { GripVertical, Pencil, Eye, EyeOff, Copy } from 'lucide-react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import type { HomeTile } from '../../../../api/client';

interface ListTileProps {
  tile: HomeTile;
  onEdit: (t: HomeTile) => void;
  onToggleActive: (t: HomeTile) => void;
  onDuplicate: (t: HomeTile) => void;
}

export const ListTile = ({ tile, onEdit, onToggleActive, onDuplicate }: ListTileProps) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: tile.id });
  const cs = tile.content?.colSpan || 2;
  const rs = tile.content?.rowSpan || 1;

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 50 : undefined,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-3 bg-zinc-900 border rounded-xl px-4 py-3 transition-all ${
        isDragging ? 'border-zinc-600 shadow-2xl shadow-white/5 scale-[1.02]' : tile.is_active ? 'border-zinc-800' : 'border-zinc-800/50 opacity-50'
      }`}
    >
      <button
        {...attributes}
        {...listeners}
        className="cursor-grab active:cursor-grabbing text-zinc-600 hover:text-zinc-400 transition-colors touch-none p-1"
      >
        <GripVertical size={16} />
      </button>
      <div
        className="w-10 h-10 rounded-lg border border-zinc-700 flex items-center justify-center text-[9px] text-zinc-400 font-mono shrink-0"
        style={{ backgroundColor: tile.content?.bg_color || '#18181b' }}
      >
        {cs}×{rs}
      </div>
      <div className="flex-1 min-w-0" onClick={() => onEdit(tile)} role="button">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-white truncate">
            {tile.content?.title || 'Без заголовка'}
          </span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-500 uppercase font-medium shrink-0">
            {tile.type}
          </span>
          {!tile.is_active && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-600 font-medium shrink-0">
              скрыт
            </span>
          )}
        </div>
        <p className="text-xs text-zinc-500 truncate mt-0.5">
          {tile.content?.description || 'Нет описания'}
        </p>
      </div>
      <div className="flex items-center gap-0.5 shrink-0">
        <button onClick={() => onDuplicate(tile)} className="p-2 rounded-lg text-zinc-600 hover:text-zinc-300 transition-colors" title="Дублировать">
          <Copy size={15} />
        </button>
        <button onClick={() => onToggleActive(tile)} className={`p-2 rounded-lg transition-colors ${tile.is_active ? 'text-zinc-400 hover:text-white' : 'text-zinc-600 hover:text-zinc-300'}`} title={tile.is_active ? 'Скрыть' : 'Показать'}>
          {tile.is_active ? <Eye size={15} /> : <EyeOff size={15} />}
        </button>
        <button onClick={() => onEdit(tile)} className="p-2 rounded-lg text-zinc-400 hover:text-white transition-colors" title="Редактировать">
          <Pencil size={15} />
        </button>
      </div>
    </div>
  );
};
