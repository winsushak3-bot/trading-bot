import { useState } from 'react';
import { motion } from 'framer-motion';
import { Lock, User, AlertCircle, ArrowRight } from 'lucide-react';
import { useAdminStore } from '../../store/useAdminStore';

export const LoginView = () => {
  const [telegramId, setTelegramId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isShaking, setIsShaking] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const login = useAdminStore((s) => s.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!telegramId.trim() || !password.trim()) {
      setError('Заполните все поля');
      triggerShake();
      return;
    }

    setIsSubmitting(true);
    try {
      const success = await login(telegramId.trim(), password.trim());
      if (!success) {
        setError('Неверный ID или пароль');
        triggerShake();
      }
    } catch {
      setError('Ошибка соединения с сервером');
      triggerShake();
    } finally {
      setIsSubmitting(false);
    }
  };

  const triggerShake = () => {
    setIsShaking(true);
    setTimeout(() => setIsShaking(false), 500);
  };

  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center p-6">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_30%,_var(--tw-gradient-stops))] from-zinc-900/30 via-black to-black" />

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
        className="relative z-10 w-full max-w-sm"
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25, ease: 'easeOut' }}
          className="text-center mb-10"
        >
          <div className="w-16 h-16 rounded-2xl bg-white/5 border border-zinc-800 flex items-center justify-center mx-auto mb-5">
            <Lock size={24} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Admin Panel</h1>
          <p className="text-zinc-500 text-sm mt-2">Вход в панель управления</p>
        </motion.div>

        <motion.form
          onSubmit={handleSubmit}
          animate={isShaking ? { x: [0, -8, 8, -8, 8, 0] } : {}}
          transition={{ duration: 0.4 }}
          className="space-y-4"
        >
          <div className="relative">
            <User size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500" />
            <input
              type="text"
              inputMode="numeric"
              placeholder="Telegram ID"
              value={telegramId}
              onChange={(e) => { setTelegramId(e.target.value); setError(''); }}
              className="w-full bg-zinc-900/80 border border-zinc-800 rounded-xl pl-11 pr-4 py-3.5 text-white text-sm placeholder:text-zinc-600 focus:outline-none focus:border-zinc-600 transition-colors"
              autoComplete="off"
            />
          </div>

          <div className="relative">
            <Lock size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500" />
            <input
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(e) => { setPassword(e.target.value); setError(''); }}
              className="w-full bg-zinc-900/80 border border-zinc-800 rounded-xl pl-11 pr-4 py-3.5 text-white text-sm placeholder:text-zinc-600 focus:outline-none focus:border-zinc-600 transition-colors"
              autoComplete="off"
            />
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 text-red-400 text-xs px-1"
            >
              <AlertCircle size={14} />
              <span>{error}</span>
            </motion.div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-white text-black font-semibold text-sm rounded-xl py-3.5 flex items-center justify-center gap-2 transition-all duration-200 active:scale-[0.98] hover:bg-zinc-200 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Вход...' : 'Войти'}
            {!isSubmitting && <ArrowRight size={16} />}
          </button>
        </motion.form>
      </motion.div>
    </div>
  );
};
