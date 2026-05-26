import { motion } from "framer-motion";
import clsx from "clsx";

export default function MagicCard({ children, className }) {
  return (
    <motion.div
      whileHover={{ scale: 1.02, rotateX: 2, rotateY: -2 }}
      transition={{ type: "spring", stiffness: 200, damping: 15 }}
      className={clsx(
        "glass rounded-2xl p-6 shadow-xl hover:shadow-cyan-500/20",
        className
      )}
    >
      {children}
    </motion.div>
  );
}