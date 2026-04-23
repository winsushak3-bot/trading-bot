import { motion } from 'framer-motion';
import { Mail, MessageCircle, ExternalLink } from 'lucide-react';
import { useBackButton } from '../../../../hooks';
import { slideFromRight, TAP_BUTTON } from '../../../../shared/animations';
import { useTranslation } from '../../../../i18n';

interface AboutModalProps {
  onClose: () => void;
}

export const AboutModal = ({ onClose }: AboutModalProps) => {
  const { t } = useTranslation();
  useBackButton(onClose);

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <motion.div
        variants={slideFromRight}
        initial="hidden"
        animate="visible"
        exit="hidden"
        className="absolute inset-0 bg-black flex flex-col"
      >
        <div className="bg-black px-4 pb-4" style={{ paddingTop: 'calc(16px + var(--safe-top, 0px))' }}>
          <h3 className="text-2xl font-bold text-white">{t('profile.aboutModal.title')}</h3>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ paddingBottom: 'calc(80px + var(--safe-bottom, 0px))' }}>
          {/* App Info */}
          <div className="bg-zinc-900 border-2 border-zinc-700 rounded-2xl p-5 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-20 h-20 bg-gradient-to-br from-white/5 to-transparent rounded-br-full pointer-events-none" />
            <div className="relative z-10">
              <h4 className="text-xl font-bold text-white mb-2">Trading Bot</h4>
              <p className="text-zinc-400 text-sm mb-3">
                {t('profile.aboutModal.description')}
              </p>
              <div className="flex items-center gap-2 text-zinc-500 text-xs">
                <span>{t('profile.aboutModal.version')} 1.0.0</span>
                <span>•</span>
                <span>2025</span>
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="bg-zinc-900 border-2 border-zinc-700 rounded-2xl p-5 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-20 h-20 bg-gradient-to-br from-white/5 to-transparent rounded-br-full pointer-events-none" />
            <div className="relative z-10">
              <h4 className="text-lg font-bold text-white mb-3">{t('profile.aboutModal.features')}</h4>
              <ul className="space-y-2 text-zinc-400 text-sm">
                <li>• {t('profile.aboutModal.feature1')}</li>
                <li>• {t('profile.aboutModal.feature2')}</li>
                <li>• {t('profile.aboutModal.feature3')}</li>
                <li>• {t('profile.aboutModal.feature4')}</li>
                <li>• {t('profile.aboutModal.feature5')}</li>
              </ul>
            </div>
          </div>

          {/* Contact */}
          <div className="space-y-2">
            <a href="https://t.me/trading_bot_channel" target="_blank" rel="noopener noreferrer" className={`block w-full bg-zinc-900 border-2 border-zinc-700 rounded-2xl p-4 ${TAP_BUTTON} relative overflow-hidden`}>
              <div className="absolute top-0 left-0 w-16 h-16 bg-gradient-to-br from-white/5 to-transparent rounded-br-full pointer-events-none" />
              <div className="flex items-center gap-3 relative z-10">
                <div className="p-2 bg-white rounded-xl">
                  <MessageCircle size={20} className="text-black" />
                </div>
                <div className="flex-1 text-left">
                  <p className="text-white font-bold">{t('profile.aboutModal.telegramChannel')}</p>
                  <p className="text-zinc-500 text-sm">@trading_bot_channel</p>
                </div>
                <ExternalLink size={16} className="text-zinc-600" />
              </div>
            </a>

            <a href="mailto:support@tradingbot.com" className={`block w-full bg-zinc-900 border-2 border-zinc-700 rounded-2xl p-4 ${TAP_BUTTON} relative overflow-hidden`}>
              <div className="absolute top-0 left-0 w-16 h-16 bg-gradient-to-br from-white/5 to-transparent rounded-br-full pointer-events-none" />
              <div className="flex items-center gap-3 relative z-10">
                <div className="p-2 bg-white rounded-xl">
                  <Mail size={20} className="text-black" />
                </div>
                <div className="flex-1 text-left">
                  <p className="text-white font-bold">Email</p>
                  <p className="text-zinc-500 text-sm">support@tradingbot.com</p>
                </div>
                <ExternalLink size={16} className="text-zinc-600" />
              </div>
            </a>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
