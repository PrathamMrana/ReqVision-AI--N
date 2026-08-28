import { motion } from 'framer-motion';
import { useRef } from 'react';
import { Link } from 'react-router-dom';
import { 
  Database, Search, Target, ShieldAlert, CheckCircle2, ArrowRight, Zap, 
  Activity, Clock, FileText, BarChart3, LayoutDashboard, FileOutput, Server, Code, XCircle, BrainCircuit,
  Sparkles, Network, GitPullRequest, Layers, ShieldCheck, Cpu
} from 'lucide-react';
import UploadBox from '../components/UploadBox';

const ParticleVortex = () => {
  const rows = 36;
  const cols = 36;
  const particles = [];
  
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const dx = i - rows / 2;
      const dy = j - cols / 2;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      const delay = (dist * -0.2).toFixed(2);
      const hue = 210 + (dist * 4); 
      const color = `hsl(${hue}, 90%, 75%)`;

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
      
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_50%,#05050A_100%)]" />
    </div>
  );
};

export default function Home() {
  const demoRef = useRef(null);

  const scrollToDemo = () => {
    demoRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const capabilities = [
    { icon: <Target className="w-5 h-5" />, title: "Scope Creep Intelligence", desc: "Autonomous detection of unbudgeted requirement drift and feature expansion." },
    { icon: <Network className="w-5 h-5" />, title: "Cross-Doc Traceability", desc: "Bi-directional linkage spanning BRDs, SRS, Change Requests, and Test Scenarios." },
    { icon: <ShieldCheck className="w-5 h-5" />, title: "Continuous Assurance", desc: "Automated quality scoring, ambiguity resolution, and non-measurable term audit." },
    { icon: <Cpu className="w-5 h-5" />, title: "Deterministic NLP Engine", desc: "TF-IDF vectorization with numerical constraint preservation and zero hallucination." },
    { icon: <Layers className="w-5 h-5" />, title: "Architecture Impact Graph", desc: "Layered component dependency mapping across Frontend, Backend, DB, and Cloud." },
    { icon: <FileOutput className="w-5 h-5" />, title: "Executive Audit Export", desc: "Comprehensive compliance-ready PDF reports with print-optimized pagination." },
    { icon: <Clock className="w-5 h-5" />, title: "Sprint Effort Estimation", desc: "Algorithmic Story Points calculation derived from structural text delta." },
    { icon: <GitPullRequest className="w-5 h-5" />, title: "Change Request Linking", desc: "Direct AFFECTS mapping correlating ad-hoc changes to target specifications." }
  ];

  return (
    <div className="relative min-h-screen bg-transparent overflow-hidden font-sans text-slate-100">
      <ParticleVortex />

      {/* Navigation */}
      <nav className="w-full max-w-7xl mx-auto px-6 py-6 flex justify-between items-center z-50 relative">
        <div className="flex items-center gap-2.5">
          <BrainCircuit className="w-8 h-8 text-neon-blue" />
          <span className="text-xl font-extrabold text-slate-50 tracking-tight">
            ReqVision<span className="text-neon-blue">AI</span>
            <span className="ml-2 text-[10px] uppercase font-bold tracking-widest bg-neon-blue/10 text-neon-blue border border-neon-blue/30 px-2 py-0.5 rounded-full">
              Platform
            </span>
          </span>
        </div>
        <div className="flex gap-6 items-center">
          <Link to="/dashboard" className="hidden md:block text-sm font-semibold text-slate-400 hover:text-white transition-colors">Dashboard</Link>
          <button onClick={scrollToDemo} className="hidden md:block text-sm font-semibold text-slate-400 hover:text-white transition-colors">Intelligence Engine</button>
          <a href="https://github.com/PrathamMrana/ReqVision-AI--N" target="_blank" rel="noreferrer" className="hidden md:flex text-sm font-semibold text-slate-400 hover:text-white transition-colors items-center gap-1.5">
            <Code className="w-4 h-4 text-neon-blue"/> GitHub
          </a>
          <div className="w-px h-6 bg-slate-800 hidden md:block"></div>
          <button onClick={scrollToDemo} className="px-5 py-2.5 bg-neon-blue/20 hover:bg-neon-blue/30 text-white rounded-xl text-sm font-bold neon-border shadow-neon-glow hover:shadow-[0_0_20px_var(--color-neon-blue)] transition-all">
            Launch Platform
          </button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-24">
        
        {/* 1. Hero Section: Software Intelligence Platform */}
        <div className="text-center max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: [0, -6, 0] }}
            transition={{ opacity: { duration: 0.5 }, y: { repeat: Infinity, duration: 4, ease: "easeInOut" } }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900/80 border border-indigo-500/40 text-neon-blue text-xs sm:text-sm font-extrabold mb-8 shadow-lg shadow-indigo-950/40 backdrop-blur-md"
          >
            <Sparkles className="w-4 h-4 text-amber-400" /> Software Intelligence Platform
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black text-slate-50 tracking-tight leading-[1.05]"
          >
            Software Intelligence. <br/>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 font-black tracking-tight">
              Requirements. Traceability. Assurance.
            </span>
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mt-8 text-lg sm:text-xl md:text-2xl text-slate-300 leading-relaxed max-w-3xl mx-auto font-normal"
          >
            The autonomous intelligence layer for modern engineering teams. Ingest BRDs, SRS, Change Requests, and Technical Specs to eliminate scope creep, map cross-document traceability, and guarantee continuous architectural assurance before code is written.
          </motion.p>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-10 flex flex-col sm:flex-row justify-center items-center gap-4"
          >
            <motion.button 
              whileHover={{ scale: 1.04, y: -2 }}
              whileTap={{ scale: 0.96 }}
              onClick={scrollToDemo} 
              className="w-full sm:w-auto px-9 py-4 bg-neon-blue/20 hover:bg-neon-blue/30 text-white neon-border shadow-neon-glow hover:shadow-[0_0_30px_var(--color-neon-blue)] rounded-2xl font-extrabold shadow-2xl transition-all flex items-center justify-center gap-2 group text-lg glass-card"
            >
              Launch Intelligence Engine <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-neon-blue" />
            </motion.button>
            <motion.button 
              whileHover={{ scale: 1.04, y: -2 }}
              whileTap={{ scale: 0.96 }}
              onClick={scrollToDemo} 
              className="w-full sm:w-auto px-9 py-4 bg-slate-900/60 hover:bg-slate-800 text-slate-200 border border-slate-700/80 rounded-2xl font-bold shadow-sm transition-all flex items-center justify-center gap-2 text-lg glass-card"
            >
              Explore Traceability Matrix
            </motion.button>
          </motion.div>
        </div>

        {/* 2. Platform Value Props / Stats Bar */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-20 grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-5xl mx-auto bg-slate-900/80 backdrop-blur-2xl p-6 md:p-8 rounded-3xl border border-slate-700/80 shadow-2xl shadow-neon-blue/10"
        >
          <div className="text-center p-4">
            <div className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-neon-blue mb-1 font-mono">Multi-Source</div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">BRD · SRS · FRD · CR · QA</div>
          </div>
          <div className="text-center p-4 border-y sm:border-y-0 sm:border-x border-slate-800">
            <div className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-slate-50 mb-1 font-mono">Bi-Directional</div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">Traceability & Provenance</div>
          </div>
          <div className="text-center p-4 flex flex-col justify-center">
            <div className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300 font-mono mb-1">
              Zero-Hallucination
            </div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">Verified Lexical NLP Math</div>
          </div>
        </motion.div>

        {/* 3. Live Demo / Upload Box */}
        <div className="mt-32 scroll-mt-28" ref={demoRef}>
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-neon-blue mb-3">
              <Zap className="w-4 h-4 text-amber-400" /> Interactive Workbench
            </div>
            <h2 className="text-3xl md:text-5xl font-extrabold text-slate-50 tracking-tight">Software Intelligence Engine</h2>
            <p className="text-slate-400 mt-3 max-w-2xl mx-auto text-base sm:text-lg font-medium">
              Upload multiple baseline documents and updated specifications to generate an end-to-end requirement drift, provenance, and cross-document assurance audit.
            </p>
          </div>
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="relative z-10"
          >
            <UploadBox />
          </motion.div>
        </div>

        {/* 4. The 4-Stage Software Intelligence Pipeline */}
        <div className="mt-36">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-indigo-400 mb-3">
              <Activity className="w-4 h-4 text-indigo-400" /> Architectural Workflow
            </div>
            <h2 className="text-3xl md:text-5xl font-extrabold text-slate-50 tracking-tight">How Software Intelligence Works</h2>
            <p className="text-slate-400 mt-3 text-base sm:text-lg max-w-xl mx-auto">
              A deterministic 4-stage pipeline translating fragmented specifications into verifiable engineering truth.
            </p>
          </div>
          
          <div className="relative max-w-6xl mx-auto">
            <div className="hidden md:block absolute top-20 left-10 w-[calc(100%-5rem)] h-[1px] bg-gradient-to-r from-transparent via-blue-500/30 to-transparent -z-10"></div>
            <motion.div 
              animate={{ left: ['0%', '100%'], opacity: [0, 1, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="hidden md:block absolute top-20 w-32 h-[1px] bg-gradient-to-r from-transparent via-blue-400 to-transparent -z-10"
            />
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[
                { 
                  step: "01", 
                  title: "Multi-Source Ingestion", 
                  desc: "Ingest BRD, SRS, Change Requests, User Stories, and Test Specs in TXT, DOCX, or PDF formats simultaneously.", 
                  icon: <FileText className="w-7 h-7" /> 
                },
                { 
                  step: "02", 
                  title: "Provenance & Extraction", 
                  desc: "Preserve document provenance, source hierarchies, and atomic requirement statements with zero loss.", 
                  icon: <Database className="w-7 h-7" /> 
                },
                { 
                  step: "03", 
                  title: "Cross-Document Matrix", 
                  desc: "Execute TF-IDF cosine similarity and token deltas to map AFFECTS, TRACEABLE_TO, and MODIFIED_FROM links.", 
                  icon: <Network className="w-7 h-7" /> 
                },
                { 
                  step: "04", 
                  title: "Continuous Assurance", 
                  desc: "Generate Story Points, backward-compatibility alerts, ambiguity deductions, and architecture graphs.", 
                  icon: <ShieldCheck className="w-7 h-7" /> 
                }
              ].map((s, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1, type: "spring", stiffness: 200, damping: 25 }}
                  className="group relative p-7 rounded-3xl neon-border overflow-hidden transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_20px_40px_-15px_rgba(96,165,250,0.15)] bg-slate-900/60 glass-card"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500/0 via-indigo-500/0 to-purple-500/0 group-hover:from-blue-500/10 group-hover:via-indigo-500/5 group-hover:to-transparent transition-all duration-700 opacity-0 group-hover:opacity-100 -z-10"></div>
                  
                  <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-6 bg-slate-800/60 border border-slate-700/60 text-slate-300 group-hover:bg-blue-600 group-hover:text-white group-hover:border-blue-400 group-hover:shadow-[0_0_30px_rgba(59,130,246,0.4)] transition-all duration-500 relative z-10">
                    {s.icon}
                  </div>
                  
                  <div className="absolute top-4 right-4 text-6xl font-black text-slate-800/40 select-none group-hover:text-blue-500/10 transition-colors duration-500 z-0">
                    {s.step}
                  </div>
                  
                  <h3 className="text-lg font-extrabold text-slate-50 mb-2 group-hover:text-blue-400 transition-colors duration-300 relative z-10">{s.title}</h3>
                  <p className="text-slate-400 text-xs sm:text-sm font-medium leading-relaxed relative z-10 group-hover:text-slate-300 transition-colors duration-300">{s.desc}</p>
                  
                  <div className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-blue-500 to-indigo-500 w-0 group-hover:w-full transition-all duration-500 ease-out"></div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* 5. Comparison: Legacy Review vs Software Intelligence Platform */}
        <div className="mt-36 max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-5xl font-extrabold text-slate-50 tracking-tight">Why Software Intelligence?</h2>
            <p className="text-slate-400 mt-3 text-base sm:text-lg">Replace subjective manual reviews with verified quantitative engineering assurance.</p>
          </div>
          <div className="bg-slate-900/90 rounded-3xl shadow-2xl shadow-neon-blue/10 border border-slate-800 overflow-hidden glass-card">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-800/50 border-b border-slate-800">
                  <th className="p-6 sm:p-8 text-base sm:text-lg font-bold text-slate-400 uppercase tracking-widest w-1/2">Manual Requirement Review</th>
                  <th className="p-6 sm:p-8 text-base sm:text-lg font-black text-neon-blue uppercase tracking-widest bg-slate-800/80 w-1/2">
                    <div className="flex items-center gap-3"><Zap className="w-5 h-5 text-amber-400"/> ReqVision Intelligence Platform</div>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {[
                  ["Manual scanning of disparate Word & PDF files", "Unified multi-document ingestion with full provenance tracking"],
                  ["Siloed Change Requests causing missed sprint scope", "Autonomous CR ↔ SRS linking with explicit AFFECTS relationships"],
                  ["Subjective story points & gut-feel estimation", "Algorithmic Story Points calculated from exact token delta"],
                  ["Undetected breaking changes & silent API drift", "Automated backward-compatibility audits & architecture chains"],
                  ["Hours wasted in manual compliance audits", "Instant export of high-fidelity, compliance-ready PDF reports"]
                ].map((row, i) => (
                  <tr key={i} className="hover:bg-slate-800/40 transition-colors group">
                    <td className="p-6 sm:p-8">
                      <div className="text-slate-400 font-medium text-sm sm:text-base flex items-center gap-3 sm:gap-4">
                        <XCircle className="w-5 h-5 text-slate-500 group-hover:text-red-400 transition-colors shrink-0"/> 
                        {row[0]}
                      </div>
                    </td>
                    <td className="p-6 sm:p-8 bg-slate-800/20">
                      <div className="text-slate-100 font-bold text-sm sm:text-base flex items-center gap-3 sm:gap-4">
                        <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0"/> 
                        {row[1]}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 6. Platform Capabilities Grid */}
        <div className="mt-36">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-5xl font-extrabold text-slate-50 tracking-tight">Core Platform Capabilities</h2>
            <p className="text-slate-400 mt-3 text-base sm:text-lg">Full-lifecycle requirement governance, traceability, and architectural verification.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 max-w-6xl mx-auto">
            {capabilities.map((c, i) => (
              <motion.div 
                whileHover={{ scale: 1.02, y: -2 }}
                key={i} 
                className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 shadow-sm hover:shadow-xl hover:border-neon-blue/60 transition-all cursor-default glass-card flex flex-col justify-between"
              >
                <div>
                  <div className="w-10 h-10 rounded-xl bg-neon-blue/10 border border-neon-blue/30 flex items-center justify-center text-neon-blue mb-4">
                    {c.icon}
                  </div>
                  <h3 className="font-bold text-slate-100 text-base mb-2">{c.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed font-medium">{c.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

      </div>

      {/* Footer */}
      <footer className="bg-transparent text-slate-400 py-16 mt-32 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-8 grid md:grid-cols-2 gap-12 items-center">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <BrainCircuit className="w-9 h-9 text-neon-blue" />
              <span className="text-2xl font-extrabold text-white tracking-tight">ReqVision<span className="text-neon-blue">AI</span></span>
            </div>
            <p className="text-slate-400 leading-relaxed max-w-md text-sm font-medium">
              Enterprise Software Intelligence Platform delivering continuous requirement drift analysis, multi-document traceability, and automated engineering assurance.
            </p>
          </div>
          <div className="flex md:justify-end gap-8 text-sm font-bold">
            <a href="https://github.com/PrathamMrana/ReqVision-AI--N" target="_blank" rel="noreferrer" className="hover:text-white transition-colors flex items-center gap-2">
              <Code className="w-4 h-4 text-neon-blue"/> GitHub
            </a>
            <a href="#" className="hover:text-white transition-colors flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-400"/> Architecture
            </a>
            <span className="flex items-center gap-2 text-slate-400">
              <Server className="w-4 h-4 text-emerald-400"/> Platform v2.0
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
