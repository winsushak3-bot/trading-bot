import { motion, AnimatePresence } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { PageWrapper } from '../../shared/ui';
import { contentFade } from '../../shared/animations';
import { NewsItem, NewsFilter, DynamicTiles, ArticleModal } from './components';
import { useState, useCallback } from 'react';
import { useBackButton, useNews } from '../../hooks';
import { useTranslation } from '../../i18n';
import type { NewsArticle } from '../../hooks';

/* ─── News list for a category ─── */
const NewsList = ({ category, onSelect, readIds }: {
  category: 'crypto' | 'forex';
  onSelect: (article: NewsArticle) => void;
  readIds: Set<string>;
}) => {
  const { items, isLoading, error } = useNews(category);
  const { t } = useTranslation();

  if (isLoading && items.length === 0) {
    return (
      <div className="flex justify-center items-center h-32">
        <Loader2 className="w-6 h-6 animate-spin text-zinc-500" />
      </div>
    );
  }

  if (error && items.length === 0) {
    return <div className="text-center py-12 text-zinc-500 text-sm">{t('home.loadError')}</div>;
  }

  if (items.length === 0) {
    return <div className="text-center py-12 text-zinc-500 text-sm">{t('home.noNews')}</div>;
  }

  return (
    <>
      {items.map((article) => (
        <NewsItem
          key={article.id}
          source={article.source}
          title={article.title}
          time={article.time}
          readTime={article.readTime}
          image={article.image}
          isUnread={!readIds.has(article.id)}
          onClick={() => onSelect(article)}
        />
      ))}
    </>
  );
};

export const HomeView = () => {
  const [selectedNews, setSelectedNews] = useState<NewsArticle | null>(null);
  const [activeCategory, setActiveCategory] = useState(0);
  const [readNews, setReadNews] = useState<Set<string>>(new Set());

  const handleCloseNews = useCallback(() => setSelectedNews(null), []);
  useBackButton(selectedNews ? handleCloseNews : null);

  const handleNewsClick = (article: NewsArticle) => {
    setSelectedNews(article);
    setReadNews((prev) => new Set([...prev, article.id]));
  };

  return (
    <>
      <PageWrapper className="space-y-6 pb-4 -mx-2">
        <NewsFilter activeCategory={activeCategory} onCategoryChange={setActiveCategory} />

        <div className="relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeCategory}
              variants={contentFade()}
              initial="hidden"
              animate="visible"
              exit="hidden"
              className="space-y-3"
            >
              {activeCategory === 0 && <DynamicTiles />}
              {activeCategory === 1 && (
                <NewsList category="forex" onSelect={handleNewsClick} readIds={readNews} />
              )}
              {activeCategory === 2 && (
                <NewsList category="crypto" onSelect={handleNewsClick} readIds={readNews} />
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </PageWrapper>

      <AnimatePresence>
        {selectedNews && (
          <ArticleModal
            key="news-modal"
            article={selectedNews}
            onClose={handleCloseNews}
          />
        )}
      </AnimatePresence>
    </>
  );
};
