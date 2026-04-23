import { create } from 'zustand';
import { apiClient } from '../api/client';

type AuthMode = 'none' | 'telegram' | 'token';

interface AdminState {
  activeTab: string;
  setActiveTab: (tab: string) => void;

  // Auth
  isAuthenticated: boolean;
  authMode: AuthMode;
  adminToken: string | null;

  setTelegramAuth: () => void;
  login: (telegramId: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const STORAGE_KEY = 'admin_token';

export const useAdminStore = create<AdminState>((set) => ({
  activeTab: 'stats',
  setActiveTab: (tab: string) => set({ activeTab: tab }),

  // Auth
  isAuthenticated: false,
  authMode: 'none',
  adminToken: localStorage.getItem(STORAGE_KEY),

  setTelegramAuth: () => {
    set({ isAuthenticated: true, authMode: 'telegram', adminToken: null });
  },

  login: async (telegramId: string, password: string): Promise<boolean> => {
    try {
      const res = await apiClient.post('/admin/auth/login', {
        telegram_id: Number(telegramId),
        password,
      });
      const token: string = res.data.token;
      localStorage.setItem(STORAGE_KEY, token);
      set({ isAuthenticated: true, authMode: 'token', adminToken: token });
      return true;
    } catch {
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem(STORAGE_KEY);
    set({ isAuthenticated: false, authMode: 'none', adminToken: null });
  },
}));
