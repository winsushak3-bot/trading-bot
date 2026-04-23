import { X, AlertCircle, Upload, Type, Image as ImageIcon, ChevronDown, ChevronUp, Link, Film } from 'lucide-react';
import type { EditorState } from './types';
import { inputCls, errorInputCls } from './constants';

type Props = Pick<EditorState,
  'type' | 'expandable' | 'setExpandable' | 'expandBlocks' | 'setExpandBlocks' |
  'actionUrl' | 'setActionUrl' | 'actionText' | 'setActionText' |
  'errors' | 'setErrors' | 'setShowCropModal' | 'setExpandCropIndex'
>;

export const TabAction = (s: Props) => {
  if (s.type === 'promo') {
    return (
      <div className="text-center py-8 text-zinc-500 text-sm">
        Для промо ссылка настраивается на вкладке «Контент»
      </div>
    );
  }

  if (s.type === 'info' || s.type === 'banner') {
    return (
      <>
        <div className="flex items-center justify-between py-2">
          <div>
            <span className="text-sm text-zinc-300">Раскрытие по клику</span>
            <p className="text-[11px] text-zinc-600 mt-0.5">При нажатии тайл раскроется с доп. контентом</p>
          </div>
          <button
            onClick={() => s.setExpandable(!s.expandable)}
            className={`w-11 h-6 rounded-full transition-colors relative shrink-0 ${s.expandable ? 'bg-white' : 'bg-zinc-700'}`}
          >
            <div className={`absolute top-0.5 w-5 h-5 rounded-full transition-all ${s.expandable ? 'left-[22px] bg-black' : 'left-0.5 bg-zinc-400'}`} />
          </button>
        </div>

        {s.expandable && <ExpandBlocksEditor s={s} />}

        {s.type === 'banner' && (
          <>
            <div className="border-t border-zinc-800 pt-4 mt-2">
              <label className="block text-xs font-medium text-zinc-400 mb-1.5">Ссылка-действие</label>
              <input
                type="text" value={s.actionUrl}
                onChange={(e) => { s.setActionUrl(e.target.value); s.setErrors(p => ({ ...p, actionUrl: '' })); }}
                placeholder="https://..."
                className={s.errors.actionUrl ? errorInputCls : inputCls}
              />
              {s.errors.actionUrl && <p className="flex items-center gap-1 text-red-400 text-xs mt-1"><AlertCircle size={12} />{s.errors.actionUrl}</p>}
              <p className="text-zinc-600 text-[11px] mt-1">Кнопка появится внутри раскрытого контента</p>
            </div>
            {s.actionUrl && (
              <div>
                <label className="block text-xs font-medium text-zinc-400 mb-1.5">Текст кнопки</label>
                <input type="text" value={s.actionText} onChange={(e) => s.setActionText(e.target.value)} placeholder="Перейти" className={inputCls} />
              </div>
            )}
          </>
        )}
      </>
    );
  }

  // Default: cube or other types with action URL
  return (
    <>
      <div>
        <label className="block text-xs font-medium text-zinc-400 mb-1.5">Ссылка-действие</label>
        <input
          type="text" value={s.actionUrl}
          onChange={(e) => { s.setActionUrl(e.target.value); s.setErrors(p => ({ ...p, actionUrl: '' })); }}
          placeholder="https://..."
          className={s.errors.actionUrl ? errorInputCls : inputCls}
        />
        {s.errors.actionUrl && <p className="flex items-center gap-1 text-red-400 text-xs mt-1"><AlertCircle size={12} />{s.errors.actionUrl}</p>}
        <p className="text-zinc-600 text-[11px] mt-1">Кнопка появится внутри модалки баннера</p>
      </div>
      {s.actionUrl && (
        <div>
          <label className="block text-xs font-medium text-zinc-400 mb-1.5">Текст кнопки</label>
          <input type="text" value={s.actionText} onChange={(e) => s.setActionText(e.target.value)} placeholder="Перейти" className={inputCls} />
        </div>
      )}
      {!s.actionUrl && (
        <div className="text-center py-8 text-zinc-600 text-sm">
          Добавьте ссылку, чтобы в баннере появилась кнопка
        </div>
      )}
    </>
  );
};

/* ── Expand Blocks Sub-editor ─────────────────────────── */
const ExpandBlocksEditor = ({ s }: { s: Props }) => (
  <>
    <div className="space-y-2">
      {s.expandBlocks.map((block, idx) => (
        <div key={idx} className="bg-zinc-800/50 rounded-xl p-3 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-700 text-zinc-400 uppercase font-medium">
                {block.type === 'text' ? 'Текст' : block.type === 'image' ? 'Фото' : block.type === 'video' ? 'Видео' : 'Ссылка'}
              </span>
              <span className="text-zinc-500 text-xs">#{idx + 1}</span>
            </div>
            <div className="flex items-center gap-1">
              {idx > 0 && (
                <button onClick={() => { const a = [...s.expandBlocks]; [a[idx - 1], a[idx]] = [a[idx], a[idx - 1]]; s.setExpandBlocks(a); }} className="p-1 rounded text-zinc-600 hover:text-zinc-300 transition-colors">
                  <ChevronUp size={14} />
                </button>
              )}
              {idx < s.expandBlocks.length - 1 && (
                <button onClick={() => { const a = [...s.expandBlocks]; [a[idx], a[idx + 1]] = [a[idx + 1], a[idx]]; s.setExpandBlocks(a); }} className="p-1 rounded text-zinc-600 hover:text-zinc-300 transition-colors">
                  <ChevronDown size={14} />
                </button>
              )}
              <button onClick={() => s.setExpandBlocks(prev => prev.filter((_, i) => i !== idx))} className="p-1 rounded text-zinc-600 hover:text-red-400 transition-colors">
                <X size={14} />
              </button>
            </div>
          </div>

          {block.type === 'text' && (
            <textarea
              value={block.value}
              onChange={(e) => { const a = [...s.expandBlocks]; a[idx] = { ...a[idx], value: e.target.value }; s.setExpandBlocks(a); }}
              placeholder="Текст блока..." rows={3}
              className={inputCls + ' resize-none text-xs'}
            />
          )}

          {block.type === 'image' && (
            <div className="space-y-2">
              {block.value ? (
                <div className="relative rounded-xl overflow-hidden border border-zinc-700 group">
                  <img src={block.value} alt="" className="w-full h-24 object-cover" onError={(e) => (e.currentTarget.style.display = 'none')} />
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center gap-2">
                    <button onClick={() => { s.setExpandCropIndex(idx); s.setShowCropModal(true); }} className="opacity-0 group-hover:opacity-100 px-2 py-1 rounded-lg bg-zinc-800/80 text-white text-xs transition-opacity">Заменить</button>
                    <button onClick={() => { const a = [...s.expandBlocks]; a[idx] = { ...a[idx], value: '' }; s.setExpandBlocks(a); }} className="opacity-0 group-hover:opacity-100 w-6 h-6 rounded-full bg-red-500/80 flex items-center justify-center text-white transition-opacity"><X size={12} /></button>
                  </div>
                </div>
              ) : (
                <button onClick={() => { s.setExpandCropIndex(idx); s.setShowCropModal(true); }} className="w-full border-2 border-dashed border-zinc-700 rounded-xl py-5 flex flex-col items-center gap-1.5 hover:border-zinc-500 transition-colors group">
                  <Upload size={18} className="text-zinc-500 group-hover:text-zinc-300 transition-colors" />
                  <span className="text-zinc-500 text-[10px] group-hover:text-zinc-300">Загрузить фото</span>
                </button>
              )}
            </div>
          )}

          {block.type === 'video' && (
            <input type="text" value={block.value} onChange={(e) => { const a = [...s.expandBlocks]; a[idx] = { ...a[idx], value: e.target.value }; s.setExpandBlocks(a); }} placeholder="URL видео (mp4)..." className={inputCls + ' text-xs'} />
          )}

          {block.type === 'link' && (
            <>
              <input type="text" value={block.value} onChange={(e) => { const a = [...s.expandBlocks]; a[idx] = { ...a[idx], value: e.target.value }; s.setExpandBlocks(a); }} placeholder="https://..." className={inputCls + ' text-xs'} />
              <input type="text" value={block.label || ''} onChange={(e) => { const a = [...s.expandBlocks]; a[idx] = { ...a[idx], label: e.target.value }; s.setExpandBlocks(a); }} placeholder="Текст ссылки" className={inputCls + ' text-xs'} />
            </>
          )}
        </div>
      ))}
    </div>

    {/* Add block buttons */}
    <div className="grid grid-cols-4 gap-1.5">
      {[
        { t: 'text' as const, icon: Type, label: 'Текст' },
        { t: 'image' as const, icon: ImageIcon, label: 'Фото' },
        { t: 'video' as const, icon: Film, label: 'Видео' },
        { t: 'link' as const, icon: Link, label: 'Ссылка' },
      ].map((b) => (
        <button
          key={b.t}
          onClick={() => s.setExpandBlocks(prev => [...prev, { type: b.t, value: '' }])}
          className="flex flex-col items-center gap-1 py-2.5 rounded-xl bg-zinc-800 border border-zinc-700 text-zinc-400 hover:text-white hover:border-zinc-500 transition-colors text-[10px] font-medium"
        >
          <b.icon size={14} />
          {b.label}
        </button>
      ))}
    </div>

    {s.expandBlocks.length === 0 && (
      <div className="text-center py-4 text-zinc-600 text-xs">Добавьте блоки контента выше</div>
    )}
  </>
);
