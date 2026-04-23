import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Blocks, Plus, RefreshCw, Loader2, Smartphone, Save, List, LayoutGrid } from 'lucide-react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragOverlay,
} from '@dnd-kit/core';
import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core';
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { api } from '../../api/client';
import type { HomeTile, HomeTileCreate, HomeTileUpdate } from '../../api/client';
import { TileEditor, LivePreview, GridTile, ListTile, DragGhost } from './components';
import { useToastStore } from '../../shared/ui';

/* ── Main View ────────────────────────────────────────── */
export const ConstructorView = () => {
  const [tiles, setTiles] = useState<HomeTile[]>([]);
  const serverTiles = useRef<HomeTile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [editingTile, setEditingTile] = useState<HomeTile | null>(null);
  const [showEditor, setShowEditor] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [activeDragId, setActiveDragId] = useState<number | null>(null);
  const toast = useToastStore((s) => s.add);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const isDirty = useCallback(() => {
    if (tiles.length !== serverTiles.current.length) return false;
    return tiles.some((t, i) => {
      const s = serverTiles.current[i];
      return t.id !== s.id || t.is_active !== s.is_active;
    });
  }, [tiles]);

  const loadTiles = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.tiles.getAll();
      setTiles(data);
      serverTiles.current = data;
    } catch (e: any) {
      toast(e?.message || 'Ошибка загрузки', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  useEffect(() => { loadTiles(); }, [loadTiles]);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveDragId(event.active.id as number);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveDragId(null);
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = tiles.findIndex(t => t.id === active.id);
    const newIndex = tiles.findIndex(t => t.id === over.id);
    if (oldIndex === -1 || newIndex === -1) return;
    const newTiles = [...tiles];
    const [moved] = newTiles.splice(oldIndex, 1);
    newTiles.splice(newIndex, 0, moved);
    setTiles(newTiles);
  };

  const handleToggleActive = (tile: HomeTile) => {
    setTiles(prev => prev.map(t => t.id === tile.id ? { ...t, is_active: !t.is_active } : t));
  };

  const handleSaveAll = async () => {
    setIsSaving(true);
    try {
      const orders = tiles.map((t, i) => ({ id: t.id, order: i }));
      await api.tiles.reorder(orders);

      for (const tile of tiles) {
        const server = serverTiles.current.find(s => s.id === tile.id);
        if (server && server.is_active !== tile.is_active) {
          await api.tiles.update(tile.id, { is_active: tile.is_active });
        }
      }

      toast('Все изменения сохранены');
      await loadTiles();
    } catch (e: any) {
      toast(e?.message || 'Ошибка сохранения', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDiscardChanges = () => {
    setTiles([...serverTiles.current]);
    toast('Изменения отменены', 'info');
  };

  const handleCreate = async (data: HomeTileCreate) => {
    try {
      await api.tiles.create(data);
      setShowEditor(false);
      setEditingTile(null);
      toast('Тайл создан');
      await loadTiles();
    } catch (e: any) {
      toast(e?.message || 'Ошибка создания', 'error');
    }
  };

  const handleUpdate = async (id: number, data: Partial<HomeTileCreate>) => {
    try {
      await api.tiles.update(id, data as HomeTileUpdate);
      setShowEditor(false);
      setEditingTile(null);
      toast('Тайл сохранён');
      await loadTiles();
    } catch (e: any) {
      toast(e?.message || 'Ошибка обновления', 'error');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.tiles.delete(id);
      setShowEditor(false);
      setEditingTile(null);
      toast('Тайл удалён');
      await loadTiles();
    } catch (e: any) {
      toast(e?.message || 'Ошибка удаления', 'error');
    }
  };

  const handleDuplicate = async (tile: HomeTile) => {
    try {
      await api.tiles.create({
        type: tile.type,
        size: tile.size,
        order: tiles.length,
        is_active: false,
        content: { ...tile.content, title: (tile.content?.title || '') + ' (копия)' },
      });
      toast('Тайл дублирован', 'info');
      await loadTiles();
    } catch (e: any) {
      toast(e?.message || 'Ошибка дублирования', 'error');
    }
  };

  const openNewEditor = () => { setEditingTile(null); setShowEditor(true); };
  const openEditEditor = (tile: HomeTile) => { setEditingTile(tile); setShowEditor(true); };
  const closeEditor = () => { setShowEditor(false); setEditingTile(null); };

  const activeCount = tiles.filter(t => t.is_active).length;
  const hasChanges = isDirty();
  const dragTile = activeDragId ? tiles.find(t => t.id === activeDragId) : null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ type: 'spring', damping: 28, stiffness: 260 }}
    >
      {/* Header */}
      <div className="mb-4 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-white">Конструктор</h1>
            <p className="text-zinc-500 text-xs mt-0.5">
              {tiles.length > 0
                ? `${tiles.length} тайлов · ${activeCount} активных`
                : 'Управление баннерами'}
            </p>
          </div>
          <button
            onClick={openNewEditor}
            className="h-9 px-3.5 rounded-xl bg-white text-black font-semibold text-xs flex items-center gap-1.5 hover:bg-zinc-200 transition-colors active:scale-[0.98]"
          >
            <Plus size={14} />
            Создать
          </button>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="flex bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={`w-9 h-9 flex items-center justify-center transition-colors ${viewMode === 'grid' ? 'bg-white text-black' : 'text-zinc-500 hover:text-white'}`}
            >
              <LayoutGrid size={14} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`w-9 h-9 flex items-center justify-center transition-colors ${viewMode === 'list' ? 'bg-white text-black' : 'text-zinc-500 hover:text-white'}`}
            >
              <List size={14} />
            </button>
          </div>
          <button
            onClick={() => setShowPreview(true)}
            disabled={tiles.length === 0}
            className="w-9 h-9 rounded-xl bg-white/5 border border-zinc-800 flex items-center justify-center hover:bg-white/10 transition-colors active:scale-95 disabled:opacity-30"
          >
            <Smartphone size={14} className="text-white" />
          </button>
          <button
            onClick={loadTiles}
            disabled={isLoading}
            className="w-9 h-9 rounded-xl bg-white/5 border border-zinc-800 flex items-center justify-center hover:bg-white/10 transition-colors active:scale-95 disabled:opacity-30"
          >
            <RefreshCw size={14} className={`text-white ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Content */}
      {isLoading && tiles.length === 0 ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 size={24} className="text-zinc-600 animate-spin" />
        </div>
      ) : tiles.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-20 h-20 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-5">
            <Blocks size={32} className="text-zinc-600" />
          </div>
          <p className="text-zinc-400 text-sm font-medium">Пока пусто</p>
          <p className="text-zinc-600 text-xs mt-1">Создайте первый баннер</p>
          <button
            onClick={openNewEditor}
            className="mt-5 px-5 py-2.5 rounded-xl bg-white text-black font-semibold text-sm flex items-center gap-1.5 hover:bg-zinc-200 transition-colors active:scale-[0.98]"
          >
            <Plus size={16} />
            Создать тайл
          </button>
        </div>
      ) : (
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
          <SortableContext items={tiles.map(t => t.id)} strategy={verticalListSortingStrategy}>
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-4 gap-2 auto-rows-[70px]">
                {tiles.map((tile) => (
                  <GridTile
                    key={tile.id}
                    tile={tile}
                    onEdit={openEditEditor}
                    onToggleActive={handleToggleActive}
                    onDuplicate={handleDuplicate}
                  />
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {tiles.map((tile) => (
                  <ListTile
                    key={tile.id}
                    tile={tile}
                    onEdit={openEditEditor}
                    onToggleActive={handleToggleActive}
                    onDuplicate={handleDuplicate}
                  />
                ))}
              </div>
            )}
          </SortableContext>
          <DragOverlay dropAnimation={null}>
            {dragTile && <DragGhost tile={dragTile} />}
          </DragOverlay>
        </DndContext>
      )}

      {/* Floating Save Bar */}
      <AnimatePresence>
        {hasChanges && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-24 left-4 right-4 z-30 flex justify-center"
          >
            <div className="flex items-center gap-3 bg-zinc-900/95 backdrop-blur-xl border border-zinc-700 rounded-2xl px-5 py-3 shadow-2xl max-w-md">
              <span className="text-zinc-400 text-sm">Есть несохранённые изменения</span>
              <button
                onClick={handleDiscardChanges}
                className="px-4 py-2 rounded-xl text-zinc-400 bg-zinc-800 hover:bg-zinc-700 text-sm font-medium transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleSaveAll}
                disabled={isSaving}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white text-black text-sm font-bold hover:bg-zinc-200 transition-colors active:scale-[0.98] disabled:opacity-50"
              >
                {isSaving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                Сохранить
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Editor modal */}
      <AnimatePresence>
        {showEditor && (
          <TileEditor
            tile={editingTile}
            nextOrder={tiles.length}
            onSave={handleCreate}
            onUpdate={handleUpdate}
            onDelete={handleDelete}
            onClose={closeEditor}
          />
        )}
      </AnimatePresence>

      {/* Live Preview */}
      <AnimatePresence>
        {showPreview && (
          <LivePreview tiles={tiles} onClose={() => setShowPreview(false)} />
        )}
      </AnimatePresence>
    </motion.div>
  );
};
