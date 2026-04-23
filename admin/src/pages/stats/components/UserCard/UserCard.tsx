import type { AdminUser } from '../../../../api/client';

const LANG_FLAG: Record<string, string> = { ru: '🇷🇺', en: '🇬🇧', ua: '🇺🇦' };

const formatDate = (iso: string) => {
  const d = new Date(iso);
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: '2-digit' });
};

interface Props {
  user: AdminUser;
}

export const UserCard = ({ user }: Props) => {
  const initials = (user.username || user.nickname || String(user.tg_id)).slice(0, 2).toUpperCase();

  return (
    <div className="flex items-center gap-3 py-3 border-b border-zinc-800/60 last:border-0">
      <div className="w-9 h-9 rounded-xl bg-zinc-800 flex items-center justify-center shrink-0 text-xs font-bold text-zinc-300">
        {initials}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <span className="text-sm font-medium text-white truncate">
            {user.username ? `@${user.username}` : user.nickname ?? '—'}
          </span>
          {user.username && user.nickname && (
            <span className="text-zinc-500 text-xs truncate">· {user.nickname}</span>
          )}
          <span className="ml-auto text-xs shrink-0">{LANG_FLAG[user.language] ?? user.language}</span>
        </div>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-zinc-600 text-[11px]">{user.tg_id}</span>
          {user.referrals_count > 0 && (
            <span className="text-zinc-500 text-[11px]">· {user.referrals_count} реф.</span>
          )}
          <span className="ml-auto text-zinc-600 text-[11px]">{formatDate(user.created_at)}</span>
        </div>
      </div>
    </div>
  );
};
