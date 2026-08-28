import { motion, useInView } from 'framer-motion';
import { useRef, useEffect, useState } from 'react';

const AnimatedCounter = ({ value }) => {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });
  
  // Extract number and suffix/prefix (e.g. "<2s", "95%")
  const numMatch = String(value).match(/\d+/);
  if (!numMatch) return <span>{value}</span>;
  
  const targetNumber = parseInt(numMatch[0], 10);
  const prefix = String(value).substring(0, numMatch.index);
  const suffix = String(value).substring(numMatch.index + numMatch[0].length);

  useEffect(() => {
    if (isInView) {
      let start = 0;
      const duration = 1500;
      
      const timer = setInterval(() => {
        start += Math.ceil(targetNumber / 20) || 1; 
        if (start >= targetNumber) {
          setCount(targetNumber);
          clearInterval(timer);
        } else {
          setCount(start);
        }
      }, 50);
      return () => clearInterval(timer);
    }
  }, [isInView, targetNumber]);

  return (
    <span ref={ref}>
      <span className="print:hidden">{prefix}{count}{suffix}</span>
      <span className="hidden print:inline">{prefix}{targetNumber}{suffix}</span>
    </span>
  );
};

export default function StatCard({ title, value, subtitle, icon, trendColor = "text-slate-500", delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5, ease: "easeOut" }}
      whileHover={{ y: -4, scale: 1.01 }}
      className="rounded-2xl border border-slate-800 p-6 flex flex-col relative overflow-hidden group shadow-sm hover:shadow-xl hover:shadow-neon-blue/20 hover:border-neon-blue/50 transition-all duration-300 glass-card"
    >
      <div className="absolute -right-4 -top-4 w-24 h-24 bg-primary-900/30 rounded-full opacity-0 group-hover:opacity-50 group-hover:scale-150 transition-all duration-500"></div>
      <div className="flex justify-between items-start mb-4 relative z-10">
        <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider">{title}</h4>
        <div className={`p-2.5 rounded-xl bg-slate-950 border border-slate-800 shadow-sm ${trendColor} group-hover:scale-110 transition-transform duration-300`}>
          {icon}
        </div>
      </div>
      <div className="relative z-10">
        <span className="text-3xl font-extrabold text-slate-50 tracking-tight">
          <AnimatedCounter value={value} />
        </span>
        {subtitle && (
          <p className="text-xs text-slate-400 mt-1.5 font-medium">{subtitle}</p>
        )}
      </div>
    </motion.div>
  );
}
