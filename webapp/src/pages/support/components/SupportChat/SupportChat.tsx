import { useState, useEffect, useRef } from 'react';
import { Send, Paperclip, Image, Video, File } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useBackButton } from '../../../../hooks';
import { api } from '../../../../api/client';
import { slideFromRight, slideUp, staggerScaleIn, TAP_BUTTON } from '../../../../shared/animations';
import { useTranslation } from '../../../../i18n';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  time: string;
}

interface SupportChatProps {
  onClose: () => void;
}

export const SupportChat = ({ onClose }: SupportChatProps) => {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [showAttachMenu, setShowAttachMenu] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [errorText, setErrorText] = useState<string | null>(null);
  const ticketIdRef = useRef<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  useBackButton(onClose);

  const fetchTicket = async (allowCreateIfMissing: boolean, signal?: AbortSignal) => {
    try {
      let ticketDetails;
      try {
        ticketDetails = await api.support.getMyTicket();
      } catch (error) {
        if (axios.isCancel(error)) return;
        const status = axios.isAxiosError(error) ? error.response?.status : undefined;
        if (allowCreateIfMissing && status === 404) {
          await api.support.createTicket();
          ticketDetails = await api.support.getMyTicket();
        } else {
          throw error;
        }
      }

      if (signal?.aborted) return;
      ticketIdRef.current = ticketDetails.id;
      const formattedMessages = ticketDetails.messages.map((m: any) => ({
        id: m.id,
        text: m.text,
        isUser: m.sender === 'user',
        time: new Date(m.created_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
      }));
      setMessages(formattedMessages);
      setErrorText(null);
    } catch (error) {
      if (signal?.aborted) return;
      console.error('Error fetching ticket', error);
      setErrorText(t('support.loadError'));
    } finally {
      if (!signal?.aborted) setIsLoading(false);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    fetchTicket(true, controller.signal);

    const interval = setInterval(() => {
      if (ticketIdRef.current) fetchTicket(false, controller.signal);
    }, 5000);

    return () => {
      controller.abort();
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || !ticketIdRef.current) return;

    const tempText = inputValue;
    setInputValue('');
    
    try {
      const newMessage = await api.support.sendMessage(ticketIdRef.current!, tempText);
      setMessages(prev => [...prev, {
        id: newMessage.id,
        text: newMessage.text,
        isUser: true,
        time: new Date(newMessage.created_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
      }]);
      setErrorText(null);
    } catch (error) {
      console.error('Failed to send message', error);
      setErrorText(t('support.sendError'));
    }
  };

  const attachOptions = [
    { icon: Image, label: t('support.photo'), color: 'bg-white/90' },
    { icon: Video, label: t('support.video'), color: 'bg-white/90' },
    { icon: File, label: t('support.file'), color: 'bg-white/90' },
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <motion.div
        variants={slideFromRight}
        initial="hidden"
        animate="visible"
        exit="hidden"
        className="absolute inset-0 bg-black flex flex-col"
      >
        {/* Header */}
        <div className="bg-black px-4 pb-4 flex items-center gap-3 border-b border-zinc-800" style={{ paddingTop: 'calc(16px + var(--safe-top, 0px))' }}>
          <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-black font-bold">
            S
          </div>
          <div>
            <h3 className="text-white font-bold">{t('support.supportTeam')}</h3>
            <p className="text-xs text-zinc-500">{t('support.replyingSoon')}</p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 pb-4">
          {errorText && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl px-3 py-2 text-xs text-red-300">
              {errorText}
            </div>
          )}
          {isLoading ? (
            <div className="text-center text-zinc-500 text-sm mt-10">{t('support.loadingMessages')}</div>
          ) : messages.length === 0 ? (
            <div className="text-center text-zinc-500 text-sm mt-10">
              {t('support.welcomeMessage')}
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-2 ${
                    msg.isUser
                      ? 'bg-white text-black rounded-br-md'
                      : 'bg-zinc-800 text-white rounded-bl-md'
                  }`}
                >
                  <p className="text-sm">{msg.text}</p>
                  <p className={`text-[10px] mt-1 ${msg.isUser ? 'text-zinc-600' : 'text-zinc-500'}`}>
                    {msg.time}
                  </p>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="bg-black px-4 pt-4 relative border-t border-zinc-800" style={{ paddingBottom: 'calc(16px + var(--safe-bottom, 0px))' }}>
          {/* Attach Menu */}
          <AnimatePresence>
            {showAttachMenu && (
              <motion.div
                variants={slideUp}
                initial="hidden"
                animate="visible"
                exit="hidden"
                className="absolute bottom-20 left-4 flex flex-col gap-3"
              >
                {attachOptions.map((option, index) => (
                  <motion.button
                    key={option.label}
                    variants={staggerScaleIn(index)}
                    initial="hidden"
                    animate="visible"
                    exit="hidden"
                    onClick={() => setShowAttachMenu(false)}
                    className={`${option.color} backdrop-blur-sm rounded-full p-2.5 shadow-lg ${TAP_BUTTON} border-2 border-zinc-700`}
                  >
                    <option.icon size={20} className="text-black" />
                  </motion.button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          <div className="flex gap-2">
            <button
              onClick={() => setShowAttachMenu(!showAttachMenu)}
              className={`rounded-full p-3 ${TAP_BUTTON} border ${
                showAttachMenu ? 'bg-white text-black border-white rotate-45' : 'bg-transparent text-white border-zinc-700'
              }`}
            >
              <Paperclip size={20} />
            </button>
            
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder={t('support.messagePlaceholder')}
              className="flex-1 bg-transparent text-white rounded-full px-4 py-3 text-sm outline-none placeholder:text-zinc-500 border border-zinc-700 focus:border-zinc-500 transition-colors"
            />
            
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() || isLoading}
              className={`bg-white text-black rounded-full p-3 disabled:opacity-30 disabled:cursor-not-allowed ${TAP_BUTTON} border border-white`}
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
