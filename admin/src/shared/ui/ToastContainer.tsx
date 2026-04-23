import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, Info, X } from 'lucide-react';
import { useToastStore } from './useToast';

const icons = {
  success: <CheckCircle size={16} className="text-emerald-400" />,
  error: <XCircle size={16} className="text-red-400" />,
  info: <Info size={16} className="text-blue-400" />,
};

const borders = {
  success: 'border-emerald-500/20',
  error: 'border-red-500/20',
  info: 'border-blue-500/20',
};

export const ToastContainer = () => {
  const { toasts, remove } = useToastStore();

  return (
    <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, x: 40, scale: 0.95 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 40, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className={`pointer-events-auto flex items-center gap-2.5 bg-zinc-900/95 backdrop-blur-xl border ${borders[toast.type]} rounded-xl px-4 py-3 shadow-2xl min-w-[240px] max-w-[360px]`}
          >
            {icons[toast.type]}
            <span className="text-sm text-white flex-1">{toast.message}</span>
            <button
              onClick={() => remove(toast.id)}
              className="text-zinc-500 hover:text-white transition-colors shrink-0"
            >
              <X size={14} />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
