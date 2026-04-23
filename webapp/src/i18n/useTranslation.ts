import { create } from 'zustand';
import { translations, defaultLanguage, Language } from './i18n';

interface I18nStore {
  language: Language;
  setLanguage: (lang: Language) => void;
}

const STORAGE_KEY = 'app_language';

const getSavedLanguage = (): Language => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'ru' || saved === 'en' || saved === 'ua') return saved;
  } catch {}
  return defaultLanguage;
};

export const useI18nStore = create<I18nStore>((set) => ({
  language: getSavedLanguage(),
  setLanguage: (lang) => {
    try { localStorage.setItem(STORAGE_KEY, lang); } catch {}
    set({ language: lang });
  },
}));

export const useTranslation = () => {
  const { language, setLanguage } = useI18nStore();

  const t = (key: string): string => {
    const keys = key.split('.');
    let value: any = translations[language];

    for (const k of keys) {
      if (value && typeof value === 'object') {
        value = value[k];
      } else {
        return key;
      }
    }

    return typeof value === 'string' ? value : key;
  };

  return { t, language, setLanguage };
};
