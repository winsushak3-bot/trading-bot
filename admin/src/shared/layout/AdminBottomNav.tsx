import { Blocks, Home, MessageCircle } from 'lucide-react';
import { useAdminStore } from '../../store/useAdminStore';

export const AdminBottomNav = () => {
  const { activeTab, setActiveTab } = useAdminStore();

  const navItems = [
    { id: 'stats', icon: Home, label: 'Статистика' },
    { id: 'constructor', icon: Blocks, label: 'Конструктор' },
    { id: 'support', icon: MessageCircle, label: 'Поддержка' },
  ];

  return (
    <div className="fixed left-4 right-4 z-40 bottom-4">
      <div className="relative bg-zinc-900/95 backdrop-blur-xl border-2 border-zinc-700 rounded-3xl px-3 py-2.5 shadow-2xl max-w-md mx-auto overflow-visible">
        <div className="flex justify-center items-center relative z-10 h-[50px]">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex-1 flex flex-col items-center gap-1 py-2 px-2 rounded-xl transition-colors duration-200 ${
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
