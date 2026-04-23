import { useState, useCallback } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Bell } from 'lucide-react';
import { NotificationModal } from './NotificationModal';

export const NotificationButton = () => {
  const [showModal, setShowModal] = useState(false);
  const handleClose = useCallback(() => setShowModal(false), []);
  const hasUnread = false;

  return (
    <>
      <button 
        onClick={() => setShowModal(true)}
        className="relative p-3 bg-zinc-800 rounded-xl border border-zinc-700 transition-transform duration-100 active:scale-[0.97]"
      >
        <Bell size={22} className="text-zinc-300" />
        {hasUnread && (
          <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-white rounded-full"></span>
        )}
      </button>

      <AnimatePresence>
        {showModal && (
          <NotificationModal onClose={handleClose} />
        )}
      </AnimatePresence>
    </>
  );
};
