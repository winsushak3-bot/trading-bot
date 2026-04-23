import { AlertCircle } from 'lucide-react';
import type { EditorState } from './types';
import { inputCls, errorInputCls } from './constants';

type Props = Pick<EditorState,
  'title' | 'setTitle' | 'description' | 'setDescription' | 'imageUrl' | 'setImageUrl' |
  'actionUrl' | 'setActionUrl' | 'type' | 'isCube' | 'errors' | 'setErrors'
>;

export const TabContent = (s: Props) => {
  if (s.isCube) {
    return (
      <div className="text-center py-6 text-zinc-500 text-sm">
        Куб-тайлы не имеют текстового контента.<br/>
        <span className="text-zinc-600 text-xs">Добавьте изображения на вкладке «Стиль»</span>
      </div>
    );
  }

  return (
    <>
      <div>
        <label className="block text-xs font-medium text-zinc-400 mb-1.5">Заголовок *</label>
        <input
          type="text" value={s.title}
          onChange={(e) => { s.setTitle(e.target.value); s.setErrors(p => ({...p, title: ''})); }}
          placeholder={s.type === 'promo' ? 'Название акции' : 'Заголовок баннера'}
          className={s.errors.title ? errorInputCls : inputCls}
        />
        {s.errors.title && <p className="flex items-center gap-1 text-red-400 text-xs mt-1"><AlertCircle size={12} />{s.errors.title}</p>}
      </div>
      {s.type !== 'promo' && (
        <div>
          <label className="block text-xs font-medium text-zinc-400 mb-1.5">Описание</label>
          <textarea
            value={s.description} onChange={(e) => s.setDescription(e.target.value)}
            placeholder="Текст баннера..." rows={3}
            className={inputCls + ' resize-none'}
          />
        </div>
      )}
      {s.type !== 'promo' && (
        <div>
          <label className="block text-xs font-medium text-zinc-400 mb-1.5">URL изображения</label>
          <input
            type="text" value={s.imageUrl}
            onChange={(e) => { s.setImageUrl(e.target.value); s.setErrors(p => ({...p, imageUrl: ''})); }}
            placeholder="https://..."
            className={s.errors.imageUrl ? errorInputCls : inputCls}
          />
          {s.errors.imageUrl && <p className="flex items-center gap-1 text-red-400 text-xs mt-1"><AlertCircle size={12} />{s.errors.imageUrl}</p>}
        </div>
      )}
      {s.type === 'promo' && (
        <div>
          <label className="block text-xs font-medium text-zinc-400 mb-1.5">Ссылка *</label>
          <input
            type="text" value={s.actionUrl}
            onChange={(e) => { s.setActionUrl(e.target.value); s.setErrors(p => ({...p, actionUrl: ''})); }}
            placeholder="https://..."
            className={s.errors.actionUrl ? errorInputCls : inputCls}
          />
          {s.errors.actionUrl && <p className="flex items-center gap-1 text-red-400 text-xs mt-1"><AlertCircle size={12} />{s.errors.actionUrl}</p>}
          <p className="text-zinc-600 text-[11px] mt-1">При нажатии пользователь перейдёт по этой ссылке</p>
        </div>
      )}
    </>
  );
};
