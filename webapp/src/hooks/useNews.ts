import { useState, useEffect, useRef } from 'react';
import { api } from '../api/client';

export interface NewsArticle {
  id: string;
  source: string;
  title: string;
  summary: string;
  image: string;
  time: string;
  publishedAt: string;
  readTime: string;
  link: string;
}

interface NewsState {
  items: NewsArticle[];
  isLoading: boolean;
  error: string | null;
}

const CACHE_TTL = 5 * 60 * 1000; // 5 min client-side cache
const cache: Record<string, { ts: number; items: NewsArticle[] }> = {};

export const useNews = (category: 'crypto' | 'forex') => {
  const [state, setState] = useState<NewsState>({
    items: cache[category]?.items || [],
    isLoading: !cache[category],
    error: null,
  });
  const abortRef = useRef(false);

  useEffect(() => {
    abortRef.current = false;

    const cached = cache[category];
    if (cached && Date.now() - cached.ts < CACHE_TTL) {
      setState({ items: cached.items, isLoading: false, error: null });
      return;
    }

    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    const fetchNews = async () => {
      try {
        const data = category === 'crypto'
          ? await api.news.getCrypto()
          : await api.news.getForex();

        if (abortRef.current) return;

        const items: NewsArticle[] = data.items || [];
        cache[category] = { ts: Date.now(), items };
        setState({ items, isLoading: false, error: null });
      } catch (e: any) {
        if (abortRef.current) return;
        console.error(`Failed to load ${category} news:`, e);
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: e?.message || 'Failed to load news',
        }));
      }
    };

    fetchNews();
    return () => { abortRef.current = true; };
  }, [category]);

  return state;
};
