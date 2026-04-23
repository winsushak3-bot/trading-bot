import { create } from 'zustand';

export interface AppUser {
  id: number;
  username?: string;
  firstName?: string;
  lastName?: string;
  languageCode?: string;
}

interface AppState {
  user: AppUser | null;
  isFullscreen: boolean;
  activeMarket: 'crypto' | 'forex' | 'screener' | null;
  homeTiles: any[] | null;
  setUser: (user: AppUser | null) => void;
  setFullscreen: (isFullscreen: boolean) => void;
  setActiveMarket: (market: 'crypto' | 'forex' | 'screener' | null) => void;
  setHomeTiles: (tiles: any[]) => void;
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  isFullscreen: false,
  activeMarket: null,
  homeTiles: null,
  setUser: (user) => set({ user }),
  setFullscreen: (isFullscreen) => set({ isFullscreen }),
  setActiveMarket: (activeMarket) => set({ activeMarket }),
  setHomeTiles: (homeTiles) => set({ homeTiles }),
}));
