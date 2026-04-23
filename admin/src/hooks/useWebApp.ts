import { useEffect, useState } from 'react';

declare global {
  interface Window {
    Telegram?: {
      WebApp: any;
    };
  }
}

export const useWebApp = () => {
  const [webApp, setWebApp] = useState<any>(null);
  const [user, setUser] = useState<any>(null);
  const [isTelegram, setIsTelegram] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const init = () => {
      const tg = window.Telegram?.WebApp;
      if (!tg) return false;

      try {
        if (!(window as any).__tg_admin_initialized__) {
          tg.ready();
          if (tg.setHeaderColor) tg.setHeaderColor('#000000');
          if (tg.setBackgroundColor) tg.setBackgroundColor('#000000');
          if (tg.expand) tg.expand();
          (window as any).__tg_admin_initialized__ = true;
        }

        setWebApp(tg);
        const hasTg = !!tg.initData || !!tg.initDataUnsafe?.user;
        setIsTelegram(hasTg);
        setUser(tg.initDataUnsafe?.user || null);
        return hasTg;
      } catch (error) {
        console.error('Telegram WebApp initialization error:', error);
        return false;
      }
    };

    if (init()) {
      setIsLoading(false);
      return;
    }

    // Retry — SDK может инициализироваться не сразу
    let attempt = 0;
    const maxAttempts = 10;
    const interval = setInterval(() => {
      attempt++;
      if (init() || attempt >= maxAttempts) {
        clearInterval(interval);
        setIsLoading(false);
      }
    }, 200);

    return () => clearInterval(interval);
  }, []);

  return { webApp, user, isTelegram, isLoading };
};
