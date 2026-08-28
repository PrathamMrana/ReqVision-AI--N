import { useState, useMemo, useRef, useEffect } from 'react';
import { useLocation, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, Activity, CheckCircle2, AlertTriangle, PlusCircle, 
  XCircle, Filter, Download, Zap, ShieldAlert, BarChart3, Clock, Search, ChevronLeft, ChevronRight,
  GitPullRequest, Layers, Network, FolderGit2
} from 'lucide-react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import StatCard from '../components/StatCard';
import DiffCard from '../components/DiffCard';
import QualityDashboard from '../components/QualityDashboard';
import TraceabilityMatrix from '../components/TraceabilityMatrix';
import ImpactAnalysis from '../components/ImpactAnalysis';
import ProjectTraceabilityDashboard from '../components/ProjectTraceabilityDashboard';

export default function Dashboard() {
  const location = useLocation();
  const printRef = useRef(null);
  const result = location.state?.result;
  
  if (!result) {
    return <Navigate to="/" replace />;
  }

  // If Phase 2 Project Intelligence Mode
  if (result.mode === 'project_intelligence') {
    return <ProjectTraceabilityDashboard result={result} />;
  }

  const [filter, setFilter] = useState('All');
  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const changes = result?.changes || [];

  const filteredChanges = useMemo(() => {
    return changes.filter(c => {
      const matchFilter = filter === 'All' || c.status === filter;
      const term = search.toLowerCase();
      const matchSearch = (c.old && c.old.toLowerCase().includes(term)) || 
                          (c.new && c.new.toLowerCase().includes(term)) ||
                          (c.module && c.module.toLowerCase().includes(term)) ||
                          (c.req_id && c.req_id.toLowerCase().includes(term));
      return matchFilter && matchSearch;
    });
  }, [changes, filter, search]);

  useEffect(() => {
    setCurrentPage(1);
  }, [filter, search]);

  const { metrics, executive_summary, module_impact, quality_summary, impact_analysis, statistics, cross_document_analysis } = result;

  const handlePrint = () => {
    window.print();
  };

  const handleRowClick = (req_id) => {
    const idx = filteredChanges.findIndex(c => c.req_id === req_id);
    if (idx !== -1) {
      setCurrentPage(idx + 1);
      const timelineEl = document.getElementById('timeline-section');
      if (timelineEl) {
        timelineEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  };

  const COLORS = {
    Unchanged: '#10b981',
    Modified: '#f59e0b',
    Added: '#3b82f6',
    Removed: '#ef4444'
  };

  const pieData = Object.entries(metrics.counts).map(([name, value]) => ({ name, value }));
  const docStats = cross_document_analysis?.statistics;

  return (
    <div className="bg-transparent min-h-screen py-8" ref={printRef}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header & Export */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4 print:hidden">
          <div>
            <h1 className="text-3xl font-bold text-slate-50">Analysis Dashboard</h1>
            <p className="text-slate-400 mt-1">Intelligent review of requirement drift and cross-document traceability</p>
          </div>
          <button 
            onClick={handlePrint}
            className="flex items-center gap-2 bg-slate-900 border border-slate-700 text-slate-300 hover:bg-slate-800 px-4 py-2 rounded-lg shadow-sm font-medium transition-colors"
          >
            <Download className="w-4 h-4" />
            Export PDF Report
          </button>
        </div>

        {/* Print Header (Visible only when printing) */}
        <div className="hidden print:flex fixed top-0 left-0 w-full justify-between items-center text-[9px] text-slate-400 border-b border-slate-700 pb-1 pt-1 bg-slate-900 z-50 px-8">
          <span className="font-bold text-slate-200">ReqVision AI | Requirement Drift & Cross-Document Report</span>
          <span>Generated on {executive_summary.comparison_date || new Date().toLocaleDateString()}</span>
        </div>
        
        {/* Print Page 1 Header */}
        <div className="hidden print:block mb-8 border-b pb-4 print:mt-12">
          <h1 className="text-3xl font-bold text-slate-50">ReqVision AI - Executive Report</h1>
          <p className="text-slate-400 mt-1">Generated automatically via Lexical Multi-Document Comparison</p>
        </div>

        {/* Executive Summary */}
        <div className="glass-card p-8 mb-8 bg-slate-900/60 border border-slate-700/50 shadow-neon-blue/10 shadow-xl neon-border border-t-4 border-primary-500">
          <div className="flex items-center gap-3 mb-4">
            <div className={`p-2 rounded-lg ${executive_summary.overall_risk === 'High' ? 'bg-red-900/40 text-red-400 border border-red-900' : 'bg-neon-blue/20 text-neon-blue border border-neon-blue/40 shadow-neon-glow'}`}>
              <ShieldAlert className="w-6 h-6" />
            </div>
            <h2 className="text-2xl font-bold text-slate-50">Executive AI Summary</h2>
            <span className={`ml-auto px-4 py-1.5 rounded-full text-sm font-bold ${ executive_summary.overall_risk === 'High' ? 'bg-red-900/40 text-red-400 border border-red-900 shadow-[0_0_10px_rgba(239,68,68,0.2)]' : executive_summary.overall_risk === 'Medium' ? 'bg-amber-900/40 text-amber-400 border border-amber-900 shadow-[0_0_10px_rgba(245,158,11,0.2)]' : 'bg-emerald-900/40 text-emerald-400 border border-emerald-900 shadow-[0_0_10px_rgba(16,185,129,0.2)]' }`}>
              Overall Risk: {executive_summary.overall_risk}
            </span>
          </div>
          
          <div className="flex flex-wrap gap-4 mb-8 text-sm text-slate-400 bg-slate-900/50 p-3 rounded-lg border border-slate-800">
            <span className="flex items-center gap-1.5"><Clock className="w-4 h-4 text-slate-400" /> Date: {executive_summary.comparison_date || 'N/A'}</span>
            <span className="flex items-center gap-1.5"><FileText className="w-4 h-4 text-slate-400" /> Baseline: {executive_summary.baseline_version || 'v1.0'}</span>
            <span className="flex items-center gap-1.5"><FileText className="w-4 h-4 text-slate-400" /> Updated: {executive_summary.updated_version || 'v2.0'}</span>
            <span className="flex items-center gap-1.5"><ShieldAlert className="w-4 h-4 text-emerald-500" /> Analysis Confidence: {executive_summary.analysis_confidence || executive_summary.ai_confidence || 'High'}</span>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">Overall Assessment</h3>
              <p className="text-slate-200 text-lg leading-relaxed">{executive_summary.assessment}</p>
              
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mt-6 mb-2">Recommendation</h3>
              <p className="font-medium p-4 bg-amber-950/30 border border-amber-900/50 rounded-xl text-amber-200">
                {executive_summary.recommendation}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">Business Impact</h3>
              <ul className="space-y-3 mb-6">
                {executive_summary.business_impact.map((impact, i) => (
                  <li key={i} className="flex items-start gap-3 text-slate-300">
                    <CheckCircle2 className="w-5 h-5 text-primary-500 shrink-0 mt-0.5" />
                    <span>{impact}</span>
                  </li>
                ))}
              </ul>

              {executive_summary.top_risks && (
                <>
                  <h3 className="text-sm font-semibold text-red-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4 text-red-500" /> Top Risks
                  </h3>
                  <ul className="space-y-2.5 bg-red-950/40 p-4 rounded-xl border border-red-900/50">
                    {executive_summary.top_risks.map((risk, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-xs font-bold text-red-300">
                        <span className="text-red-500 font-extrabold">•</span>
                        <span>{risk}</span>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Cross-Document Provenance Banner */}
        {docStats && (
          <div className="glass-card p-6 mb-8 bg-slate-900/40 border border-slate-800 rounded-2xl">
            <div className="flex items-center gap-2 mb-4">
              <FolderGit2 className="w-5 h-5 text-neon-blue" />
              <h3 className="text-base font-bold text-slate-200 uppercase tracking-wider">Cross-Document Analysis Provenance</h3>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
                <div className="text-[10px] uppercase font-bold text-slate-400">Total Documents</div>
                <div className="text-xl font-mono font-extrabold text-neon-blue mt-1">{docStats.documents_analyzed}</div>
                <div className="text-[10px] text-slate-500">{docStats.baseline_documents} Base / {docStats.updated_documents} Up</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
                <div className="text-[10px] uppercase font-bold text-slate-400">Relationships</div>
                <div className="text-xl font-mono font-extrabold text-primary-400 mt-1">{docStats.cross_document_relationships}</div>
                <div className="text-[10px] text-slate-500">Cross-Doc Links</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
                <div className="text-[10px] uppercase font-bold text-slate-400">Traceable Reqs</div>
                <div className="text-xl font-mono font-extrabold text-emerald-400 mt-1">{docStats.requirements_with_traceability}</div>
                <div className="text-[10px] text-slate-500">With Target Links</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
                <div className="text-[10px] uppercase font-bold text-slate-400">Change Requests</div>
                <div className="text-xl font-mono font-extrabold text-purple-400 mt-1">{docStats.change_requests_linked}</div>
                <div className="text-[10px] text-purple-400/80">Affects Links</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
                <div className="text-[10px] uppercase font-bold text-slate-400">BRD Requirements</div>
                <div className="text-xl font-mono font-extrabold text-cyan-400 mt-1">{docStats.brd_requirements_traced}</div>
                <div className="text-[10px] text-cyan-400/80">Traceable to SRS</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
                <div className="text-[10px] uppercase font-bold text-slate-400">Avg Similarity</div>
                <div className="text-xl font-mono font-extrabold text-amber-400 mt-1">{metrics.average_similarity}%</div>
                <div className="text-[10px] text-slate-500">Lexical Cosine</div>
              </div>
            </div>
          </div>
        )}

        {/* KPIs Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard title="Total Requirements" value={changes.length} subtitle={`From ${metrics.total_baseline} original`} icon={<FileText />} trendColor="text-primary-500" delay={0.1} />
          <StatCard title="Scope Creep Index" value={`${metrics.scope_creep_index}%`} subtitle="Based on added reqs" icon={<Activity />} trendColor={metrics.scope_creep_index > 10 ? "text-red-500" : "text-emerald-500"} delay={0.2} />
          <StatCard title="Volatility Score" value={`${metrics.volatility_score}%`} subtitle="Modifications & Additions" icon={<AlertTriangle />} trendColor={metrics.volatility_score > 20 ? "text-amber-500" : "text-emerald-500"} delay={0.3} />
          <StatCard title="Avg. Similarity" value={`${metrics.average_similarity}%`} subtitle="TF-IDF cosine similarity" icon={<Zap />} trendColor="text-primary-500" delay={0.4} />
        </div>

        {/* Quality Dashboard */}
        <QualityDashboard quality_summary={quality_summary} />

        {/* Detailed Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard title="Unchanged" value={metrics.counts.Unchanged} icon={<CheckCircle2 />} trendColor="text-emerald-500" delay={0.5} />
          <StatCard title="Modified" value={metrics.counts.Modified} icon={<AlertTriangle />} trendColor="text-amber-500" delay={0.6} />
          <StatCard title="Added" value={metrics.counts.Added} icon={<PlusCircle />} trendColor="text-primary-500" delay={0.7} />
          <StatCard title="Removed" value={metrics.counts.Removed} icon={<XCircle />} trendColor="text-red-500" delay={0.8} />
        </div>

        {/* Visual Analytics & Module Impact */}
        <div className="grid lg:grid-cols-2 gap-8 mb-8 break-inside-avoid">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="rounded-2xl border border-slate-800 p-6 shadow-sm hover:shadow-xl hover:border-neon-blue/50 transition-all duration-300 glass-card"
          >
            <h3 className="text-lg font-extrabold text-slate-200 mb-6 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary-500" /> Requirement Distribution
            </h3>
            <div className="h-64 relative">
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none mt-[-20px]">
                <span className="text-3xl font-extrabold text-slate-200">{changes.length}</span>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Total</span>
              </div>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[entry.name]} className="hover:opacity-80 transition-opacity duration-300 cursor-pointer focus:outline-none" />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}
                    itemStyle={{ fontWeight: 'bold' }}
                  />
                  <Legend wrapperStyle={{ paddingTop: '20px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="rounded-2xl border border-slate-800 p-6 shadow-sm hover:shadow-xl hover:border-neon-blue/50 transition-all duration-300 glass-card"
          >
            <h3 className="text-lg font-extrabold text-slate-200 mb-6 flex items-center gap-2">
              <Activity className="w-5 h-5 text-accent-500" /> Functional Module Impact
            </h3>
            <div className="space-y-4 max-h-[250px] overflow-y-auto pr-2 custom-scrollbar">
              {module_impact.map((mod, i) => (
                <motion.div 
                  key={i} 
                  whileHover={{ scale: 1.02, x: 4 }}
                  className="flex flex-col gap-1.5 p-2 rounded-xl hover:bg-slate-800 transition-colors cursor-default"
                >
                  <div className="flex justify-between text-sm">
                    <span className="font-bold text-slate-300">{mod.module}</span>
                    <span className="font-semibold text-slate-400">{mod.changed} changes ({mod.impact_pct}%)</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(mod.impact_pct, 100)}%` }}
                      transition={{ duration: 1.5, ease: "easeOut", delay: i * 0.1 }}
                      className={`h-full rounded-full bg-gradient-to-r ${mod.risk === 'High' ? 'from-red-400 to-red-500' : mod.risk === 'Medium' ? 'from-amber-400 to-amber-500' : 'from-primary-400 to-primary-500'}`} 
                    />
                  </div>
                </motion.div>
              ))}
              {module_impact.length === 0 && (
                <p className="text-slate-400 text-sm font-medium text-center py-8">No significant module changes detected.</p>
              )}
            </div>
          </motion.div>
        </div>

        {/* Impact Analysis */}
        <ImpactAnalysis impact_analysis={impact_analysis} />

        {/* Traceability Matrix */}
        <TraceabilityMatrix 
          changes={changes} 
          cross_document_analysis={cross_document_analysis} 
          onRowClick={handleRowClick} 
        />

        {/* Requirement Timeline */}
        <div id="timeline-section" className="mb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 print:hidden pt-8">
          <h2 className="text-2xl font-bold text-slate-50">Requirement Timeline</h2>
          
          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input 
                type="text" 
                placeholder="Search requirements..." 
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="pl-9 pr-4 py-2 rounded-lg border border-slate-700 text-sm focus:ring-2 focus:ring-primary-500 outline-none w-full sm:w-64"
              />
            </div>
            <div className="relative">
              <Filter className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <select 
                value={filter}
                onChange={e => setFilter(e.target.value)}
                className="pl-9 pr-8 py-2 rounded-lg border border-slate-700 text-sm focus:ring-2 focus:ring-primary-500 outline-none appearance-none bg-slate-900"
              >
                <option value="All">All Statuses</option>
                <option value="Unchanged">Unchanged</option>
                <option value="Modified">Modified</option>
                <option value="Added">Added</option>
                <option value="Removed">Removed</option>
              </select>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          {filteredChanges.length > 0 ? (
            <>
              {/* Interactive Paginated View (Hidden on print) */}
              <div className="print:hidden">
                <AnimatePresence mode="wait">
                  {filteredChanges.slice((currentPage - 1), currentPage).map((change) => (
                    <DiffCard key={change.req_id} change={change} index={0} />
                  ))}
                </AnimatePresence>
                
                {filteredChanges.length > 1 && (
                  <div className="flex justify-between items-center p-4 rounded-xl border border-slate-700 shadow-sm mt-6 hover:shadow-md transition-shadow glass-card">
                    <button 
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-300 bg-transparent rounded-lg border border-slate-700 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <ChevronLeft className="w-4 h-4" /> Previous
                    </button>
                    <span className="text-sm font-semibold text-slate-400">
                      Requirement {currentPage} of {filteredChanges.length}
                    </span>
                    <button 
                      onClick={() => setCurrentPage(p => Math.min(filteredChanges.length, p + 1))}
                      disabled={currentPage === filteredChanges.length}
                      className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-300 bg-transparent rounded-lg border border-slate-700 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Next <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>

              {/* Print-Only Full List View (Hidden on screen) */}
              <div className="hidden print:block space-y-8">
                {filteredChanges.map((change, index) => (
                  <div key={`print-${change.req_id}`} className="break-inside-avoid">
                    <DiffCard change={change} index={index} />
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-12 glass-panel">
              <p className="text-slate-400">No requirements match your filters.</p>
            </div>
          )}
        </div>

        {/* Footer with Execution Statistics */}
        <footer className="mt-16 pt-8 border-t border-slate-700 pb-12 print:mt-8 print:pb-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6 text-sm text-slate-400 font-medium">
            <div className="flex flex-wrap justify-center items-center gap-4 md:gap-8">
              <span className="flex items-center gap-1.5"><Clock className="w-4 h-4"/> {statistics.execution_time_ms}ms execution</span>
              <span className="flex items-center gap-1.5"><Zap className="w-4 h-4"/> {statistics.similarity_calculations} TF-IDF comparisons</span>
              <span className="flex items-center gap-1.5"><Activity className="w-4 h-4"/> TF-IDF + Cosine Sim algorithm</span>
            </div>
            <div className="flex items-center gap-6">
              <span className="font-semibold text-slate-300">ReqVision AI v1.0</span>
              <a href="https://github.com/PrathamMrana/ReqVision-AI" target="_blank" rel="noopener noreferrer" className="hover:text-primary-600 transition-colors">GitHub</a>
              <a href="#" className="hover:text-primary-600 transition-colors">Documentation</a>
            </div>
          </div>
        </footer>

      </div>
    </div>
  );
}
