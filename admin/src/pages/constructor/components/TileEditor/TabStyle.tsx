import { X, Upload, AlertCircle, Image as ImageIcon } from 'lucide-react';
import type { EditorState } from './types';
import { SIZE_OPTIONS, BG_COLORS } from './constants';

type Props = Pick<EditorState,
  'type' | 'setType' | 'sizeKey' | 'setSizeKey' | 'isCube' |
  'bgColor' | 'setBgColor' | 'bgOpacity' | 'setBgOpacity' |
  'bgImage' | 'setBgImage' | 'bgImages' | 'setBgImages' |
  'autoRotate' | 'setAutoRotate' | 'rotationInterval' | 'setRotationInterval' |
  'isActive' | 'setIsActive' | 'errors' |
  'setShowCropModal' | 'setCropTargetIndex'
>;

export const TabStyle = (s: Props) => (
  <>
    <div>
      <label className="block text-xs font-medium text-zinc-400 mb-1.5">Тип</label>
      <div className="grid grid-cols-5 gap-1.5">
        {[
          { key: 'banner', label: 'Баннер', hint: 'Модалка' },
          { key: 'promo', label: 'Промо', hint: 'Ссылка' },
          { key: 'info', label: 'Инфо', hint: 'Статика' },
          { key: 'cube', label: 'Куб', hint: '2×2' },
          { key: 'cube_banner', label: 'Куб+', hint: '4×2' },
        ].map((t) => (
          <button
            key={t.key} onClick={() => s.setType(t.key)}
            className={`py-2 rounded-lg text-[11px] font-medium transition-all flex flex-col items-center gap-0.5 ${
              s.type === t.key ? 'bg-white text-black' : 'bg-zinc-800 text-zinc-400 border border-zinc-700 hover:border-zinc-500'
            }`}
          >
            <span>{t.label}</span>
            <span className={`text-[9px] ${s.type === t.key ? 'text-zinc-500' : 'text-zinc-600'}`}>{t.hint}</span>
          </button>
        ))}
      </div>
    </div>

    {!s.isCube && (
      <div>
        <label className="block text-xs font-medium text-zinc-400 mb-1.5">Размер</label>
        <div className="grid grid-cols-5 gap-2">
          {SIZE_OPTIONS.map((opt) => (
            <button
              key={opt.value} onClick={() => s.setSizeKey(opt.value)}
              className={`py-2.5 rounded-lg text-xs font-medium transition-all ${
                s.sizeKey === opt.value ? 'bg-white text-black' : 'bg-zinc-800 text-zinc-400 border border-zinc-700 hover:border-zinc-500'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>
    )}

    {s.isCube && (
      <div className="bg-zinc-800/50 rounded-xl px-3 py-2 text-xs text-zinc-500">
        Размер: <span className="text-zinc-300 font-medium">{s.type === 'cube' ? '2×2 (квадрат)' : '4×2 (баннер)'}</span> — зафиксирован для этого типа
      </div>
    )}

    {/* Multi-image for cube types */}
    {s.isCube && (
      <>
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-xs font-medium text-zinc-400">Изображения ({s.bgImages.length}/4) *</label>
            {s.bgImages.length < 4 && (
              <button
                onClick={() => { s.setCropTargetIndex(s.bgImages.length); s.setShowCropModal(true); }}
                className="flex items-center gap-1 text-xs text-zinc-400 hover:text-white transition-colors"
              >
                <Upload size={12} /> Добавить
              </button>
            )}
          </div>
          {s.bgImages.length === 0 ? (
            <button
              onClick={() => { s.setCropTargetIndex(0); s.setShowCropModal(true); }}
              className="w-full border-2 border-dashed border-zinc-700 rounded-xl py-8 flex flex-col items-center gap-2 hover:border-zinc-500 transition-colors group"
            >
              <Upload size={24} className="text-zinc-500 group-hover:text-zinc-300 transition-colors" />
              <span className="text-zinc-500 text-xs group-hover:text-zinc-300">Загрузите минимум 2 фото</span>
            </button>
          ) : (
            <div className="grid grid-cols-4 gap-2">
              {s.bgImages.map((img, i) => (
                <div key={i} className="relative aspect-square rounded-xl overflow-hidden border border-zinc-700 group">
                  <img src={img} alt="" className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center">
                    <button
                      onClick={() => s.setBgImages(prev => prev.filter((_, idx) => idx !== i))}
                      className="opacity-0 group-hover:opacity-100 w-6 h-6 rounded-full bg-red-500/80 flex items-center justify-center text-white transition-opacity"
                    >
                      <X size={12} />
                    </button>
                  </div>
                  <div className="absolute top-1 left-1 w-5 h-5 rounded-full bg-black/60 flex items-center justify-center text-white text-[10px] font-bold">
                    {i + 1}
                  </div>
                </div>
              ))}
              {s.bgImages.length < 4 && (
                <button
                  onClick={() => { s.setCropTargetIndex(s.bgImages.length); s.setShowCropModal(true); }}
                  className="aspect-square rounded-xl border-2 border-dashed border-zinc-700 flex items-center justify-center hover:border-zinc-500 transition-colors"
                >
                  <Upload size={16} className="text-zinc-600" />
                </button>
              )}
            </div>
          )}
          {s.errors.bgImages && <p className="flex items-center gap-1 text-red-400 text-xs mt-1"><AlertCircle size={12} />{s.errors.bgImages}</p>}
        </div>
        <div>
          <div className="flex items-center justify-between py-2">
            <span className="text-sm text-zinc-300">Авто-прокрутка</span>
            <button
              onClick={() => s.setAutoRotate(!s.autoRotate)}
              className={`w-11 h-6 rounded-full transition-colors relative ${s.autoRotate ? 'bg-white' : 'bg-zinc-700'}`}
            >
              <div className={`absolute top-0.5 w-5 h-5 rounded-full transition-all ${s.autoRotate ? 'left-[22px] bg-black' : 'left-0.5 bg-zinc-400'}`} />
            </button>
          </div>
          {s.autoRotate && (
            <>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-medium text-zinc-400">Интервал вращения — {s.rotationInterval}с</label>
                <span className="text-xs text-zinc-600 font-mono">{s.rotationInterval}с</span>
              </div>
              <input
                type="range" min={1} max={10} step={0.5}
                value={s.rotationInterval}
                onChange={(e) => s.setRotationInterval(Number(e.target.value))}
                className="w-full h-1.5 bg-zinc-700 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-grab"
              />
            </>
          )}
          <p className="text-zinc-600 text-[11px] mt-1">{s.autoRotate ? 'Куб вращается автоматически + свайп' : 'Только ручная прокрутка свайпом'}</p>
        </div>
      </>
    )}

    {/* Background image */}
    {!s.isCube && (
      <div>
        <label className="block text-xs font-medium text-zinc-400 mb-1.5">Фон плиты</label>
        {s.bgImage ? (
          <div className="relative rounded-xl overflow-hidden border border-zinc-700 h-24">
            <img src={s.bgImage} alt="" className="w-full h-full object-cover" onError={(e) => (e.currentTarget.style.display = 'none')} />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
            <div className="absolute bottom-2 left-2 right-2 flex gap-2">
              <button
                onClick={() => s.setShowCropModal(true)}
                className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg bg-white/20 backdrop-blur text-white text-xs font-medium hover:bg-white/30 transition-colors"
              >
                <ImageIcon size={12} /> Заменить
              </button>
              <button
                onClick={() => s.setBgImage('')}
                className="px-3 py-1.5 rounded-lg bg-red-500/30 backdrop-blur text-red-300 text-xs font-medium hover:bg-red-500/50 transition-colors"
              >
                <X size={12} />
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => s.setShowCropModal(true)}
            className="w-full border-2 border-dashed border-zinc-700 rounded-xl py-6 flex flex-col items-center gap-2 hover:border-zinc-500 transition-colors group"
          >
            <Upload size={20} className="text-zinc-500 group-hover:text-zinc-300 transition-colors" />
            <span className="text-zinc-500 text-xs group-hover:text-zinc-300 transition-colors">Загрузить фото или видео</span>
          </button>
        )}
        <p className="text-zinc-600 text-[11px] mt-1.5">Изображение заполнит всю плиту. Можно выбрать область.</p>
      </div>
    )}

    {/* Color */}
    <div>
      <label className="block text-xs font-medium text-zinc-400 mb-1.5">Цвет подложки</label>
      <div className="grid grid-cols-3 gap-2">
        {BG_COLORS.map((c) => (
          <button
            key={c.value} onClick={() => s.setBgColor(c.value)}
            className={`flex items-center gap-2 py-2 px-3 rounded-lg text-xs font-medium transition-all ${
              s.bgColor === c.value ? 'ring-2 ring-white ring-offset-1 ring-offset-zinc-900' : 'hover:bg-zinc-800'
            }`}
          >
            <div
              className="w-5 h-5 rounded-md border border-zinc-600 shrink-0"
              style={{ backgroundColor: c.value || '#18181b' }}
            />
            <span className="text-zinc-300 truncate">{c.label}</span>
          </button>
        ))}
      </div>
    </div>

    {/* Opacity */}
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <label className="block text-xs font-medium text-zinc-400">Прозрачность фона — {s.bgOpacity}%</label>
        <span className="text-xs text-zinc-600 font-mono">{s.bgOpacity}%</span>
      </div>
      <input
        type="range" min={10} max={100} step={5}
        value={s.bgOpacity}
        onChange={(e) => s.setBgOpacity(Number(e.target.value))}
        className="w-full h-1.5 bg-zinc-700 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-grab"
      />
    </div>

    <div className="flex items-center justify-between py-2">
      <span className="text-sm text-zinc-300">Активен</span>
      <button
        onClick={() => s.setIsActive(!s.isActive)}
        className={`w-11 h-6 rounded-full transition-colors relative ${s.isActive ? 'bg-white' : 'bg-zinc-700'}`}
      >
        <div className={`absolute top-0.5 w-5 h-5 rounded-full transition-all ${s.isActive ? 'left-[22px] bg-black' : 'left-0.5 bg-zinc-400'}`} />
      </button>
    </div>
  </>
);
