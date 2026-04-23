import { useAppStore } from '../../../../store';
import { NotificationButton } from '../NotificationButton';

export const ProfileCard = () => {
  const user = useAppStore((s) => s.user);
  const displayName = user?.username ?? user?.firstName ?? 'User';
  const avatar = displayName[0]?.toUpperCase() ?? 'U';

  return (
    <div className="bg-zinc-900 border-2 border-zinc-700 rounded-2xl p-4 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-20 h-20 bg-gradient-to-br from-white/5 to-transparent rounded-br-full pointer-events-none" />
      <div className="flex items-center justify-between relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-16 h-16 bg-gradient-to-br from-zinc-700 to-zinc-800 rounded-2xl flex items-center justify-center text-2xl font-bold text-white border border-zinc-700">
            {avatar}
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">{displayName}</h3>
            {user?.id && <p className="text-zinc-500 text-sm">ID: {user.id}</p>}
          </div>
        </div>
        <NotificationButton />
      </div>
    </div>
  );
};
