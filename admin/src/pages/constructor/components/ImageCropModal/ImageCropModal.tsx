import { useState, useCallback, useRef } from 'react';
import Cropper from 'react-easy-crop';
import type { Area } from 'react-easy-crop';
import { motion } from 'framer-motion';
import { X, Upload, Loader2, Image as ImageIcon, Film } from 'lucide-react';
import { api } from '../../../../api/client';

interface ImageCropModalProps {
  aspect: number;
  onComplete: (url: string) => void;
  onClose: () => void;
}

async function getCroppedImg(src: string, crop: Area): Promise<Blob> {
  const image = new Image();
  image.crossOrigin = 'anonymous';
  await new Promise<void>((resolve, reject) => {
    image.onload = () => resolve();
    image.onerror = reject;
    image.src = src;
  });

  const canvas = document.createElement('canvas');
  canvas.width = crop.width;
  canvas.height = crop.height;
  const ctx = canvas.getContext('2d')!;
  ctx.drawImage(image, crop.x, crop.y, crop.width, crop.height, 0, 0, crop.width, crop.height);

  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error('Canvas toBlob failed'));
    }, 'image/webp', 0.9);
  });
}

export const ImageCropModal = ({ aspect, onComplete, onClose }: ImageCropModalProps) => {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedArea, setCroppedArea] = useState<Area | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setError('');

    const isVideo = file.type.startsWith('video/');
    if (isVideo) {
      handleVideoUpload(file);
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      setImageSrc(reader.result as string);
      setVideoSrc(null);
    };
    reader.readAsDataURL(file);
  };

  const handleVideoUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const url = await api.uploads.upload(file, file.name);
      onComplete(url);
    } catch (e: any) {
      setError(e?.message || 'Ошибка загрузки');
    } finally {
      setIsUploading(false);
    }
  };

  const onCropComplete = useCallback((_: Area, croppedAreaPixels: Area) => {
    setCroppedArea(croppedAreaPixels);
  }, []);

  const handleSaveCrop = async () => {
    if (!imageSrc || !croppedArea) return;
    setIsUploading(true);
    setError('');
    try {
      const blob = await getCroppedImg(imageSrc, croppedArea);
      const url = await api.uploads.upload(blob, 'tile-bg.webp');
      onComplete(url);
    } catch (e: any) {
      setError(e?.message || 'Ошибка загрузки');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[60] flex items-center justify-center px-4"
    >
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />

      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="relative z-10 bg-zinc-900 border border-zinc-700 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800">
          <h3 className="text-white font-bold text-sm">Загрузка фона</h3>
          <button onClick={onClose} className="text-zinc-500 hover:text-white transition-colors">
            <X size={18} />
          </button>
        </div>

        <div className="p-5">
          {!imageSrc && !videoSrc ? (
            <div>
              <input
                ref={fileRef}
                type="file"
                accept="image/*,video/mp4,video/webm"
                onChange={onFileChange}
                className="hidden"
              />
              <button
                onClick={() => fileRef.current?.click()}
                disabled={isUploading}
                className="w-full border-2 border-dashed border-zinc-700 rounded-2xl py-12 flex flex-col items-center gap-3 hover:border-zinc-500 transition-colors group"
              >
                {isUploading ? (
                  <Loader2 size={32} className="text-zinc-500 animate-spin" />
                ) : (
                  <>
                    <div className="w-14 h-14 rounded-2xl bg-zinc-800 flex items-center justify-center group-hover:bg-zinc-700 transition-colors">
                      <Upload size={24} className="text-zinc-400" />
                    </div>
                    <div className="text-center">
                      <p className="text-zinc-300 text-sm font-medium">Выберите файл</p>
                      <p className="text-zinc-600 text-xs mt-1">JPG, PNG, WebP, GIF, MP4, WebM · до 10 МБ</p>
                    </div>
                    <div className="flex items-center gap-4 mt-1">
                      <span className="flex items-center gap-1 text-zinc-500 text-xs"><ImageIcon size={12} /> Фото</span>
                      <span className="flex items-center gap-1 text-zinc-500 text-xs"><Film size={12} /> Видео</span>
                    </div>
                  </>
                )}
              </button>
              {error && <p className="text-red-400 text-xs mt-3 text-center">{error}</p>}
            </div>
          ) : imageSrc ? (
            <div>
              <div className="relative w-full rounded-xl overflow-hidden bg-black" style={{ height: 300 }}>
                <Cropper
                  image={imageSrc}
                  crop={crop}
                  zoom={zoom}
                  aspect={aspect}
                  onCropChange={setCrop}
                  onZoomChange={setZoom}
                  onCropComplete={onCropComplete}
                  style={{
                    containerStyle: { borderRadius: 12 },
                  }}
                />
              </div>

              <div className="mt-4">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-zinc-400">Масштаб</span>
                  <span className="text-xs text-zinc-600 font-mono">{zoom.toFixed(1)}x</span>
                </div>
                <input
                  type="range" min={1} max={3} step={0.1}
                  value={zoom}
                  onChange={(e) => setZoom(Number(e.target.value))}
                  className="w-full h-1.5 bg-zinc-700 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-grab"
                />
              </div>

              {error && <p className="text-red-400 text-xs mt-2 text-center">{error}</p>}

              <div className="flex gap-2 mt-4">
                <button
                  onClick={() => { setImageSrc(null); setCrop({ x: 0, y: 0 }); setZoom(1); }}
                  className="flex-1 py-2.5 rounded-xl bg-zinc-800 text-zinc-400 text-sm font-medium hover:bg-zinc-700 transition-colors"
                >
                  Другой файл
                </button>
                <button
                  onClick={handleSaveCrop}
                  disabled={isUploading}
                  className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-white text-black text-sm font-bold hover:bg-zinc-200 transition-colors disabled:opacity-50"
                >
                  {isUploading ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />}
                  Загрузить
                </button>
              </div>
            </div>
          ) : null}
        </div>
      </motion.div>
    </motion.div>
  );
};
