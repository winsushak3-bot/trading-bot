import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const STORAGE_KEY = 'admin_token';

const getAuthHeader = (): string | null => {
  // 1. Telegram initData (приоритет)
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    const initData = window.Telegram.WebApp.initData;
    if (initData) return `tma ${initData}`;
  }
  // 2. Admin token из localStorage
  const token = localStorage.getItem(STORAGE_KEY);
  if (token) return `Admin ${token}`;
  return null;
};

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

apiClient.interceptors.request.use((cfg) => {
  const auth = getAuthHeader();
  if (auth) {
    cfg.headers = cfg.headers ?? {};
    (cfg.headers as Record<string, string>).Authorization = auth;
  }
  return cfg;
});

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('API Error:', err.response?.data || err.message);
    if (err.response?.status === 401) {
      localStorage.removeItem(STORAGE_KEY);
      window.dispatchEvent(new CustomEvent('admin:unauthorized'));
    }
    return Promise.reject(err);
  },
);

export interface TileContent {
  title?: string;
  description?: string;
  image_url?: string;
  action_url?: string;
  action_text?: string;
  colSpan?: number;
  rowSpan?: number;
  bg_color?: string;
  bg_opacity?: number;
  bg_image?: string;
  bg_images?: string[];
  rotation_interval?: number;
  auto_rotate?: boolean;
  expandable?: boolean;
  expand_blocks?: ExpandBlock[];
}

export interface ExpandBlock {
  type: 'text' | 'image' | 'video' | 'link';
  value: string;
  label?: string;
}

export interface HomeTile {
  id: number;
  type: string;
  size: string;
  order: number;
  is_active: boolean;
  content: TileContent;
}

export interface HomeTileCreate {
  type: string;
  size: string;
  order: number;
  is_active: boolean;
  content: HomeTile['content'];
}

export interface HomeTileUpdate {
  type?: string;
  size?: string;
  order?: number;
  is_active?: boolean;
  content?: HomeTile['content'];
}

export interface AdminUser {
  id: number;
  tg_id: number;
  username: string | null;
  nickname: string | null;
  language: string;
  referrals_count: number;
  notifications_enabled: boolean;
  created_at: string;
}

export interface AdminUsersListResponse {
  users: AdminUser[];
  total: number;
}

export interface AdminStatsResponse {
  total_users: number;
  new_today: number;
  new_week: number;
  with_notifications: number;
  with_nickname: number;
  broker_accounts: number;
  tickets_new: number;
}

export const api = {
  uploads: {
    upload: async (file: Blob, filename: string): Promise<string> => {
      const form = new FormData();
      form.append('file', file, filename);
      const res = await apiClient.post('/uploads/admin/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data.url;
    },
  },
  users: {
    getStats: async (): Promise<AdminStatsResponse> => {
      const res = await apiClient.get('/users/admin/stats');
      return res.data;
    },
    getAll: async (limit = 20, offset = 0, search = ''): Promise<AdminUsersListResponse> => {
      const res = await apiClient.get('/users/admin/users', { params: { limit, offset, search } });
      return res.data;
    },
  },
  tiles: {
    getAll: async (): Promise<HomeTile[]> => {
      const res = await apiClient.get('/home/admin/layout');
      return res.data;
    },
    create: async (data: HomeTileCreate): Promise<HomeTile> => {
      const res = await apiClient.post('/home/admin/layout', data);
      return res.data;
    },
    update: async (id: number, data: HomeTileUpdate): Promise<HomeTile> => {
      const res = await apiClient.put(`/home/admin/layout/${id}`, data);
      return res.data;
    },
    delete: async (id: number): Promise<void> => {
      await apiClient.delete(`/home/admin/layout/${id}`);
    },
    reorder: async (orders: { id: number; order: number }[]): Promise<void> => {
      await apiClient.post('/home/admin/layout/reorder', orders);
    },
  },
};
