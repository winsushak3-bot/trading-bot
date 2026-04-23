import { motion, HTMLMotionProps } from 'framer-motion';
import { modalScale } from '../animations';

export const PageWrapper = ({ children, className, ...props }: HTMLMotionProps<"div">) => {
  return (
    <motion.div
      variants={modalScale}
      initial="hidden"
      animate="visible"
      exit="hidden"
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
};