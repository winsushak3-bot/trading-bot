interface TilePreviewProps {
  isCube: boolean;
  title: string;
  description: string;
  imageUrl: string;
  bgImage: string;
  bgImages: string[];
  bgColor: string;
  bgOpacity: number;
  isWhiteBg: boolean;
  colSpan: number;
  rowSpan: number;
}

export const TilePreview = ({ isCube, title, description, imageUrl, bgImage, bgImages, bgColor, bgOpacity, isWhiteBg, colSpan, rowSpan }: TilePreviewProps) => {
  const previewBg = bgColor || '#18181b';
  const opacity = bgOpacity / 100;

  return (
    <div className="px-5 pt-4 pb-2 shrink-0">
      <label className="block text-[10px] uppercase tracking-widest font-medium text-zinc-500 mb-2">Превью</label>
      <div className="grid grid-cols-4 gap-2" style={{ gridAutoRows: '70px' }}>
        <div
          className="rounded-2xl overflow-hidden flex flex-col border-2 border-zinc-700 relative"
          style={{ gridColumn: `span ${colSpan}`, gridRow: `span ${rowSpan}` }}
        >
          <div className="absolute inset-0 rounded-[14px]" style={{ backgroundColor: previewBg, opacity }} />
          {bgImage && (
            <div className="absolute inset-0 rounded-[14px] bg-cover bg-center" style={{ backgroundImage: `url(${bgImage})`, opacity }} />
          )}
          {isCube && bgImages.length > 0 ? (
            <div className="absolute inset-0 rounded-[14px] bg-cover bg-center" style={{ backgroundImage: `url(${bgImages[0]})` }} />
          ) : null}
          <div className="relative z-10 p-3 flex flex-col h-full">
            {!isCube && (
              <h3
                className={`text-sm font-bold leading-tight mb-0.5 line-clamp-2 ${isWhiteBg && !bgImage ? 'text-black' : 'text-white'}`}
                style={bgImage ? { textShadow: '0 1px 3px rgba(0,0,0,0.7)' } : undefined}
              >
                {title || 'Заголовок'}
              </h3>
            )}
            {!isCube && description && rowSpan > 1 && (
              <p
                className={`text-xs line-clamp-3 ${isWhiteBg && !bgImage ? 'text-zinc-600' : 'text-zinc-300'}`}
                style={bgImage ? { textShadow: '0 1px 2px rgba(0,0,0,0.5)' } : undefined}
              >{description}</p>
            )}
            {!isCube && imageUrl && !bgImage && rowSpan > 1 && (
              <div className="mt-auto pt-1 flex-1 flex flex-col justify-end">
                <img src={imageUrl} alt="" className="rounded-lg w-full object-cover max-h-16" onError={(e) => (e.currentTarget.style.display = 'none')} />
              </div>
            )}
            {isCube && (
              <div className="flex items-end justify-center h-full">
                <div className="flex gap-0.5">
                  {bgImages.slice(0, 4).map((_, i) => (
                    <div key={i} className={`w-1.5 h-1.5 rounded-full ${i === 0 ? 'bg-white' : 'bg-white/40'}`} />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
