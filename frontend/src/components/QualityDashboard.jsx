import { Award, ShieldAlert, AlertTriangle, Target } from 'lucide-react';
import { motion, useInView } from 'framer-motion';
import { useRef, useEffect, useState } from 'react';

const AnimatedCounter = ({ value }) => {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });
  
  useEffect(() => {
    if (isInView) {
      let start = 0;
      const targetNumber = parseInt(value, 10) || 0;
      if (targetNumber === 0) return;
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
  }, [isInView, value]);

  return (
    <span ref={ref}>
      <span className="print:hidden">{value > 0 ? count : value}</span>
      <span className="hidden print:inline">{value}</span>
    </span>
  );
};

export default function QualityDashboard({ quality_summary }) {
  if (!quality_summary) return null;
  const { average_score, ambiguous_count, atomic_count, poor_quality_count, total } = quality_summary;

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-emerald-600';
    if (score >= 70) return 'text-amber-600';
    return 'text-red-600';
  };

  const getScoreBg = (score) => {
    if (score >= 90) return 'bg-emerald-500';
    if (score >= 70) return 'bg-amber-500';
    return 'bg-red-500';
  };

  const calculatePct = (count) => total > 0 ? Math.round((count / total) * 100) : 0;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      whileHover={{ y: -2, shadow: "0 20px 25px -5px rgba(0, 0, 0, 0.05)" }}
      className="rounded-2xl border border-slate-800 p-6 shadow-sm hover:shadow-xl hover:border-neon-blue/50 transition-all duration-300 break-inside-avoid glass-card"
    >
      <div className="flex items-center gap-2 mb-8 border-b border-slate-800 pb-4">
        <Award className="w-6 h-6 text-accent-500" />
        <h3 className="text-lg font-extrabold text-slate-200 tracking-tight">Requirement Quality Dashboard</h3>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-2">
        <motion.div whileHover={{ scale: 1.02 }} className="group">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Avg Score</div>
          <div className={`text-3xl font-black ${getScoreColor(average_score)}`}><AnimatedCounter value={average_score}/>/100</div>
          <div className="w-full bg-slate-800 rounded-full h-2 mt-3 overflow-hidden">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${average_score}%` }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              className={`h-full rounded-full ${getScoreBg(average_score)}`} 
            />
          </div>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} className="group">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 flex items-center gap-1.5">
            <Target className="w-4 h-4" /> Atomic
          </div>
          <div className="text-2xl font-bold text-slate-200"><AnimatedCounter value={atomic_count}/> <span className="text-sm font-semibold text-slate-400">reqs</span></div>
          <div className="w-full bg-slate-800 rounded-full h-2 mt-3 overflow-hidden">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${calculatePct(atomic_count)}%` }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              className="h-full rounded-full bg-primary-500" 
            />
          </div>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} className="group">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4" /> Ambiguous
          </div>
          <div className="text-2xl font-bold text-slate-200"><AnimatedCounter value={ambiguous_count}/> <span className="text-sm font-semibold text-slate-400">reqs</span></div>
          <div className="w-full bg-slate-800 rounded-full h-2 mt-3 overflow-hidden">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${calculatePct(ambiguous_count)}%` }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              className="h-full rounded-full bg-amber-500" 
            />
          </div>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} className="group">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1 flex items-center gap-1.5">
            <ShieldAlert className="w-4 h-4" /> Poor Quality
          </div>
          <div className="text-2xl font-bold text-slate-200"><AnimatedCounter value={poor_quality_count}/> <span className="text-sm font-semibold text-slate-400">reqs</span></div>
          <div className="w-full bg-slate-800 rounded-full h-2 mt-3 overflow-hidden">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${calculatePct(poor_quality_count)}%` }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              className="h-full rounded-full bg-red-500" 
            />
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
