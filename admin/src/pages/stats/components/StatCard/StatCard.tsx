import { Users } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface Metric {
  label: string;
  value: number | string;
  icon: LucideIcon;
}

interface Props {
  totalUsers: number;
  metrics: Metric[];
}

export const StatsCard = ({ totalUsers, metrics }: Props) => (
  <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 flex flex-col gap-5">
    {/* Hero — общее число пользователей */}
    <div className="flex items-center gap-4">
      <div className="w-12 h-12 rounded-2xl bg-indigo-500/15 flex items-center justify-center shrink-0">
        <Users size={22} className="text-indigo-400" />
      </div>
      <div>
        <p className="text-zinc-500 text-xs font-medium">В проекте</p>
        <span className="text-3xl font-extrabold text-white leading-tight">
          {totalUsers.toLocaleString('ru-RU')}
        </span>
        <p className="text-zinc-600 text-[11px]">пользователей</p>
      </div>
    </div>

    {/* Разделитель */}
    <div className="h-px bg-zinc-800" />

    {/* Метрики сеткой 3×2 */}
    <div className="grid grid-cols-3 gap-x-3 gap-y-4">
      {metrics.map((m) => {
        const Icon = m.icon;
        return (
          <div key={m.label} className="flex flex-col items-center text-center gap-1.5">
            <div className="w-8 h-8 rounded-xl bg-zinc-800 flex items-center justify-center">
              <Icon size={14} className="text-zinc-400" />
            </div>
            <span className="text-base font-bold text-white leading-none">{m.value}</span>
            <span className="text-zinc-500 text-[10px] leading-tight">{m.label}</span>
          </div>
        );
      })}
    </div>
  </div>
);
