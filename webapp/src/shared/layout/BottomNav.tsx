import { Home, TrendingUp, Wallet, Headphones, User } from 'lucide-react';
import { useTranslation } from '../../i18n';
import { haptic } from '../../utils';

interface BottomNavProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export const BottomNav = ({ activeTab, onTabChange }: BottomNavProps) => {
  const { t } = useTranslation();

  const navItems = [
    { id: 'home', icon: Home, label: t('nav.home') },
    { id: 'wallet', icon: Wallet, label: t('nav.wallet') },
    { id: 'trade', icon: TrendingUp, label: t('nav.trade') },
    { id: 'support', icon: Headphones, label: t('nav.support') },
    { id: 'profile', icon: User, label: t('nav.profile') },
  ];

  return (
    <div className="fixed left-4 right-4 z-40" style={{ bottom: 'calc(16px + var(--safe-bottom, 0px))' }}>
        <div className="relative bg-zinc-900/95 backdrop-blur-xl border-2 border-zinc-700 rounded-3xl px-3 py-2.5 shadow-2xl max-w-md mx-auto overflow-visible">
          <div className="flex justify-between items-center relative z-10 h-[50px]">
            {navItems.map((item) => {
              const isActive = activeTab === item.id;
              
              return (
                <button
                    key={item.id}
                    onClick={() => {
                      haptic.light();
                      onTabChange(item.id);
                    }}
                    className={`flex flex-col items-center gap-1 py-2 px-2 rounded-xl transition-colors duration-200 ${
                      isActive ? 'text-white' : 'text-zinc-500 hover:text-zinc-300'
                    }`}
                >
                    <item.icon 
                        size={20}
                        strokeWidth={isActive ? 2.5 : 2}
                        className={`transition-transform duration-200 mb-1 ${isActive ? 'scale-110' : 'scale-100'}`}
                    />
                    <span className="text-[10px] font-medium">{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
    </div>
  );
};
