import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink, Loader2 } from 'lucide-react';
import { simpleFade, popupSlide } from '../../../../shared/animations';
import { ImageViewer } from '../../../../shared/ui/ImageViewer';
import { api } from '../../../../api/client';
import { useTranslation } from '../../../../i18n';
import type { NewsArticle } from '../../../../hooks';

interface ArticleModalProps {
  article: NewsArticle;
  onClose: () => void;
}

export const ArticleModal = ({ article, onClose }: ArticleModalProps) => {
  const { t } = useTranslation();
  const [fullContent, setFullContent] = useState<string | null>(null);
  const [articleImages, setArticleImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewImage, setViewImage] = useState<string | null>(null);

  // Block background scroll
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    if (!article.link) {
      setLoading(false);
      return;
    }

    api.news.getArticle(article.link)
      .then((data) => {
        if (cancelled) return;
        if (data.content) setFullContent(data.content);
        if (data.images?.length) setArticleImages(data.images);
      })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false); });

    return () => { cancelled = true; };
  }, [article.link]);

  const displayContent = fullContent || article.summary;

  const renderContent = (text: string) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="text-white font-semibold text-base block mt-4 mb-1">{part.slice(2, -2)}</strong>;
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div key="news-modal" className="fixed inset-0 z-50">
      <motion.div
        variants={simpleFade}
        initial="hidden"
        animate="visible"
        exit="hidden"
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      <motion.div
        variants={popupSlide}
        initial="hidden"
        animate="visible"
        exit="hidden"
        className="absolute inset-x-3 bg-zinc-900/95 backdrop-blur-xl rounded-3xl border-2 border-zinc-700 z-10 max-w-md mx-auto max-h-[80vh] overflow-y-auto overscroll-contain"
        style={{ top: 'calc(50px + var(--safe-top, 0px))' }}
      >
        {/* Hero image — tappable */}
        {article.image && (
          <img
            src={article.image}
            alt=""
            className="w-full h-48 object-cover rounded-t-3xl cursor-pointer"
            onClick={() => setViewImage(article.image)}
            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
          />
        )}

        <div className="p-5">
          {/* Source + time */}
          <div className="flex items-center gap-2 mb-3">
            <div className="w-6 h-6 rounded-full bg-zinc-100 flex items-center justify-center text-black font-bold text-[10px]">
              {article.source[0]}
            </div>
            <span className="text-xs font-medium text-zinc-400">{article.source}</span>
            <span className="text-[10px] text-zinc-600 ml-auto">{article.time}</span>
          </div>

          {/* Title */}
          <h3 className="text-xl font-bold text-white leading-tight mb-2">{article.title}</h3>

          {/* Published date */}
          {article.publishedAt && (
            <p className="text-[11px] text-zinc-500 mb-4">{article.publishedAt}</p>
          )}

          {/* Loading indicator */}
          {loading && (
            <div className="flex items-center gap-2 mb-4 text-zinc-500 text-xs">
              <Loader2 className="w-3 h-3 animate-spin" />
              {t('home.loadingArticle')}
            </div>
          )}

          {/* Full article content */}
          <div className="text-zinc-300 text-sm leading-relaxed mb-4 whitespace-pre-line">
            {renderContent(displayContent)}
          </div>

          {/* Article images — tappable */}
          {articleImages.length > 0 && (
            <div className="space-y-3 mb-4">
              {articleImages.map((src, i) => (
                <img
                  key={i}
                  src={src}
                  alt=""
                  loading="lazy"
                  className="w-full rounded-xl object-cover max-h-60 cursor-pointer active:opacity-80 transition-opacity"
                  onClick={() => setViewImage(src)}
                  onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                />
              ))}
            </div>
          )}

          {/* Source link at bottom */}
          {article.link && (
            <a
              href={article.link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-xl text-xs text-zinc-400 font-medium transition-colors"
            >
              <ExternalLink size={12} /> {t('common.source')}: {article.source}
            </a>
          )}
        </div>
      </motion.div>

      {/* Fullscreen image viewer */}
      <AnimatePresence>
        {viewImage && <ImageViewer src={viewImage} onClose={() => setViewImage(null)} />}
      </AnimatePresence>
    </div>
  );
};
