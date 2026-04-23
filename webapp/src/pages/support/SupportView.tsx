import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { PageWrapper } from '../../shared/ui';
import { ChatTile, FAQSection, SupportChat } from './components';

export const SupportView = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <>
      <PageWrapper className="pb-4 space-y-6 -mx-2">
        <div>
          <ChatTile onClick={() => setIsChatOpen(true)} />
        </div>

        <div>
          <FAQSection />
        </div>
      </PageWrapper>

      <AnimatePresence>
        {isChatOpen && (
          <SupportChat 
            key="support-chat" 
            onClose={() => setIsChatOpen(false)} 
          />
        )}
      </AnimatePresence>
    </>
  );
};
