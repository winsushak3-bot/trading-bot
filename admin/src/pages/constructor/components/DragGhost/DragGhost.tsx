import type { HomeTile } from '../../../../api/client';

interface DragGhostProps {
  tile: HomeTile;
}

export const DragGhost = ({ tile }: DragGhostProps) => {
  const cs = tile.content?.colSpan || 2;
  const rs = tile.content?.rowSpan || 1;
  const bg = tile.content?.bg_color || '#18181b';
  const bgImg = tile.content?.bg_image;
  const isCube = tile.type === 'cube' || tile.type === 'cube_banner';
  const cubeImgs = tile.content?.bg_images;

  return (
    <div
      className="rounded-2xl overflow-hidden border-2 border-blue-500 shadow-2xl shadow-blue-500/20 pointer-events-none"
      style={{ width: cs * 80, height: rs * 70, opacity: 0.9 }}
    >
      <div className="absolute inset-0" style={{ backgroundColor: bg }} />
      {bgImg && !isCube && <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${bgImg})` }} />}
      {isCube && cubeImgs?.[0] && <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${cubeImgs[0]})` }} />}
      <div className="absolute inset-0 bg-black/30" />
      <div className="relative z-10 p-2 flex items-center justify-center h-full">
        <span className="text-white text-xs font-bold truncate">{tile.content?.title || tile.type}</span>
      </div>
    </div>
  );
};
