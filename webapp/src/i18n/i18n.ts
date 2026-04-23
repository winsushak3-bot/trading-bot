import ruTranslations from './locales/ru.json';
import enTranslations from './locales/en.json';
import uaTranslations from './locales/ua.json';

export type Language = 'ru' | 'en' | 'ua';

export const translations = {
  ru: ruTranslations,
  en: enTranslations,
  ua: uaTranslations,
};

export const defaultLanguage: Language = 'ru';
