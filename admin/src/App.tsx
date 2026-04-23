import { useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { useAdminStore } from './store/useAdminStore';
import { useWebApp } from './hooks/useWebApp';
import { AdminBottomNav } from './shared/layout';
import { ToastContainer } from './shared/ui';
import { ConstructorView, StatsView, SupportView } from './pages';
import { LoginView } from './pages/login/LoginView';

export default function App() {
  const { activeTab, isAuthenticated, setTelegramAuth, adminToken } = useAdminStore();
  const { isTelegram, isLoading } = useWebApp();

  useEffect(() => {
    const handleUnauthorized = () => {
      useAdminStore.setState({ isAuthenticated: false, authMode: 'none', adminToken: null });
    };
    window.addEventListener('admin:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('admin:unauthorized', handleUnauthorized);
  }, []);

  useEffect(() => {
    if (isLoading) return;
    // Авто-авторизация через Telegram initData
    if (isTelegram && !isAuthenticated) {
      setTelegramAuth();
      return;
    }
    // Авто-авторизация через сохранённый токен
    if (!isAuthenticated && adminToken) {
      useAdminStore.setState({ isAuthenticated: true, authMode: 'token' });
    }
  }, [isLoading, isTelegram, isAuthenticated, adminToken, setTelegramAuth]);

  if (isLoading) {
    return (
      <div className="bg-black min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-zinc-700 border-t-white rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginView />;
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'stats':
        return <StatsView key="stats" />;
      case 'constructor':
        return <ConstructorView key="constructor" />;
      case 'support':
        return <SupportView key="support" />;
      default:
        return <StatsView key="default" />;
    }
  };

  return (
    <div className="bg-black min-h-screen text-zinc-100 font-sans select-none">
      <ToastContainer />
      <div className="min-h-screen pb-24">
        <div className="p-4 pt-6">
          <AnimatePresence mode="wait">
            {renderContent()}
          </AnimatePresence>
        </div>

        <AdminBottomNav />
      </div>
    </div>
  );
}
