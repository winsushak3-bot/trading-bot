import { useEffect, useState } from 'react';

declare global {
  interface Window {
    Telegram?: {
      WebApp: any;
    };
  }
}

export const useWebApp = () => {
  const [webApp, setWebApp] = useState<any>(() => window.Telegram?.WebApp || null);
  const [user, setUser] = useState<any>(() => window.Telegram?.WebApp?.initDataUnsafe?.user || null);
  const [isTelegram, setIsTelegram] = useState(() => !!window.Telegram?.WebApp?.initData || !!(window as any).TelegramWebviewProxy);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const tg = window.Telegram?.WebApp;
    
    if (tg) {
      try {
        // Protect Telegram WebApp side effects from running in every component.
        if (!(window as any).__tg_webapp_initialized__) {
          tg.ready();

          if (tg.setHeaderColor) tg.setHeaderColor('#000000');
          if (tg.setBackgroundColor) tg.setBackgroundColor('#000000');

          // Don't expand on signal page — keep compact (half-screen) mode
          const isSignalPage = window.location.pathname.includes('/signal/') ||
            tg.initDataUnsafe?.start_param;
          if (!isSignalPage) {
            setTimeout(() => {
              if (tg.expand) tg.expand();
            }, 100);
          }

          (window as any).__tg_webapp_initialized__ = true;
        }
        
        setWebApp(tg);
        setIsTelegram(!!tg.initData || !!(window as any).TelegramWebviewProxy);
        setUser(tg.initDataUnsafe?.user || null);
      } catch (error) {
        console.error('Telegram WebApp initialization error:', error);
      }
    } else {
      console.warn('Telegram WebApp not available');
    }
  }, []);

  return {
    webApp,
    user,
    isTelegram,
  };
};
