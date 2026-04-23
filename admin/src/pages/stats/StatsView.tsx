import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { UserPlus, CalendarDays, Bell, AtSign, Briefcase, MessageCircle, RefreshCw, Loader2 } from 'lucide-react';
import { api } from '../../api/client';
import type { AdminStatsResponse } from '../../api/client';
import { StatsCard } from './components';

export const StatsView = () => {
  const [stats, setStats] = useState<AdminStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const load = async () => {
    setIsLoading(true);
    try {
      const data = await api.users.getStats();
      setStats(data);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const metrics = stats
    ? [
        { label: 'Сегодня', value: stats.new_today, icon: UserPlus },
        { label: 'За 7 дней', value: stats.new_week, icon: CalendarDays },
        { label: 'Уведомления', value: stats.with_notifications, icon: Bell },
        { label: 'С никнеймом', value: stats.with_nickname, icon: AtSign },
        { label: 'Брокер', value: stats.broker_accounts, icon: Briefcase },
        { label: 'Тикеты', value: stats.tickets_new, icon: MessageCircle },
      ]
    : [];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ type: 'spring', damping: 28, stiffness: 260 }}
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-lg font-bold text-white">Статистика</h1>
          <p className="text-zinc-500 text-xs mt-0.5">Общие показатели</p>
        </div>
        <button
          onClick={load}
          disabled={isLoading}
          className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center hover:bg-zinc-800 transition-colors disabled:opacity-40"
        >
          <RefreshCw size={13} className={`text-white ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {isLoading || !stats ? (
        <div className="flex justify-center py-20">
          <Loader2 size={24} className="text-zinc-600 animate-spin" />
        </div>
      ) : (
        <StatsCard
          totalUsers={stats.total_users}
          metrics={metrics}
        />
      )}
    </motion.div>
  );
};
