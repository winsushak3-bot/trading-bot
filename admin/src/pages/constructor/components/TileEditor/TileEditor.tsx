import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save, Trash2 } from 'lucide-react';
import type { HomeTile, HomeTileCreate, ExpandBlock } from '../../../../api/client';
import { ImageCropModal } from '../ImageCropModal/ImageCropModal';
import { TABS, SIZE_OPTIONS, TabId } from './constants';
import { TabContent } from './TabContent';
import { TabStyle } from './TabStyle';
import { TabAction } from './TabAction';
import { TilePreview } from './TilePreview';

interface TileEditorProps {
  tile: HomeTile | null;
  nextOrder: number;
  onSave: (data: HomeTileCreate) => void;
  onUpdate: (id: number, data: Partial<HomeTileCreate>) => void;
  onDelete: (id: number) => void;
  onClose: () => void;
}

export const TileEditor = ({ tile, nextOrder, onSave, onUpdate, onDelete, onClose }: TileEditorProps) => {
  const isEdit = !!tile;

  const [tab, setTab] = useState<TabId>('content');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [actionUrl, setActionUrl] = useState('');
  const [actionText, setActionText] = useState('');
  const [sizeKey, setSizeKey] = useState('2x1');
  const [bgColor, setBgColor] = useState('');
  const [bgOpacity, setBgOpacity] = useState(100);
  const [bgImage, setBgImage] = useState('');
  const [bgImages, setBgImages] = useState<string[]>([]);
  const [rotationInterval, setRotationInterval] = useState(3);
  const [autoRotate, setAutoRotate] = useState(true);
  const [expandable, setExpandable] = useState(false);
  const [expandBlocks, setExpandBlocks] = useState<ExpandBlock[]>([]);
  const [isActive, setIsActive] = useState(true);
  const [type, setType] = useState('banner');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showCropModal, setShowCropModal] = useState(false);
  const [cropTargetIndex, setCropTargetIndex] = useState(-1);
  const [expandCropIndex, setExpandCropIndex] = useState(-1);

  const isCube = type === 'cube' || type === 'cube_banner';

  useEffect(() => {
    if (tile) {
      setTitle(tile.content?.title || '');
      setDescription(tile.content?.description || '');
      setImageUrl(tile.content?.image_url || '');
      setActionUrl(tile.content?.action_url || '');
      setActionText(tile.content?.action_text || '');
      setBgColor(tile.content?.bg_color || '');
      setBgOpacity(tile.content?.bg_opacity ?? 100);
      setBgImage(tile.content?.bg_image || '');
      setBgImages(tile.content?.bg_images || []);
      setRotationInterval(tile.content?.rotation_interval || 3);
      setAutoRotate(tile.content?.auto_rotate !== false);
      setExpandable(tile.content?.expandable || false);
      setExpandBlocks(tile.content?.expand_blocks || []);
      setIsActive(tile.is_active);
      setType(tile.type);
      const cs = tile.content?.colSpan || 2;
      const rs = tile.content?.rowSpan || 1;
      const found = SIZE_OPTIONS.find(s => s.colSpan === cs && s.rowSpan === rs);
      setSizeKey(found?.value || '2x1');
    }
  }, [tile]);

  const validate = (): boolean => {
    const e: Record<string, string> = {};
    if (!isCube && !title.trim()) e.title = 'Заголовок обязателен';
    if (imageUrl && !imageUrl.startsWith('http')) e.imageUrl = 'URL должен начинаться с http';
    if (type === 'promo' && !actionUrl.trim()) e.actionUrl = 'Ссылка обязательна для промо';
    if (actionUrl && !actionUrl.startsWith('http')) e.actionUrl = 'URL должен начинаться с http';
    if (isCube && bgImages.length < 2) e.bgImages = 'Добавьте минимум 2 изображения';
    setErrors(e);
    if (Object.keys(e).length > 0) {
      if (e.title || e.imageUrl) setTab('content');
      else if (e.bgImages) setTab('style');
      else if (e.actionUrl) setTab('action');
    }
    return Object.keys(e).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) return;
    const cubeSizeKey = type === 'cube' ? '2x2' : type === 'cube_banner' ? '4x2' : sizeKey;
    const size = SIZE_OPTIONS.find(s => s.value === cubeSizeKey) || SIZE_OPTIONS.find(s => s.value === sizeKey)!;
    const payload: HomeTileCreate = {
      type,
      size: cubeSizeKey,
      order: tile?.order ?? nextOrder,
      is_active: isActive,
      content: {
        title: title.trim() || undefined,
        description: description.trim() || undefined,
        image_url: imageUrl.trim() || undefined,
        action_url: actionUrl.trim() || undefined,
        action_text: actionText.trim() || undefined,
        colSpan: size.colSpan,
        rowSpan: size.rowSpan,
        bg_color: bgColor || undefined,
        bg_opacity: bgOpacity < 100 ? bgOpacity : undefined,
        bg_image: bgImage.trim() || undefined,
        bg_images: isCube && bgImages.length > 0 ? bgImages : undefined,
        rotation_interval: isCube ? rotationInterval : undefined,
        auto_rotate: isCube ? autoRotate : undefined,
        expandable: expandable ? true : undefined,
        expand_blocks: expandable && expandBlocks.length > 0 ? expandBlocks : undefined,
      },
    };
    if (isEdit && tile) onUpdate(tile.id, payload);
    else onSave(payload);
  };

  const effectiveSizeKey = type === 'cube' ? '2x2' : type === 'cube_banner' ? '4x2' : sizeKey;
  const curSize = SIZE_OPTIONS.find(s => s.value === effectiveSizeKey) || SIZE_OPTIONS.find(s => s.value === sizeKey)!;

  const shared = {
    title, setTitle, description, setDescription, imageUrl, setImageUrl,
    actionUrl, setActionUrl, actionText, setActionText,
    sizeKey, setSizeKey, bgColor, setBgColor, bgOpacity, setBgOpacity,
    bgImage, setBgImage, bgImages, setBgImages,
    rotationInterval, setRotationInterval, autoRotate, setAutoRotate,
    expandable, setExpandable, expandBlocks, setExpandBlocks,
    isActive, setIsActive, type, setType, isCube,
    errors, setErrors,
    setShowCropModal, setCropTargetIndex, setExpandCropIndex,
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-start justify-center pt-4 px-4 overflow-y-auto"
    >
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 30, scale: 0.97 }}
        className="relative z-10 w-full max-w-lg bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden flex flex-col my-4"
        style={{ maxHeight: 'calc(100vh - 2rem)' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800 shrink-0">
          <h2 className="text-lg font-bold text-white">{isEdit ? 'Редактировать' : 'Новый тайл'}</h2>
          <button onClick={onClose} className="text-zinc-500 hover:text-white transition-colors"><X size={20} /></button>
        </div>

        {/* Preview */}
        <TilePreview
          isCube={isCube}
          title={title}
          description={description}
          imageUrl={imageUrl}
          bgImage={bgImage}
          bgImages={bgImages}
          bgColor={bgColor}
          bgOpacity={bgOpacity}
          isWhiteBg={bgColor === '#ffffff'}
          colSpan={curSize.colSpan}
          rowSpan={curSize.rowSpan}
        />

        {/* Tabs */}
        <div className="flex gap-1 px-5 pt-3 pb-1 shrink-0">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                tab === t.id ? 'bg-white text-black' : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <t.icon size={13} />
              {t.label}
            </button>
          ))}
        </div>

        {/* Form body */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4 min-h-0">
          {tab === 'content' && <TabContent {...shared} />}
          {tab === 'style' && <TabStyle {...shared} />}
          {tab === 'action' && <TabAction {...shared} />}
        </div>

        {/* Footer */}
        <div className="flex items-center gap-3 px-5 py-4 border-t border-zinc-800 shrink-0">
          {isEdit && !showDeleteConfirm && (
            <button onClick={() => setShowDeleteConfirm(true)} className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-red-400 bg-red-500/10 hover:bg-red-500/20 text-sm font-medium transition-colors">
              <Trash2 size={16} />
            </button>
          )}
          {showDeleteConfirm && (
            <div className="flex items-center gap-2">
              <span className="text-red-400 text-xs">Удалить?</span>
              <button onClick={() => tile && onDelete(tile.id)} className="px-3 py-1.5 rounded-lg bg-red-500 text-white text-xs font-bold hover:bg-red-600 transition-colors">Да</button>
              <button onClick={() => setShowDeleteConfirm(false)} className="px-3 py-1.5 rounded-lg bg-zinc-800 text-zinc-400 text-xs font-medium hover:bg-zinc-700 transition-colors">Нет</button>
            </div>
          )}
          <div className="flex-1" />
          <button onClick={onClose} className="px-5 py-2.5 rounded-xl text-zinc-400 bg-zinc-800 hover:bg-zinc-700 text-sm font-medium transition-colors">Отмена</button>
          <button onClick={handleSubmit} className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-white text-black text-sm font-bold hover:bg-zinc-200 transition-colors active:scale-[0.98]">
            <Save size={16} />
            {isEdit ? 'Сохранить' : 'Создать'}
          </button>
        </div>
      </motion.div>

      {/* Crop Modal */}
      <AnimatePresence>
        {showCropModal && (
          <ImageCropModal
            aspect={expandCropIndex >= 0 ? 16 / 9 : isCube ? (type === 'cube' ? 1 : 2) : (curSize.colSpan / curSize.rowSpan)}
            onComplete={(url) => {
              if (expandCropIndex >= 0) {
                const arr = [...expandBlocks];
                arr[expandCropIndex] = { ...arr[expandCropIndex], value: url };
                setExpandBlocks(arr);
                setExpandCropIndex(-1);
              } else if (isCube) {
                setBgImages(prev => [...prev, url]);
              } else {
                setBgImage(url);
              }
              setShowCropModal(false);
            }}
            onClose={() => { setShowCropModal(false); setExpandCropIndex(-1); }}
          />
        )}
      </AnimatePresence>
    </motion.div>
  );
};
