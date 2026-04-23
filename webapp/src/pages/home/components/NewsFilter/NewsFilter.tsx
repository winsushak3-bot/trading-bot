import { useTranslation } from '../../../../i18n';

interface NewsFilterProps {
  activeCategory: number;
  onCategoryChange: (index: number) => void;
}

export const NewsFilter = ({ activeCategory, onCategoryChange }: NewsFilterProps) => {
  const { t } = useTranslation();

  const categories = [t('home.categories.all'), 'Forex', 'Crypto'];

  return (
    <div className="flex gap-2 overflow-x-auto pb-2 px-2 scrollbar-hide">
        {categories.map((cat, i) => (
            <button 
                key={cat} 
                onClick={() => onCategoryChange(i)}
                className={`px-4 py-2 rounded-full text-xs font-bold whitespace-nowrap border transition-colors ${
                    i === activeCategory
                    ? 'bg-white text-black border-white' 
                    : 'bg-black text-zinc-500 border-zinc-800 hover:border-zinc-600'
                }`}
            >
                {cat}
            </button>
        ))}
    </div>
  );
};
