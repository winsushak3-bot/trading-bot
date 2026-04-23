import { motion } from 'framer-motion';
import { MessageCircle } from 'lucide-react';

export const SupportView = () => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ type: 'spring', damping: 28, stiffness: 260 }}
    >
      <div className="mb-4">
        <h1 className="text-lg font-bold text-white">Поддержка</h1>
        <p className="text-zinc-500 text-xs mt-0.5">Ответы на обращения</p>
      </div>

      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-20 h-20 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-5">
          <MessageCircle size={32} className="text-zinc-600" />
        </div>
        <p className="text-zinc-400 text-sm font-medium">Пока пусто</p>
        <p className="text-zinc-600 text-xs mt-1">Обращений нет</p>
      </div>
    </motion.div>
  );
};
