import React, { useState, useMemo, useEffect } from 'react';
import { 
  FileText, Database, Layers, CheckCircle2, AlertTriangle, AlertCircle, 
  Search, ShieldAlert, Download, Sparkles, Filter, ChevronRight, Activity,
  GitPullRequest, Clock, Server, Check, X, Network, Link2, ArrowRight,
  Shield, Cpu, Zap, Compass, BarChart3, ChevronDown, Eye, Terminal,
  Sliders, AlertOctagon, HelpCircle, CornerDownRight, ExternalLink
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ProjectTraceabilityDashboard({ result }) {
  // Navigation tabs: 'overview' | 'matrix' | 'graph' | 'chains' | 'impact' | 'quality'
  const [activeTab, setActiveTab] = useState('overview');
  
  // Matrix Filters
  const [statusFilter, setStatusFilter] = useState('All');
  const [relFilter, setRelFilter] = useState('All');
  const [layerFilter, setLayerFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedRows, setExpandedRows] = useState({});

  // Slide-over Drawer State
  const [drawerArtifact, setDrawerArtifact] = useState(null);
  const [drawerRelationship, setDrawerRelationship] = useState(null);

  // Command Palette (Cmd+K)
  const [isCommandOpen, setIsCommandOpen] = useState(false);
  const [commandQuery, setCommandQuery] = useState('');

  // Graph state
  const [selectedGraphNode, setSelectedGraphNode] = useState(null);
  const [graphLayerFilter, setGraphLayerFilter] = useState('All');

  // Backend Payload Data
  const summary = result.summary || {};
  const matrix = result.traceability_matrix || result.relationships || [];
  const chains = result.traceability_chains || result.chains || [];
  const graph = result.traceability_graph || result.graph || { nodes: [], edges: [] };
  const allArtifacts = result.artifacts || [];
  const documents = result.documents || [];
  const topConflicts = result.top_conflicts || result.conflicts || [];
  const topUnmapped = result.top_unmapped || result.gaps || [];
  const crImpacts = result.change_request_impacts || [];
  const momLinks = result.meeting_minutes_links || [];

  // Phase B Intelligence Metrics from Canonical Store
  const healthScore = result.software_health_score || {
    overall_score: summary.coverage_percentage || 0,
    grade: summary.coverage_percentage >= 90 ? 'A' : summary.coverage_percentage >= 75 ? 'B' : 'C',
    formula: '30% Traceability + 25% Verification + 20% Implementation + 15% Conflict Cleanliness + 10% NFR Coverage',
    breakdown: {
      traceability_completeness: { score: summary.coverage_percentage || 0, weight: '30%' },
      verification_coverage: { score: 85, weight: '25%' },
      implementation_fidelity: { score: 90, weight: '20%' },
      conflict_stability: { score: Math.max(0, 100 - (topConflicts.length * 15)), weight: '15%' },
      nfr_assurance: { score: 100, weight: '10%' }
    }
  };

  const riskRadar = result.risk_radar || [];
  const requirementQuality = result.requirement_quality || [];
  const testIntelligence = result.test_intelligence || {
    total_test_cases: 0,
    mapped_test_cases: 0,
    unmapped_test_cases: 0,
    verified_stories_count: 0,
    total_stories_count: 0,
    verification_rate: '0%',
    test_gaps: []
  };
  const changeImpactSummary = result.change_impact_summary || {
    total_change_requests: 0,
    active_change_impacts: crImpacts.length,
    direct_impact_items: crImpacts,
    derived_impacts: []
  };

  const semanticEnabled = result.semantic_enabled === true;
  const semanticModel = result.semantic_model || 'sentence-transformers/all-mpnet-base-v2';
  const analysisMode = result.analysis_mode || 'hybrid_semantic_lexical';

  // Keyboard shortcut listener for Cmd+K / Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCommandOpen(prev => !prev);
      }
      if (e.key === 'Escape') {
        setIsCommandOpen(false);
        setDrawerArtifact(null);
        setDrawerRelationship(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Filtered Matrix Rows
  const filteredMatrix = useMemo(() => {
    return matrix.filter(row => {
      const matchStatus = statusFilter === 'All' || row.status === statusFilter;
      const matchRel = relFilter === 'All' || row.relationship === relFilter;
      const matchLayer = layerFilter === 'All' || row.source_type === layerFilter || row.target_type === layerFilter;
      
      const term = searchQuery.toLowerCase().trim();
      if (!term) return matchStatus && matchRel && matchLayer;

      const sId = (row.source_artifact || '').toLowerCase();
      const sText = (row.source_text || '').toLowerCase();
      const tId = (row.target_artifact || '').toLowerCase();
      const tText = (row.target_text || '').toLowerCase();
      const rel = (row.relationship || '').toLowerCase();
      const ev = (row.evidence || '').toLowerCase();

      const matchSearch = sId.includes(term) || sText.includes(term) || tId.includes(term) || tText.includes(term) || rel.includes(term) || ev.includes(term);
      return matchStatus && matchRel && matchLayer && matchSearch;
    });
  }, [matrix, statusFilter, relFilter, layerFilter, searchQuery]);

  // Command Palette Results
  const commandResults = useMemo(() => {
    if (!commandQuery.trim()) return allArtifacts.slice(0, 10);
    const q = commandQuery.toLowerCase();
    return allArtifacts.filter(a => 
      (a.artifact_id || '').toLowerCase().includes(q) ||
      (a.text || '').toLowerCase().includes(q) ||
      (a.document_type || '').toLowerCase().includes(q) ||
      (a.document_name || '').toLowerCase().includes(q)
    ).slice(0, 15);
  }, [allArtifacts, commandQuery]);

  const toggleRowExpand = (idx) => {
    setExpandedRows(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const openArtifactDrawer = (artId) => {
    const found = allArtifacts.find(a => a.artifact_id === artId);
    if (found) {
      setDrawerArtifact(found);
      setDrawerRelationship(null);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'MATCHED':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">MATCHED</span>;
      case 'PARTIAL':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">PARTIAL</span>;
      case 'CONFLICT':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">CONFLICT</span>;
      default:
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-slate-800 text-slate-400 border border-slate-700">UNMAPPED</span>;
    }
  };

  const getRelBadge = (rel) => {
    switch (rel) {
      case 'TRACEABLE_TO': return 'bg-blue-500/10 text-blue-300 border-blue-500/30';
      case 'IMPLEMENTED_BY': return 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30';
      case 'REALIZED_BY': return 'bg-purple-500/10 text-purple-300 border-purple-500/30';
      case 'VERIFIED_BY': return 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
      case 'AFFECTS': return 'bg-rose-500/10 text-rose-300 border-rose-500/30';
      case 'RELATED_TO': return 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30';
      default: return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  // Extract layer counts
  const layerStats = useMemo(() => {
    const counts = { BRD: 0, SRS: 0, FRD: 0, USER_STORY: 0, TEST_CASE: 0, CHANGE_REQUEST: 0, MEETING_MINUTES: 0 };
    allArtifacts.forEach(a => {
      const t = (a.document_type || 'OTHER').toUpperCase().replace(' ', '_');
      if (counts[t] !== undefined) counts[t]++;
      else if (t === 'USER_STORIES') counts['USER_STORY']++;
      else if (t === 'TEST_CASES') counts['TEST_CASE']++;
      else if (t === 'CHANGE_REQUESTS') counts['CHANGE_REQUEST']++;
      else if (t === 'MEETING_MINS' || t === 'MOM') counts['MEETING_MINUTES']++;
    });
    return counts;
  }, [allArtifacts]);

  return (
    <div className="bg-[#0B0F19] min-h-screen py-6 text-slate-100 font-sans selection:bg-cyan-500/30">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 space-y-6">

        {/* ── TOP BAR / COMMAND HEADER ────────────────────────────────────────── */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 p-5 rounded-2xl bg-[#111827]/80 backdrop-blur-xl border border-slate-800/80 shadow-2xl">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="flex h-2.5 w-2.5 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-emerald-400">ENGINE ONLINE</span>
              <span className="text-slate-600">•</span>
              <span className="text-xs font-mono text-slate-400">{semanticModel}</span>
              <span className="text-slate-600">•</span>
              <span className="text-xs font-mono text-cyan-400 capitalize">{analysisMode.replace(/_/g, ' ')}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight flex items-center gap-3">
              ReqVision AI <span className="text-slate-600 font-light">|</span> <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400">Software Intelligence Command Center</span>
            </h1>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <button
              onClick={() => setIsCommandOpen(true)}
              className="flex items-center gap-3 px-4 py-2 rounded-xl bg-slate-900/90 border border-slate-700/60 hover:border-cyan-500/50 text-slate-300 text-xs font-mono transition-all shadow-inner hover:shadow-cyan-500/10 w-full md:w-auto justify-between md:justify-start cursor-pointer"
            >
              <span className="flex items-center gap-2"><Search className="w-3.5 h-3.5 text-cyan-400" /> Search Artifacts & Trace...</span>
              <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-[10px] text-slate-400">⌘K</kbd>
            </button>

            <button
              onClick={() => window.print()}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-xs shadow-lg shadow-cyan-600/20 transition-all cursor-pointer whitespace-nowrap"
            >
              <Download className="w-3.5 h-3.5" /> Export Intelligence PDF
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div 
            onClick={() => setActiveTab('overview')}
            className={`p-4 rounded-2xl border transition-all cursor-pointer ${activeTab === 'overview' ? 'bg-cyan-950/20 border-cyan-500/40 shadow-lg shadow-cyan-500/10' : 'bg-[#111827]/60 border-slate-800/80 hover:border-slate-700'}`}
          >
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1">
              <span className="flex items-center gap-1.5"><Shield className="w-3.5 h-3.5 text-cyan-400" /> HEALTH</span>
              <span className={`font-bold px-1.5 py-0.2 rounded text-[10px] ${healthScore.overall_score >= 80 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`}>
                {healthScore.grade}
              </span>
            </div>
            <div className="text-2xl font-black text-white">{healthScore.overall_score}<span className="text-xs text-slate-500 font-normal">/100</span></div>
            <div className="text-[10px] text-slate-500 font-mono mt-1">Multi-signal index</div>
          </div>

          <div 
            onClick={() => { setActiveTab('matrix'); setStatusFilter('All'); }}
            className="p-4 rounded-2xl bg-[#111827]/60 border border-slate-800/80 hover:border-slate-700 transition-all cursor-pointer"
          >
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1">
              <span className="flex items-center gap-1.5"><Layers className="w-3.5 h-3.5 text-blue-400" /> TRACEABILITY</span>
            </div>
            <div className="text-2xl font-black text-white">{summary.coverage_percentage || 0}<span className="text-xs text-slate-500 font-normal">%</span></div>
            <div className="text-[10px] text-slate-500 font-mono mt-1">{summary.total_relationships || matrix.length} canonical links</div>
          </div>

          <div 
            onClick={() => setActiveTab('quality')}
            className="p-4 rounded-2xl bg-[#111827]/60 border border-slate-800/80 hover:border-slate-700 transition-all cursor-pointer"
          >
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1">
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> VERIFIED</span>
            </div>
            <div className="text-2xl font-black text-emerald-400">{testIntelligence.verification_rate}</div>
            <div className="text-[10px] text-slate-500 font-mono mt-1">{testIntelligence.verified_stories_count}/{testIntelligence.total_stories_count} stories tested</div>
          </div>

          <div 
            onClick={() => { setActiveTab('overview'); }}
            className="p-4 rounded-2xl bg-[#111827]/60 border border-slate-800/80 hover:border-slate-700 transition-all cursor-pointer"
          >
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1">
              <span className="flex items-center gap-1.5"><ShieldAlert className="w-3.5 h-3.5 text-rose-400" /> RISKS & GAPS</span>
              {topConflicts.length > 0 && <span className="bg-rose-500/20 text-rose-400 px-1 rounded text-[10px] font-bold">!</span>}
            </div>
            <div className="text-2xl font-black text-rose-400">{riskRadar.length}</div>
            <div className="text-[10px] text-slate-500 font-mono mt-1">{topConflicts.length} conflicts, {topUnmapped.length} gaps</div>
          </div>

          <div 
            onClick={() => setActiveTab('impact')}
            className="p-4 rounded-2xl bg-[#111827]/60 border border-slate-800/80 hover:border-slate-700 transition-all cursor-pointer"
          >
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1">
              <span className="flex items-center gap-1.5"><GitPullRequest className="w-3.5 h-3.5 text-amber-400" /> CHANGE IMPACT</span>
            </div>
            <div className="text-2xl font-black text-amber-400">{changeImpactSummary.active_change_impacts}</div>
            <div className="text-[10px] text-slate-500 font-mono mt-1">{changeImpactSummary.total_change_requests} CRs analyzed</div>
          </div>

          <div 
            onClick={() => setActiveTab('graph')}
            className="p-4 rounded-2xl bg-[#111827]/60 border border-slate-800/80 hover:border-slate-700 transition-all cursor-pointer"
          >
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1">
              <span className="flex items-center gap-1.5"><Database className="w-3.5 h-3.5 text-purple-400" /> ARTIFACTS</span>
            </div>
            <div className="text-2xl font-black text-white">{summary.total_artifacts || allArtifacts.length}</div>
            <div className="text-[10px] text-slate-500 font-mono mt-1">across {documents.length} layers</div>
          </div>
        </div>

        <div className="flex items-center gap-2 border-b border-slate-800 pb-2 overflow-x-auto scrollbar-none">
          {[
            { id: 'overview', label: 'Intelligence Overview & Map', icon: Compass },
            { id: 'matrix', label: `Smart Matrix (${filteredMatrix.length})`, icon: BarChart3 },
            { id: 'graph', label: 'Knowledge Graph', icon: Network },
            { id: 'chains', label: `End-to-End Chains (${chains.length})`, icon: Link2 },
            { id: 'impact', label: `Change Impact (${changeImpactSummary.active_change_impacts})`, icon: GitPullRequest },
            { id: 'quality', label: `Test & Quality Center (${requirementQuality.length})`, icon: Cpu }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-xs sm:text-sm transition-all whitespace-nowrap cursor-pointer ${
                  isActive 
                    ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 shadow-sm' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="p-6 rounded-2xl bg-[#111827]/70 border border-slate-800/80 space-y-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <Compass className="w-4 h-4 text-cyan-400" /> Engineering Intelligence Architecture Map
                  </h2>
                  <p className="text-xs text-slate-400">Canonical cross-document traceability paths across system lifecycle tiers</p>
                </div>
                <span className="text-xs font-mono text-slate-500">Live Canonical Projection</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-7 gap-3 py-4">
                {[
                  { layer: 'BRD', label: 'Business Goals', count: layerStats.BRD, color: 'border-blue-500/40 bg-blue-950/20 text-blue-300' },
                  { layer: 'SRS', label: 'System Req.', count: layerStats.SRS, color: 'border-sky-500/40 bg-sky-950/20 text-sky-300' },
                  { layer: 'FRD', label: 'Capabilities', count: layerStats.FRD, color: 'border-cyan-500/40 bg-cyan-950/20 text-cyan-300' },
                  { layer: 'USER_STORY', label: 'User Stories', count: layerStats.USER_STORY, color: 'border-purple-500/40 bg-purple-950/20 text-purple-300' },
                  { layer: 'TEST_CASE', label: 'Test Suites', count: layerStats.TEST_CASE, color: 'border-emerald-500/40 bg-emerald-950/20 text-emerald-300' },
                  { layer: 'CHANGE_REQUEST', label: 'Change Delta', count: layerStats.CHANGE_REQUEST, color: 'border-amber-500/40 bg-amber-950/20 text-amber-300' },
                  { layer: 'MEETING_MINUTES', label: 'Decisions', count: layerStats.MEETING_MINUTES, color: 'border-indigo-500/40 bg-indigo-950/20 text-indigo-300' }
                ].map((tier) => (
                  <div key={tier.layer} className="relative group">
                    <div className={`p-3.5 rounded-xl border ${tier.color} space-y-1 transition-all group-hover:scale-[1.02]`}>
                      <div className="text-[10px] font-mono font-bold opacity-75">{tier.layer}</div>
                      <div className="text-xs font-bold text-white truncate">{tier.label}</div>
                      <div className="text-lg font-black text-white">{tier.count} <span className="text-[10px] text-slate-400 font-normal">items</span></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="p-6 rounded-2xl bg-[#111827]/70 border border-slate-800/80 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Shield className="w-4 h-4 text-cyan-400" /> Software Intelligence Health Score Formula
                  </h3>
                  <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-mono text-xs font-bold">
                    Score: {healthScore.overall_score}/100
                  </span>
                </div>
                <p className="text-xs text-slate-400 font-mono bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
                  Formula: {healthScore.formula}
                </p>
                <div className="space-y-2.5 pt-1">
                  {Object.entries(healthScore.breakdown || {}).map(([metricKey, mData]) => (
                    <div key={metricKey} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-300 font-medium capitalize">{metricKey.replace(/_/g, ' ')}</span>
                        <span className="text-slate-400 font-mono">{mData.score}% (Weight: {mData.weight})</span>
                      </div>
                      <div className="w-full bg-slate-800/80 rounded-full h-1.5">
                        <div 
                          className={`h-1.5 rounded-full ${mData.score >= 80 ? 'bg-emerald-500' : mData.score >= 60 ? 'bg-amber-500' : 'bg-rose-500'}`} 
                          style={{ width: `${Math.min(100, mData.score)}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-[#111827]/70 border border-slate-800/80 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-rose-400" /> Active Risk Radar
                  </h3>
                  <span className="text-xs font-mono text-slate-400">{riskRadar.length} items flagged</span>
                </div>
                {riskRadar.length === 0 ? (
                  <div className="p-8 text-center rounded-xl bg-slate-900/40 border border-slate-800/60 space-y-2">
                    <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
                    <div className="text-xs font-bold text-white">Zero High-Risk Gaps Detected</div>
                  </div>
                ) : (
                  <div className="space-y-2.5 max-h-[260px] overflow-y-auto pr-1">
                    {riskRadar.map((risk, idx) => (
                      <div 
                        key={idx}
                        onClick={() => openArtifactDrawer(risk.artifact_id)}
                        className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-rose-500/40 transition-all cursor-pointer space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${risk.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400' : 'bg-blue-500/20 text-blue-400'}`}>
                            {risk.severity} • {risk.category}
                          </span>
                          <span className="text-xs font-mono text-cyan-400">{risk.artifact_id}</span>
                        </div>
                        <div className="text-xs font-bold text-slate-200">{risk.title}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'matrix' && (
          <div className="space-y-4">
            <div className="p-4 rounded-2xl bg-[#111827]/70 border border-slate-800/80 flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
                <div className="relative w-full sm:w-72">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Filter by ID, text, action..."
                    className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-900 border border-slate-700/60 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
                <div className="flex items-center gap-1.5 bg-slate-900 p-1 rounded-xl border border-slate-800">
                  {['All', 'MATCHED', 'PARTIAL', 'CONFLICT', 'UNMAPPED'].map(st => (
                    <button
                      key={st}
                      onClick={() => setStatusFilter(st)}
                      className={`px-3 py-1 rounded-lg text-xs font-mono font-medium transition-all ${statusFilter === st ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400'}`}
                    >
                      {st}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="rounded-2xl bg-[#111827]/80 border border-slate-800/80 overflow-hidden shadow-2xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/90 text-slate-400 font-mono text-[11px] uppercase tracking-wider border-b border-slate-800">
                    <tr>
                      <th className="py-3.5 px-4">Source Artifact</th>
                      <th className="py-3.5 px-3">Relationship</th>
                      <th className="py-3.5 px-4">Target Artifact</th>
                      <th className="py-3.5 px-3">Status</th>
                      <th className="py-3.5 px-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-sans">
                    {filteredMatrix.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-900/50">
                        <td className="py-3 px-4">
                          <div className="font-mono font-bold text-cyan-400">{row.source_artifact}</div>
                          <div className="text-slate-300 text-[11px] truncate max-w-sm">{row.source_text}</div>
                        </td>
                        <td className="py-3 px-3">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border ${getRelBadge(row.relationship)}`}>{row.relationship}</span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="font-mono font-bold text-sky-400">{row.target_artifact}</div>
                          <div className="text-slate-400 text-[11px] truncate max-w-sm">{row.target_text}</div>
                        </td>
                        <td className="py-3 px-3">{getStatusBadge(row.status)}</td>
                        <td className="py-3 px-3 text-right">
                          <button onClick={() => toggleRowExpand(idx)} className="text-[11px] bg-slate-800 px-2 py-1 rounded">Explain</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        <AnimatePresence>
          {drawerArtifact && (
            <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm">
              <motion.div
                initial={{ x: '100%' }}
                animate={{ x: 0 }}
                exit={{ x: '100%' }}
                className="w-full max-w-lg bg-[#0F172A] border-l border-slate-800 p-6 overflow-y-auto space-y-6 shadow-2xl"
              >
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <h2 className="text-xl font-black text-white font-mono">{drawerArtifact.artifact_id}</h2>
                  <button onClick={() => setDrawerArtifact(null)}><X className="w-5 h-5" /></button>
                </div>
                <p className="text-slate-300 text-xs font-mono">{drawerArtifact.text}</p>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {isCommandOpen && (
            <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/70 backdrop-blur-sm p-4">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="w-full max-w-2xl bg-[#0F172A] border border-slate-700/80 rounded-2xl overflow-hidden shadow-2xl"
              >
                <div className="p-4 border-b border-slate-800">
                  <input autoFocus value={commandQuery} onChange={(e) => setCommandQuery(e.target.value)} className="w-full bg-transparent text-white focus:outline-none font-mono" placeholder="Search..." />
                </div>
                <div className="p-2 space-y-1">
                  {commandResults.map((art, idx) => (
                    <div key={idx} onClick={() => { openArtifactDrawer(art.artifact_id); setIsCommandOpen(false); }} className="p-2.5 rounded-xl hover:bg-slate-800 cursor-pointer flex justify-between">
                      <span className="font-mono text-cyan-400">{art.artifact_id}</span>
                      <span className="text-slate-400 truncate text-xs">{art.text}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
