import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { accordion, rotate180 } from '../../../../shared/animations';
import { useTranslation } from '../../../../i18n';

export const FAQSection = () => {
  const { t } = useTranslation();
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const faqData = [
    { question: t('support.faq.q1'), answer: t('support.faq.a1') },
    { question: t('support.faq.q2'), answer: t('support.faq.a2') },
    { question: t('support.faq.q3'), answer: t('support.faq.a3') },
    { question: t('support.faq.q4'), answer: t('support.faq.a4') },
    { question: t('support.faq.q5'), answer: t('support.faq.a5') }
  ];

  return (
    <div className="space-y-3">
      <h3 className="text-xl font-bold text-white px-2">{t('support.faq.title')}</h3>
      
      <div className="space-y-2">
        {faqData.map((item, index) => (
          <div 
            key={index}
            className="bg-zinc-900 border-2 border-zinc-700 rounded-2xl overflow-hidden relative"
          >
            <div className="absolute top-0 left-0 w-16 h-16 bg-gradient-to-br from-white/5 to-transparent rounded-br-full pointer-events-none" />
            
            <button
              onClick={() => setOpenIndex(openIndex === index ? null : index)}
              className="w-full p-4 flex justify-between items-center text-left relative z-10 hover:bg-zinc-800/50 transition-colors"
            >
              <span className="text-white font-medium pr-2">{item.question}</span>
              <motion.div
                variants={rotate180(openIndex === index)}
                animate="animate"
              >
                <ChevronDown size={20} className="text-zinc-400 flex-shrink-0" />
              </motion.div>
            </button>

            <AnimatePresence>
              {openIndex === index && (
                <motion.div
                  variants={accordion}
                  initial="hidden"
                  animate="visible"
                  exit="hidden"
                  className="overflow-hidden"
                >
                  <div className="px-4 pb-4 text-sm text-zinc-400 leading-relaxed relative z-10">
                    {item.answer}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
      </div>
    </div>
  );
};
