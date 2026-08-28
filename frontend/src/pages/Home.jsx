import { motion } from 'framer-motion';
import { useRef } from 'react';
import { Link } from 'react-router-dom';
import { 
  Database, Target, ArrowRight, Zap, 
  Activity, Clock, FileText, LayoutDashboard, FileOutput, Server, Code, XCircle, CheckCircle2, BrainCircuit,
  Sparkles, Network, GitPullRequest, Layers, ShieldCheck, Cpu
} from 'lucide-react';
import UploadBox from '../components/UploadBox';

// Modern, ultra-clean ambient glow background (no noisy dots)
const AmbientMeshBackground = () => {
  return (
    <div className="fixed inset-0 w-screen h-screen overflow-hidden -z-10 bg-[#06070B] pointer-events-none">
      {/* Top Center Primary Aurora Glow */}
      <div 
        className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[800px] sm:w-[1100px] h-[500px] rounded-full blur-[140px] opacity-25"
        style={{
          background: 'radial-gradient(circle, rgba(56,189,248,0.7) 0%, rgba(99,102,241,0.5) 45%, rgba(168,85,247,0.2) 75%, transparent 100%)'
        }}
      />
      {/* Subtle Bottom Ambient Accent */}
      <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[450px] bg-indigo-900/10 rounded-full blur-[160px]" />
      
      {/* Subtle Top Grid Texture with Vignette */}
      <div 
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(to right, #ffffff 1px, transparent 1px), linear-gradient(to bottom, #ffffff 1px, transparent 1px)`,
          backgroundSize: '48px 48px'
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#06070B]/70 to-[#06070B]" />
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
    <div className="relative min-h-screen bg-[#06070B] overflow-hidden font-sans text-slate-100 selection:bg-neon-blue/30 selection:text-white">
      <AmbientMeshBackground />

      {/* Sleek Minimalist Navbar */}
      <nav className="w-full max-w-7xl mx-auto px-6 py-6 flex justify-between items-center z-50 relative">
        <div className="flex items-center gap-2.5">
          <BrainCircuit className="w-7 h-7 text-neon-blue" />
          <span className="text-lg font-bold text-white tracking-tight">
            ReqVision<span className="text-neon-blue">AI</span>
          </span>
        </div>
        <div className="flex gap-6 items-center">
          <Link to="/dashboard" className="hidden md:block text-xs font-semibold text-slate-400 hover:text-white transition-colors">Dashboard</Link>
          <button onClick={scrollToDemo} className="hidden md:block text-xs font-semibold text-slate-400 hover:text-white transition-colors">Platform Engine</button>
          <a href="https://github.com/PrathamMrana/ReqVision-AI--N" target="_blank" rel="noreferrer" className="hidden md:flex text-xs font-semibold text-slate-400 hover:text-white transition-colors items-center gap-1.5">
            <Code className="w-3.5 h-3.5 text-neon-blue"/> GitHub
          </a>
          <div className="w-px h-5 bg-slate-800 hidden md:block"></div>
          <button onClick={scrollToDemo} className="px-4 py-2 bg-neon-blue/15 hover:bg-neon-blue/25 text-neon-blue border border-neon-blue/40 rounded-lg text-xs font-bold transition-all shadow-sm hover:shadow-[0_0_15px_rgba(56,189,248,0.25)]">
            Launch Platform
          </button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-10 sm:pt-16 pb-24">
        
        {/* 1. Ultra-Clean, High-Impact Hero Section */}
        <div className="text-center max-w-4xl mx-auto">
          
          {/* Subtle Platform Pill */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-slate-900/90 border border-slate-700/60 text-slate-300 text-xs font-medium mb-6 shadow-sm backdrop-blur-xl"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-white font-semibold">Software Intelligence Platform</span>
            <span className="w-1 h-1 rounded-full bg-slate-600"></span>
            <span className="text-slate-400">Continuous Assurance</span>
          </motion.div>
          
          {/* Main Headline */}
          <motion.h1 
            initial={{ opacity: 0, y: -12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.05 }}
            className="text-4xl sm:text-5xl md:text-6xl font-black text-white tracking-tight leading-[1.15] max-w-3xl mx-auto"
          >
            Software Intelligence <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-200 to-purple-400 font-extrabold">
              Requirements · Traceability · Assurance
            </span>
          </motion.h1>
          
          {/* Subheading */}
          <motion.p 
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.5 }}
            className="mt-6 text-sm sm:text-base md:text-lg text-slate-400 leading-relaxed max-w-2xl mx-auto font-normal"
          >
            The autonomous intelligence platform for engineering teams. Ingest BRDs, SRS, Change Requests, and Technical Specs to eliminate scope creep, map cross-document traceability, and guarantee continuous architectural assurance before code is shipped.
          </motion.p>
          
          {/* Primary Action Buttons */}
          <motion.div 
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15, duration: 0.5 }}
            className="mt-8 flex flex-col sm:flex-row justify-center items-center gap-3.5"
          >
            <motion.button 
              whileHover={{ scale: 1.02, y: -1 }}
              whileTap={{ scale: 0.98 }}
              onClick={scrollToDemo} 
              className="w-full sm:w-auto px-7 py-3.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold shadow-lg shadow-blue-900/30 transition-all flex items-center justify-center gap-2 text-sm sm:text-base"
            >
              Launch Intelligence Engine <ArrowRight className="w-4 h-4" />
            </motion.button>
            <motion.button 
              whileHover={{ scale: 1.02, y: -1 }}
              whileTap={{ scale: 0.98 }}
              onClick={scrollToDemo} 
              className="w-full sm:w-auto px-7 py-3.5 bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-700/80 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 text-sm sm:text-base"
            >
              Explore Traceability Matrix
            </motion.button>
          </motion.div>

          {/* Minimalist Feature Tags */}
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25, duration: 0.5 }}
            className="mt-10 flex flex-wrap justify-center items-center gap-2"
          >
            {["Multi-Source Ingestion", "Cross-Doc Traceability", "Deterministic NLP Engine", "Architectural Assurance"].map((tag, idx) => (
              <span key={idx} className="px-3 py-1 rounded-full bg-slate-900/60 border border-slate-800 text-slate-400 text-xs font-medium">
                {tag}
              </span>
            ))}
          </motion.div>
        </div>

        {/* 2. Live Demo / Upload Box */}
        <div className="mt-20 scroll-mt-20" ref={demoRef}>
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-blue-400 mb-2">
              <Zap className="w-3.5 h-3.5 text-amber-400" /> Interactive Workbench
            </div>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">Software Intelligence Engine</h2>
            <p className="text-slate-400 mt-2 max-w-xl mx-auto text-sm sm:text-base font-normal">
              Upload multiple baseline documents and updated specifications to generate an end-to-end requirement drift, provenance, and cross-document assurance audit.
            </p>
          </div>
          <motion.div
            initial={{ opacity: 0, scale: 0.99 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="relative z-10"
          >
            <UploadBox />
          </motion.div>
        </div>

        {/* 3. The 4-Stage Software Intelligence Pipeline */}
        <div className="mt-32">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-indigo-400 mb-2">
              <Activity className="w-3.5 h-3.5 text-indigo-400" /> Architectural Workflow
            </div>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">How Software Intelligence Works</h2>
            <p className="text-slate-400 mt-2 text-sm sm:text-base max-w-lg mx-auto">
              A deterministic 4-stage pipeline translating fragmented specifications into verifiable engineering truth.
            </p>
          </div>
          
          <div className="relative max-w-5xl mx-auto">
            <div className="hidden md:block absolute top-16 left-10 w-[calc(100%-5rem)] h-[1px] bg-gradient-to-r from-transparent via-blue-500/30 to-transparent -z-10"></div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-5">
              {[
                { 
                  step: "01", 
                  title: "Multi-Source Ingestion", 
                  desc: "Ingest BRD, SRS, Change Requests, User Stories, and Test Specs in TXT, DOCX, or PDF formats simultaneously.", 
                  icon: <FileText className="w-5 h-5" /> 
                },
                { 
                  step: "02", 
                  title: "Provenance & Extraction", 
                  desc: "Preserve document provenance, source hierarchies, and atomic requirement statements with zero loss.", 
                  icon: <Database className="w-5 h-5" /> 
                },
                { 
                  step: "03", 
                  title: "Cross-Document Matrix", 
                  desc: "Execute TF-IDF cosine similarity and token deltas to map AFFECTS, TRACEABLE_TO, and MODIFIED_FROM links.", 
                  icon: <Network className="w-5 h-5" /> 
                },
                { 
                  step: "04", 
                  title: "Continuous Assurance", 
                  desc: "Generate Story Points, backward-compatibility alerts, ambiguity deductions, and architecture graphs.", 
                  icon: <ShieldCheck className="w-5 h-5" /> 
                }
              ].map((s, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.08, duration: 0.4 }}
                  className="group relative p-6 rounded-2xl border border-slate-800 bg-slate-900/50 backdrop-blur-md overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:border-slate-700"
                >
                  <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-4 bg-slate-800 border border-slate-700 text-slate-300 group-hover:bg-blue-600 group-hover:text-white group-hover:border-blue-400 transition-all duration-300">
                    {s.icon}
                  </div>
                  
                  <div className="absolute top-3 right-3 text-4xl font-black text-slate-800/40 select-none">
                    {s.step}
                  </div>
                  
                  <h3 className="text-base font-bold text-white mb-1.5 group-hover:text-blue-400 transition-colors duration-200">{s.title}</h3>
                  <p className="text-slate-400 text-xs font-normal leading-relaxed">{s.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* 4. Comparison: Legacy Review vs Software Intelligence Platform */}
        <div className="mt-32 max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">Why Software Intelligence?</h2>
            <p className="text-slate-400 mt-2 text-sm sm:text-base">Replace subjective manual reviews with verified quantitative engineering assurance.</p>
          </div>
          <div className="bg-slate-900/70 rounded-2xl border border-slate-800 overflow-hidden backdrop-blur-md">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-800/60 border-b border-slate-800">
                  <th className="p-5 sm:p-6 text-xs sm:text-sm font-bold text-slate-400 uppercase tracking-widest w-1/2">Manual Requirement Review</th>
                  <th className="p-5 sm:p-6 text-xs sm:text-sm font-extrabold text-blue-400 uppercase tracking-widest bg-slate-800/80 w-1/2">
                    <div className="flex items-center gap-2"><Zap className="w-4 h-4 text-amber-400"/> ReqVision Intelligence Platform</div>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80 text-xs sm:text-sm">
                {[
                  ["Manual scanning of disparate Word & PDF files", "Unified multi-document ingestion with full provenance tracking"],
                  ["Siloed Change Requests causing missed sprint scope", "Autonomous CR ↔ SRS linking with explicit AFFECTS relationships"],
                  ["Subjective story points & gut-feel estimation", "Algorithmic Story Points calculated from exact token delta"],
                  ["Undetected breaking changes & silent API drift", "Automated backward-compatibility audits & architecture chains"],
                  ["Hours wasted in manual compliance audits", "Instant export of high-fidelity, compliance-ready PDF reports"]
                ].map((row, i) => (
                  <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-4 sm:p-5 text-slate-400 font-normal flex items-center gap-3">
                      <XCircle className="w-4 h-4 text-slate-500 shrink-0"/> 
                      {row[0]}
                    </td>
                    <td className="p-4 sm:p-5 bg-slate-800/20 text-slate-200 font-semibold">
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0"/> 
                        {row[1]}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 5. Platform Capabilities Grid */}
        <div className="mt-32">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">Core Platform Capabilities</h2>
            <p className="text-slate-400 mt-2 text-sm sm:text-base">Full-lifecycle requirement governance, traceability, and architectural verification.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto">
            {capabilities.map((c, i) => (
              <motion.div 
                whileHover={{ scale: 1.02, y: -2 }}
                key={i} 
                className="p-5 rounded-xl border border-slate-800 bg-slate-900/50 shadow-sm hover:border-slate-700 transition-all cursor-default backdrop-blur-sm flex flex-col justify-between"
              >
                <div>
                  <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-3">
                    {c.icon}
                  </div>
                  <h3 className="font-bold text-white text-sm mb-1.5">{c.title}</h3>
                  <p className="text-[11px] text-slate-400 leading-relaxed font-normal">{c.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

      </div>

      {/* Clean Footer */}
      <footer className="bg-transparent text-slate-400 py-12 mt-28 border-t border-slate-800/80">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-8 items-center">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <BrainCircuit className="w-6 h-6 text-blue-400" />
              <span className="text-lg font-bold text-white tracking-tight">ReqVision<span className="text-blue-400">AI</span></span>
            </div>
            <p className="text-slate-400 text-xs font-normal max-w-md">
              Enterprise Software Intelligence Platform delivering continuous requirement drift analysis, multi-document traceability, and automated engineering assurance.
            </p>
          </div>
          <div className="flex md:justify-end gap-6 text-xs font-semibold">
            <a href="https://github.com/PrathamMrana/ReqVision-AI--N" target="_blank" rel="noreferrer" className="hover:text-white transition-colors flex items-center gap-1.5">
              <Code className="w-3.5 h-3.5 text-blue-400"/> GitHub
            </a>
            <a href="#" className="hover:text-white transition-colors flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-indigo-400"/> Architecture
            </a>
            <span className="flex items-center gap-1.5 text-slate-500">
              <Server className="w-3.5 h-3.5 text-emerald-400"/> v2.0
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
