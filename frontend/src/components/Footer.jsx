import { useLocation } from 'react-router-dom';

export default function Footer() {
  const location = useLocation();
  if (location.pathname === '/') return null;

  return (
    <footer className="w-full bg-slate-900 text-slate-400 py-12 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex flex-col items-center md:items-start gap-2">
            <span className="font-bold text-xl tracking-tight text-white">
              ReqVision <span className="text-primary-500">AI</span>
            </span>
            <p className="text-sm text-slate-400 max-w-sm text-center md:text-left">
              Intelligent Requirement Drift & Scope Impact Analysis Platform. Built for modern software engineering teams.
            </p>
          </div>
          <div className="flex gap-6 text-sm font-medium">
            <a href="#" className="hover:text-white transition-colors">Documentation</a>
            <a href="#" className="hover:text-white transition-colors">API</a>
            <a href="#" className="hover:text-white transition-colors">GitHub</a>
          </div>
        </div>
        <div className="mt-12 pt-8 border-t border-slate-800 text-sm text-center">
          &copy; {new Date().getFullYear()} ReqVision AI. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
