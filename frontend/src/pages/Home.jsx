import { motion } from 'framer-motion';
import { useRef } from 'react';
import { Link } from 'react-router-dom';
import { 
  Database, Search, Target, ShieldAlert, CheckCircle2, ArrowRight, Zap, 
  Activity, Clock, FileText, BarChart3, LayoutDashboard, FileOutput, Server, Code, XCircle, BrainCircuit
} from 'lucide-react';
import UploadBox from '../components/UploadBox';


const ParticleVortex = () => {
  // FULL-SCREEN Advanced Quantum Data Wave
  const rows = 36;
  const cols = 36;
  const particles = [];
  
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const dx = i - rows / 2;
      const dy = j - cols / 2;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      const delay = (dist * -0.2).toFixed(2);
      
      // HSL Color radiating perfectly 
      const hue = 210 + (dist * 4); 
      const color = `hsl(${hue}, 90%, 75%)`;

      // We push EVERY particle to ensure the grid covers the entire screen, no culling!
      particles.push({ id: `${i}-${j}`, i, j, delay, color });
    }
  }

  return (
    <div className="fixed inset-0 w-screen h-screen overflow-hidden -z-10 bg-[#05050A] flex items-center justify-center pointer-events-none">
      
      <style>{`
        @keyframes quantum-wave {
          0% { transform: translateZ(-80px) scale(0.5); opacity: 0.1; }
          100% { transform: translateZ(80px) scale(2); opacity: 0.8; }
        }
        @keyframes slow-spin {
          from { transform: perspective(1000px) rotateX(60deg) rotateZ(0deg); }
          to { transform: perspective(1000px) rotateX(60deg) rotateZ(360deg); }
        }
        .quantum-grid {
          animation: slow-spin 120s linear infinite;
          transform-style: preserve-3d;
        }
        .quantum-dot {
          will-change: transform, opacity;
        }
      `}</style>

      {/* Ambient Full-Screen Core Glow */}
      <div className="absolute w-[100vw] h-[100vw] bg-indigo-900/10 rounded-full blur-[150px]" />
      
      <div className="relative w-full h-full flex items-center justify-center">
        {/* MASSIVE 200vw x 200vw grid to ensure corners are covered even during rotation */}
        <div className="relative quantum-grid" style={{ width: '200vw', height: '200vw' }}>
          {particles.map(p => (
            <div
              key={p.id}
              className="absolute rounded-full quantum-dot"
              style={{
                width: '5px',
                height: '5px',
                backgroundColor: p.color,
                left: `${(p.i / rows) * 100}%`,
                top: `${(p.j / cols) * 100}%`,
                boxShadow: `0 0 12px ${p.color}`,
                animation: `quantum-wave 3s ease-in-out ${p.delay}s infinite alternate`
              }}
            />
          ))}
        </div>
      </div>
      
      {/* Very subtle edge vignette, just for softening the very edges */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_50%,#05050A_100%)]" />
    </div>
  );
};

export default function Home() {
  const demoRef = useRef(null);

  const scrollToDemo = () => {
    demoRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const features = [
    { icon: <Target className="w-5 h-5" />, title: "Scope Creep Detection" },
    { icon: <Database className="w-5 h-5" />, title: "Traceability Matrix" },
    { icon: <ShieldAlert className="w-5 h-5" />, title: "Requirement Quality" },
    { icon: <Zap className="w-5 h-5" />, title: "TF-IDF Comparison" },
    { icon: <LayoutDashboard className="w-5 h-5" />, title: "Interactive Dashboard" },
    { icon: <FileOutput className="w-5 h-5" />, title: "PDF Report" },
    { icon: <Clock className="w-5 h-5" />, title: "Timeline Analysis" },
    { icon: <Activity className="w-5 h-5" />, title: "Impact Analysis" }
  ];

  return (
    <div className="relative min-h-screen bg-transparent overflow-hidden font-sans">
      <ParticleVortex />
      {/* Navbar Placeholder */}
      <nav className="w-full max-w-7xl mx-auto px-6 py-6 flex justify-between items-center z-50 relative">
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-8 h-8 text-neon-blue" />
          <span className="text-xl font-bold text-slate-50 tracking-tight">ReqVision<span className="text-neon-blue">AI</span></span>
        </div>
        <div className="flex gap-6 items-center">
          <Link to="/dashboard" className="hidden md:block text-sm font-semibold text-slate-400 hover:text-slate-900 transition-colors">Dashboard</Link>
          <button onClick={scrollToDemo} className="hidden md:block text-sm font-semibold text-slate-400 hover:text-slate-900 transition-colors">Live Demo</button>
          <a href="https://github.com/PrathamMrana/ReqVision-AI" target="_blank" rel="noreferrer" className="hidden md:flex text-sm font-semibold text-slate-400 hover:text-slate-900 transition-colors items-center gap-1"><Code className="w-4 h-4"/> GitHub</a>
          <div className="w-px h-6 bg-slate-700 hidden md:block"></div>
          <button className="text-sm font-bold text-slate-300 hover:text-primary-600 transition-colors">Log In</button>
          <button onClick={scrollToDemo} className="px-5 py-2.5 hover:bg-slate-800 text-white rounded-xl text-sm font-bold shadow-lg shadow-slate-900/20 transition-all glass-card">Get Started</button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-24">
        {/* 1. Hero Section */}
        <div className="text-center max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: [0, -8, 0] }}
            transition={{ opacity: { duration: 0.5 }, y: { repeat: Infinity, duration: 4, ease: "easeInOut" } }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900 border border-primary-900 text-neon-blue text-sm font-bold mb-8 shadow-sm"
          >
            <Zap className="w-4 h-4 text-accent-500" /> Powered by TF-IDF & Cosine Similarity
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-5xl md:text-7xl font-extrabold text-slate-50 tracking-tight leading-[1.1]"
          >
            Intelligent <span className="text-gradient font-black tracking-tight">Requirement Drift</span> <br className="hidden md:block"/> Analysis
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mt-6 text-xl text-slate-400 leading-relaxed max-w-2xl mx-auto font-medium"
          >
            Instantly compare Software Requirement Specifications (SRS). Detect modifications, track scope creep, and mitigate project risks before they impact your sprint.
          </motion.p>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-10 flex flex-col sm:flex-row justify-center gap-4"
          >
            <motion.button 
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              onClick={scrollToDemo} 
              className="px-8 py-4 bg-neon-blue/10 hover:bg-neon-blue/20 text-white neon-border shadow-neon-glow hover:shadow-[0_0_20px_var(--color-neon-blue)] rounded-xl font-bold shadow-xl shadow-slate-900/20 transition-colors flex items-center justify-center gap-2 group text-lg glass-card"
            >
              Analyze SRS <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </motion.button>
            <motion.button 
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              onClick={scrollToDemo} 
              className="px-8 py-4 bg-slate-900/50 hover:bg-slate-800 text-slate-200 border border-slate-700 rounded-xl font-bold shadow-sm transition-colors flex items-center justify-center gap-2 text-lg glass-card"
            >
              View Live Demo
            </motion.button>
          </motion.div>
        </div>

        {/* 2. Animated Statistics */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-24 grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-5xl mx-auto bg-slate-900/80 backdrop-blur-xl p-8 md:p-10 rounded-3xl border border-slate-700 shadow-xl shadow-neon-blue/10"
        >
          <div className="text-center">
            <div className="text-3xl md:text-4xl font-extrabold text-slate-50 mb-2 mt-1">Unlimited</div>
            <div className="text-xs md:text-sm font-bold text-slate-400 uppercase tracking-widest">Requirements Capacity</div>
          </div>
          <div className="text-center">
            <div className="text-3xl md:text-4xl font-extrabold text-neon-blue mb-2 mt-1">High</div>
            <div className="text-xs md:text-sm font-bold text-slate-400 uppercase tracking-widest">Detection Accuracy</div>
          </div>
          <div className="text-center flex flex-col justify-center">
            <div className="text-3xl md:text-4xl font-extrabold text-gradient font-black tracking-tight mb-2 mt-1">TF-IDF</div>
            <div className="text-xs md:text-sm font-bold text-slate-400 uppercase tracking-widest">Core NLP Engine</div>
          </div>
        </motion.div>

        {/* 11. Live Demo / Upload Box */}
        <div className="mt-40 scroll-mt-32" ref={demoRef}>
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-50 tracking-tight">Live Interactive Demo</h2>
            <p className="text-slate-400 mt-3 max-w-2xl mx-auto text-lg">Upload your Baseline and Updated SRS text files below to instantly generate a comprehensive change impact dashboard.</p>
          </div>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="relative z-10"
          >
            <UploadBox />
          </motion.div>
        </div>

        {/* 3. How It Works */}
        <div className="mt-40">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-50 tracking-tight">How It Works</h2>
            <p className="text-slate-400 mt-3 text-lg">A seamless NLP pipeline built for software engineering.</p>
          </div>
          
          <div className="relative max-w-5xl mx-auto">
            <div className="hidden md:block absolute top-20 left-10 w-[calc(100%-5rem)] h-[1px] bg-gradient-to-r from-transparent via-blue-500/30 to-transparent -z-10"></div>
            {/* Animated laser travelling through pipeline */}
            <motion.div 
              animate={{ left: ['0%', '100%'], opacity: [0, 1, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="hidden md:block absolute top-20 w-32 h-[1px] bg-gradient-to-r from-transparent via-blue-400 to-transparent -z-10"
            />
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              {[
                { step: "01", title: "Baseline SRS", desc: "Upload the master requirements document as your source of truth.", icon: <FileText className="w-7 h-7" /> },
                { step: "02", title: "Updated SRS", desc: "Inject the modified document containing new sprint changes.", icon: <FileOutput className="w-7 h-7" /> },
                { step: "03", title: "Neural Pipeline", desc: "Our engine executes cosine similarity to map shifting dependencies.", icon: <Activity className="w-7 h-7" /> },
                { step: "04", title: "Impact Dashboard", desc: "Instantly trace scope creep and project risks in the dashboard.", icon: <LayoutDashboard className="w-7 h-7" /> }
              ].map((s, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1, type: "spring", stiffness: 200, damping: 25 }}
                  className="group relative p-8 rounded-3xl neon-border overflow-hidden transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_20px_40px_-15px_rgba(96,165,250,0.15)] bg-gradient-to-b from-white/[0.03] to-transparent"
                >
                  {/* Subtle Background Glow on Hover */}
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500/0 via-indigo-500/0 to-purple-500/0 group-hover:from-blue-500/10 group-hover:via-indigo-500/5 group-hover:to-transparent transition-all duration-700 opacity-0 group-hover:opacity-100 -z-10"></div>
                  
                  {/* Premium Icon Container */}
                  <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-8 bg-slate-800/40 border border-slate-700/50 text-slate-300 group-hover:bg-blue-600 group-hover:text-white group-hover:border-blue-400 group-hover:shadow-[0_0_30px_rgba(59,130,246,0.4)] transition-all duration-500 relative z-10">
                    {s.icon}
                  </div>
                  
                  {/* Majestic Watermark Number */}
                  <div className="absolute top-4 right-4 text-7xl font-black text-slate-800/40 select-none group-hover:text-blue-500/10 transition-colors duration-500 z-0">
                    {s.step}
                  </div>
                  
                  <h3 className="text-xl font-bold text-slate-50 mb-3 group-hover:text-blue-400 transition-colors duration-300 relative z-10">{s.title}</h3>
                  <p className="text-slate-400 font-medium leading-relaxed relative z-10 group-hover:text-slate-300 transition-colors duration-300">{s.desc}</p>
                  
                  {/* Bottom animated border line */}
                  <div className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-blue-500 to-indigo-500 w-0 group-hover:w-full transition-all duration-500 ease-out"></div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* 6. Why ReqVision AI (Comparison) */}
        <div className="mt-40 max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-50 tracking-tight">Why ReqVision AI?</h2>
            <p className="text-slate-400 mt-3 text-lg">Ditch manual reviews for automated quantitative intelligence.</p>
          </div>
          <div className="bg-slate-900 rounded-3xl shadow-2xl shadow-neon-blue/10 border border-slate-800 overflow-hidden">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-800/40 border-b border-slate-800">
                  <th className="p-8 text-lg font-bold text-slate-400 uppercase tracking-widest w-1/2">Traditional Review</th>
                  <th className="p-8 text-lg font-black text-neon-blue uppercase tracking-widest bg-slate-800/60 w-1/2">
                    <div className="flex items-center gap-3"><Zap className="w-6 h-6 text-accent-500"/> ReqVision AI</div>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  ["Manual requirement scanning", "Automated TF-IDF vector matching"],
                  ["Time consuming (hours/days)", "Analyzed locally in seconds"],
                  ["Error prone & inconsistent", "100% Consistent execution rules"],
                  ["No quantitative impact analysis", "Dynamic module impact & risk level"],
                  ["Undetected scope creep", "Precise scope creep index calculation"],
                  ["Static PDF reports", "Interactive tracing & animated dashboard"]
                ].map((row, i) => (
                  <tr key={i} className="hover:bg-slate-800/40 transition-colors group">
                    <td className="p-8">
                      <div className="text-slate-400 font-medium text-lg flex items-center gap-4"><XCircle className="w-6 h-6 text-slate-300 group-hover:text-red-400 transition-colors shrink-0"/> {row[0]}</div>
                    </td>
                    <td className="p-8 bg-slate-800/20">
                      <div className="text-slate-50 font-bold text-lg flex items-center gap-4"><CheckCircle2 className="w-6 h-6 text-emerald-500 shrink-0"/> {row[1]}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 4. Feature Grid & 5. Tech Stack */}
        <div className="mt-40 grid lg:grid-cols-2 gap-20 items-center">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-slate-50 mb-8 tracking-tight">Powerful Capabilities</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {features.map((f, i) => (
                <motion.div 
                  whileHover={{ scale: 1.02 }}
                  key={i} 
                  className="flex items-center gap-4 p-5 rounded-2xl border border-slate-800 shadow-sm hover:shadow-md hover:border-neon-blue transition-all cursor-default glass-card"
                >
                  <div className="w-10 h-10 rounded-xl bg-primary-900/30 flex items-center justify-center text-neon-blue shrink-0">
                    {f.icon}
                  </div>
                  <span className="font-bold text-slate-200">{f.title}</span>
                </motion.div>
              ))}
            </div>
            
            <div className="mt-16">
              <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest mb-6">Technology Stack</h3>
              <div className="flex flex-wrap gap-3">
                {['React', 'FastAPI', 'Python', 'TF-IDF', 'Scikit-learn', 'TailwindCSS', 'Recharts', 'Framer Motion'].map(tech => (
                  <span key={tech} className="px-5 py-2.5 text-white text-sm font-bold rounded-xl shadow-lg shadow-slate-900/20 hover:bg-primary-600 transition-colors cursor-default glass-card">{tech}</span>
                ))}
              </div>
            </div>
          </div>
          
          {/* 7. Dashboard Showcase Mockup */}
          <motion.div 
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            animate={{ y: [0, -15, 0] }}
            transition={{ 
              opacity: { duration: 0.5 }, 
              x: { duration: 0.5 },
              y: { repeat: Infinity, duration: 6, ease: "easeInOut" }
            }}
            viewport={{ once: true }}
            className="relative perspective-1000"
          >
            <div className="absolute inset-0 bg-gradient-to-tr from-primary-500 to-accent-500 rounded-3xl transform rotate-3 scale-105 opacity-20 filter blur-2xl"></div>
            <motion.div 
              whileHover={{ rotate: 0, scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
              className="bg-slate-900 rounded-3xl shadow-2xl overflow-hidden border border-slate-700 relative z-10 transform -rotate-2 ease-out"
            >
              <div className="bg-slate-800/80 backdrop-blur px-6 py-4 flex items-center gap-3 border-b border-slate-700/50">
                <div className="w-3.5 h-3.5 rounded-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]"></div>
                <div className="w-3.5 h-3.5 rounded-full bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]"></div>
                <div className="w-3.5 h-3.5 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                <div className="ml-6 text-sm font-mono text-slate-400 bg-slate-900/50 border border-slate-700/50 px-6 py-1.5 rounded-full flex-1 text-center truncate">reqvision-ai.demo / dashboard</div>
              </div>
              <div className="p-8 bg-transparent h-[500px] overflow-hidden flex flex-col gap-6">
                {/* Mock UI Elements */}
                <div className="h-24 rounded-2xl border border-slate-700 shadow-sm p-6 flex items-center justify-between animate-pulse glass-card">
                   <div className="flex items-center gap-6">
                      <div className="w-14 h-14 bg-primary-900/50 rounded-full flex items-center justify-center"><ShieldAlert className="w-7 h-7 text-neon-blue"/></div>
                      <div>
                        <div className="w-40 h-5 bg-slate-700 rounded-md mb-3"></div>
                        <div className="w-64 h-4 bg-slate-800 rounded-md"></div>
                      </div>
                   </div>
                   <div className="w-32 h-10 bg-emerald-100 rounded-full"></div>
                </div>
                <div className="grid grid-cols-4 gap-6">
                   {[1,2,3,4].map(i => <div key={i} className="h-28 rounded-2xl border border-slate-700 shadow-sm p-5 flex flex-col justify-between glass-card"><div className="w-10 h-10 bg-slate-800 rounded-xl"></div><div className="w-20 h-6 bg-slate-700 rounded-md"></div></div>)}
                </div>
                <div className="flex-1 rounded-2xl border border-slate-700 shadow-sm p-6 glass-card">
                  <div className="w-48 h-6 bg-slate-700 rounded-md mb-6"></div>
                  <div className="w-full h-4 bg-slate-800 rounded-md mb-3"></div>
                  <div className="w-full h-4 bg-slate-800 rounded-md mb-3"></div>
                  <div className="w-3/4 h-4 bg-slate-800 rounded-md"></div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>

      </div>

      {/* 10. Footer */}
      <footer className="bg-transparent text-slate-400 py-16 mt-32 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-8 grid md:grid-cols-2 gap-12 items-center">
          <div>
            <div className="flex items-center gap-3 mb-6">
              <BrainCircuit className="w-10 h-10 text-neon-blue" />
              <span className="text-2xl font-bold text-white tracking-tight">ReqVision<span className="text-primary-500">AI</span></span>
            </div>
            <p className="text-slate-400 leading-relaxed max-w-md text-sm font-medium">An advanced NLP-powered Software Requirement Specification (SRS) analyzer utilizing TF-IDF and Cosine Similarity to automatically detect scope creep and requirement drift.</p>
          </div>
          <div className="flex md:justify-end gap-10 text-sm font-bold">
            <a href="https://github.com/PrathamMrana/ReqVision-AI" target="_blank" rel="noreferrer" className="hover:text-white transition-colors flex items-center gap-2"><Code className="w-5 h-5"/> GitHub</a>
            <a href="#" className="hover:text-white transition-colors flex items-center gap-2"><FileText className="w-5 h-5"/> Documentation</a>
            <span className="flex items-center gap-2 text-slate-400"><Server className="w-5 h-5"/> v1.0.0</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
