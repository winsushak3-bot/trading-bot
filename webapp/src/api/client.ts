import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const getInitData = (): string => {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return window.Telegram.WebApp.initData || '';
  }
  return '';
};

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true',
  },
  timeout: 10000,
});

apiClient.interceptors.request.use((config) => {
  const initData = getInitData();
  if (initData) {
    config.headers.Authorization = `tma ${initData}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const api = {
  support: {
    getMyTicket: async () => {
      const response = await apiClient.get('/support/my-ticket');
      return response.data;
    },
    createTicket: async () => {
      const response = await apiClient.post('/support/my-ticket');
      return response.data;
    },
    sendMessage: async (ticketId: number, text: string) => {
      const response = await apiClient.post(`/support/ticket/${ticketId}/message`, { text });
      return response.data;
    }
  },

  home: {
    getLayout: async () => {
      const response = await apiClient.get('/home/layout');
      return response.data;
    }
  },

  news: {
    getCrypto: async () => {
      const response = await apiClient.get('/news/crypto');
      return response.data;
    },
    getForex: async () => {
      const response = await apiClient.get('/news/forex');
      return response.data;
    },
    getArticle: async (url: string) => {
      const response = await apiClient.get('/news/article', { params: { url } });
      return response.data as { content: string; images: string[] };
    },
  }
};
