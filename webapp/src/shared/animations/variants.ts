import { Variants } from "framer-motion";

// ============================================================
// 1. МОДАЛЫ — backdrop + контент fullscreen-экранов
// ============================================================

/** Backdrop затемнение (используется во всех модалах) */
export const simpleFade: Variants = {
  hidden: { opacity: 0, transition: { duration: 0.15, ease: 'easeIn' } },
  visible: { opacity: 1, transition: { duration: 0.2, ease: 'easeOut' } },
};

/** Fullscreen-модал: open = spring, close = fast tween */
export const modalScale: Variants = {
  hidden: { opacity: 0, scale: 0.97, transition: { duration: 0.15, ease: 'easeIn' } },
  visible: { opacity: 1, scale: 1, transition: { type: 'spring', damping: 28, stiffness: 260 } },
};

// ============================================================
// 2. КОНТЕНТ — появление элементов на странице
// ============================================================

/** Slide up — для меню, action sheets */
export const slideUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { type: "tween", ease: "easeOut", duration: 0.25 } },
};

/** Popup-модал с slide-up (DynamicTiles, News detail и т.д.) */
export const popupSlide: Variants = {
  hidden: { opacity: 0, y: 50, scale: 0.95, transition: { duration: 0.15, ease: 'easeIn' } },
  visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.2, ease: 'easeOut' } },
};

/** Быстрый crossfade контента (смена категорий, табов, loader) */
export const contentFade = (duration = 0.15, delay = 0): Variants => ({
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration, delay } },
});

/** Stagger scale-in для списков кнопок/элементов */
export const staggerScaleIn = (index: number): Variants => ({
  hidden: { scale: 0, opacity: 0 },
  visible: { scale: 1, opacity: 1, transition: { delay: index * 0.05, duration: 0.25, ease: 'easeOut' } },
});

/** Навигация в стиле Telegram Android — экран выезжает справа (push/pop) */
export const slideFromRight: Variants = {
  hidden: { x: '100%', opacity: 1, transition: { type: 'tween', duration: 0.25, ease: [0.25, 0.1, 0.25, 1] } },
  visible: { x: 0, opacity: 1, transition: { type: 'tween', duration: 0.25, ease: [0.25, 0.1, 0.25, 1] } },
};

// ============================================================
// 3. КОМПОНЕНТЫ — специфичные анимации (FAQ, и т.д.)
// ============================================================

/** Аккордеон — раскрытие контента */
export const accordion: Variants = {
  hidden: { height: 0, opacity: 0 },
  visible: { height: 'auto', opacity: 1, transition: { duration: 0.2 } },
};

/** Вращение 180° (шеврон аккордеона) */
export const rotate180 = (isOpen: boolean): Variants => ({
  animate: { rotate: isOpen ? 180 : 0, transition: { duration: 0.2 } },
});

// ============================================================
// 4. TAP / PRESS — единые CSS-классы для нажатий
//    Меняешь здесь → меняется везде
// ============================================================

/** Плитка (Settings, About, NewsItem, Crypto, Forex) */
export const TAP_TILE = "transition-transform duration-100 active:scale-[0.97]";

/** Мелкие кнопки (send, attach, notification) */
export const TAP_BUTTON = "transition-transform duration-100 active:scale-[0.98]";
