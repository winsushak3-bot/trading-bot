import { Type, Palette, MousePointerClick } from 'lucide-react';

export const SIZE_OPTIONS = [
  { value: '1x1', label: '1×1', colSpan: 1, rowSpan: 1 },
  { value: '2x1', label: '2×1', colSpan: 2, rowSpan: 1 },
  { value: '2x2', label: '2×2', colSpan: 2, rowSpan: 2 },
  { value: '4x1', label: '4×1', colSpan: 4, rowSpan: 1 },
  { value: '4x2', label: '4×2', colSpan: 4, rowSpan: 2 },
];

export const BG_COLORS = [
  { value: '', label: 'По умолч.' },
  { value: '#18181b', label: 'Zinc 900' },
  { value: '#1e3a5f', label: 'Синий' },
  { value: '#1a2e1a', label: 'Зелёный' },
  { value: '#3b1a1a', label: 'Красный' },
  { value: '#2d1f4e', label: 'Фиолет' },
  { value: '#3d2e1a', label: 'Оранж' },
  { value: '#1a2d3d', label: 'Голубой' },
  { value: '#ffffff', label: 'Белый' },
];

export const TABS = [
  { id: 'content', label: 'Контент', icon: Type },
  { id: 'style', label: 'Стиль', icon: Palette },
  { id: 'action', label: 'Действие', icon: MousePointerClick },
] as const;

export type TabId = typeof TABS[number]['id'];

export const inputCls = "w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-white text-sm placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500 transition-colors";
export const errorInputCls = "w-full bg-zinc-800 border border-red-500/50 rounded-xl px-4 py-3 text-white text-sm placeholder:text-zinc-600 focus:outline-none focus:border-red-400 transition-colors";
