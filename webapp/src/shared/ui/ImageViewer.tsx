import { motion } from 'framer-motion';
import { simpleFade } from '../animations';

interface ImageViewerProps {
  src: string;
  onClose: () => void;
}

export const ImageViewer = ({ src, onClose }: ImageViewerProps) => (
  <div className="fixed inset-0 z-[60] flex items-center justify-center" onClick={onClose}>
    <motion.div
      variants={simpleFade}
      initial="hidden"
      animate="visible"
      exit="hidden"
      className="absolute inset-0 bg-black/90"
    />
    <motion.img
      src={src}
      alt=""
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="relative z-10 max-w-[95vw] max-h-[90vh] object-contain rounded-xl"
    />
  </div>
);
