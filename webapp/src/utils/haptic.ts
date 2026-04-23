const hf = () => window.Telegram?.WebApp?.HapticFeedback;

export const haptic = {
  light: () => hf()?.impactOccurred('light'),
  medium: () => hf()?.impactOccurred('medium'),
  heavy: () => hf()?.impactOccurred('heavy'),
  success: () => hf()?.notificationOccurred('success'),
  warning: () => hf()?.notificationOccurred('warning'),
  error: () => hf()?.notificationOccurred('error'),
};
