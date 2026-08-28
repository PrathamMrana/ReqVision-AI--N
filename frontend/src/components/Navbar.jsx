import { Link, useLocation } from 'react-router-dom';
import { BrainCircuit } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();
  if (location.pathname === '/') return null;

  return (
    <nav className="print:hidden sticky top-0 z-50 w-full glass-card rounded-none border-b border-slate-700/50 bg-slate-950/80 backdrop-blur-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2">
              <BrainCircuit className="h-8 w-8 text-neon-blue" />
              <span className="font-bold text-xl tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">
                ReqVision <span className="text-gradient">AI</span>
              </span>
            </Link>
          </div>
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-slate-400 hover:text-neon-blue hover:shadow-neon-blue/20 transition-all duration-300 transition-colors font-medium">
              Home
            </Link>
            <Link to="/dashboard" className="text-slate-400 hover:text-neon-blue hover:shadow-neon-blue/20 transition-all duration-300 transition-colors font-medium">
              Dashboard
            </Link>
            <a 
              href="https://github.com/PrathamMrana/ReqVision-AI"
              target="_blank" 
              rel="noreferrer"
              className="bg-neon-blue/20 hover:bg-neon-blue/30 text-white neon-border shadow-neon-glow px-5 py-2 rounded-full font-medium transition-colors shadow-lg shadow-neon-blue/30 hover:shadow-[0_0_20px_var(--color-neon-blue)]"
            >
              Star on GitHub
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}
