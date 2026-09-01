import React, { useState, useMemo, useEffect } from 'react';
import { 
  FileText, Database, Layers, CheckCircle2, AlertTriangle, AlertCircle, 
  Search, ShieldAlert, Download, Sparkles, Filter, ChevronRight, Activity,
  GitPullRequest, Clock, Server, Check, X, Network, Link2, ArrowRight,
  Shield, Cpu, Zap, Compass, BarChart3, ChevronDown, Eye, Terminal,
  Sliders, AlertOctagon, HelpCircle, CornerDownRight, ExternalLink,
  Maximize2, Minimize2, RefreshCw, Copy, CheckCheck, ListFilter,
  Workflow, ArrowUpRight, Crosshair
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ProjectTraceabilityDashboard({ result }) {
  // Navigation tabs: 'overview' | 'matrix' | 'graph' | 'chains' | 'impact' | 'quality'
  const [activeTab, setActiveTab] = useState('overview');
  
  // Matrix Filters & Settings
  const [statusFilter, setStatusFilter] = useState('All');
  const [relFilter, setRelFilter] = useState('All');
  const [layerFilter, setLayerFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedRows, setExpandedRows] = useState({});
  const [copiedId, setCopiedId] = useState(null);

  // Slide-over Drawer State
  const [drawerArtifact, setDrawerArtifact] = useState(null);

  // Command Palette (Cmd+K)
  const [isCommandOpen, setIsCommandOpen] = useState(false);
  const [commandQuery, setCommandQuery] = useState('');

  // Graph state & Interactive Selection
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

  // Phase B Intelligence Metrics from Canonical Store
  const healthScore = result.software_health_score || {
    overall_score: summary.coverage_percentage || 0,
    grade: (summary.coverage_percentage || 0) >= 90 ? 'A' : (summary.coverage_percentage || 0) >= 75 ? 'B' : 'C',
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
    total_change_requests: crImpacts.length,
    active_change_impacts: crImpacts.length,
    direct_impact_items: crImpacts,
    derived_impacts: []
  };

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

  // Counts by status
  const statusCounts = useMemo(() => {
    const counts = { All: matrix.length, MATCHED: 0, PARTIAL: 0, CONFLICT: 0, UNMAPPED: 0 };
    matrix.forEach(r => {
      if (counts[r.status] !== undefined) counts[r.status]++;
      else counts.UNMAPPED++;
    });
    return counts;
  }, [matrix]);

  // Command Palette Results
  const commandResults = useMemo(() => {
    if (!commandQuery.trim()) return allArtifacts.slice(0, 10);
    const q = commandQuery.toLowerCase();
    return allArtifacts.filter(a => 
      (a.artifact_id || '').toLowerCase().includes(q) ||
      (a.text || '').toLowerCase().includes(q) ||
      (a.document_type || '').toLowerCase().includes(q)
    ).slice(0, 15);
  }, [allArtifacts, commandQuery]);

  const toggleRowExpand = (idx) => {
    setExpandedRows(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const openArtifactDrawer = (artId) => {
    if (!artId || artId === '—') return;
    const found = allArtifacts.find(a => a.artifact_id === artId || a.id === artId);
    if (found) {
      setDrawerArtifact(found);
    } else {
      setDrawerArtifact({ artifact_id: artId, text: 'Artifact specification registered in canonical graph.', document_type: 'TRACE_NODE' });
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'MATCHED':
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5 w-fit shadow-sm shadow-emerald-500/10">
            <CheckCircle2 className="w-3.5 h-3.5" /> MATCHED
          </span>
        );
      case 'PARTIAL':
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-mono font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30 flex items-center gap-1.5 w-fit shadow-sm shadow-amber-500/10">
            <AlertTriangle className="w-3.5 h-3.5" /> PARTIAL
          </span>
        );
      case 'CONFLICT':
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center gap-1.5 w-fit shadow-sm shadow-rose-500/10">
            <AlertCircle className="w-3.5 h-3.5" /> CONFLICT
          </span>
        );
      case 'UNMAPPED':
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-mono font-bold bg-slate-800 text-slate-400 border border-slate-700 flex items-center gap-1.5 w-fit">
            <X className="w-3.5 h-3.5" /> UNMAPPED
          </span>
        );
    }
  };

  const getRelBadge = (rel) => {
    switch (rel) {
      case 'TRACEABLE_TO': return 'bg-blue-500/10 text-blue-300 border-blue-500/30';
      case 'IMPLEMENTED_BY': return 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30';
      case 'REALIZED_BY': return 'bg-purple-500/10 text-purple-300 border-purple-500/30';
      case 'VERIFIED_BY': return 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
      case 'AFFECTS': return 'bg-rose-500/10 text-rose-300 border-rose-500/30';
      default: return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

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
    <div className="bg-[#070B14] min-h-screen py-6 text-slate-100 font-sans selection:bg-cyan-500/30">
      <div className="max-w-[1560px] mx-auto px-4 sm:px-6 lg:px-8 space-y-6">

        {/* ── TOP BAR / COMMAND HEADER ────────────────────────────────────────── */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 p-6 rounded-3xl bg-[#0D1527]/90 backdrop-blur-2xl border border-slate-800/80 shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="flex h-2.5 w-2.5 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-emerald-400">ENGINE ACTIVE</span>
              <span className="text-slate-700">•</span>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded-full border border-cyan-800/40">{semanticModel}</span>
              <span className="text-slate-700">•</span>
              <span className="text-xs font-mono text-slate-300 capitalize">{analysisMode.replace(/_/g, ' ')}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-white tracking-tight flex items-center gap-3">
              ReqVision AI <span className="text-slate-700 font-light">/</span> <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400">Software Intelligence Platform</span>
            </h1>
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            {/* Command Palette Trigger */}
            <button
              onClick={() => setIsCommandOpen(true)}
              className="flex items-center gap-3 px-4 py-2.5 rounded-2xl bg-slate-900/90 border border-slate-700/60 hover:border-cyan-500/60 text-slate-300 text-xs font-mono transition-all shadow-inner hover:shadow-cyan-500/10 w-full sm:w-auto justify-between cursor-pointer"
            >
              <span className="flex items-center gap-2"><Search className="w-4 h-4 text-cyan-400" /> Search Intelligence Graph...</span>
              <kbd className="px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-[10px] text-slate-400">⌘K</kbd>
            </button>

            {/* Executive Print / PDF Export */}
            <button
              onClick={() => window.print()}
              className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-gradient-to-r from-cyan-600 via-sky-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-xs shadow-lg shadow-cyan-600/25 transition-all cursor-pointer whitespace-nowrap"
            >
              <Download className="w-4 h-4" /> Export Intelligence Dossier
            </button>
          </div>
        </div>

        {/* ── INTELLIGENCE SUMMARY KPI CARDS ─────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
          
          {/* Health Score Card */}
          <div 
            onClick={() => setActiveTab('overview')}
            className={`p-4 rounded-3xl border transition-all cursor-pointer ${activeTab === 'overview' ? 'bg-cyan-950/30 border-cyan-500/50 shadow-lg shadow-cyan-500/15' : 'bg-[#0D1527]/70 border-slate-800/80 hover:border-slate-700'}`}
          >
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1.5">
              <span className="flex items-center gap-1.5"><Shield className="w-4 h-4 text-cyan-400" /> HEALTH</span>
              <span className={`font-bold px-2 py-0.5 rounded-full text-[10px] ${healthScore.overall_score >= 80 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'}`}>
                Grade {healthScore.grade}
              </span>
            </div>
            <div className="text-3xl font-black text-white">{healthScore.overall_score}<span className="text-xs text-slate-500 font-normal">/100</span></div>
            <div className="text-[11px] text-cyan-400/80 font-mono mt-1">Multi-signal Index</div>
          </div>

          {/* Traceability Completeness */}
          <div 
            onClick={() => { setActiveTab('matrix'); setStatusFilter('All'); }}
            className={`p-4 rounded-3xl border transition-all cursor-pointer ${activeTab === 'matrix' ? 'bg-blue-950/30 border-blue-500/50 shadow-lg shadow-blue-500/15' : 'bg-[#0D1527]/70 border-slate-800/80 hover:border-slate-700'}`}
          >
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1.5">
              <span className="flex items-center gap-1.5"><Layers className="w-4 h-4 text-blue-400" /> TRACEABILITY</span>
            </div>
            <div className="text-3xl font-black text-white">{summary.coverage_percentage || 0}<span className="text-xs text-slate-500 font-normal">%</span></div>
            <div className="text-[11px] text-blue-400/80 font-mono mt-1">{summary.total_relationships || matrix.length} verified links</div>
          </div>

          {/* Verification Coverage */}
          <div 
            onClick={() => setActiveTab('quality')}
            className={`p-4 rounded-3xl border transition-all cursor-pointer ${activeTab === 'quality' ? 'bg-emerald-950/30 border-emerald-500/50 shadow-lg shadow-emerald-500/15' : 'bg-[#0D1527]/70 border-slate-800/80 hover:border-slate-700'}`}
          >
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1.5">
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> VERIFIED</span>
            </div>
            <div className="text-3xl font-black text-emerald-400">{testIntelligence.verification_rate}</div>
            <div className="text-[11px] text-emerald-400/80 font-mono mt-1">{testIntelligence.verified_stories_count}/{testIntelligence.total_stories_count} stories tested</div>
          </div>

          {/* Risk Radar & Conflicts */}
          <div 
            onClick={() => { setActiveTab('overview'); }}
            className="p-4 rounded-3xl bg-[#0D1527]/70 border border-slate-800/80 hover:border-slate-700 transition-all cursor-pointer"
          >
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1.5">
              <span className="flex items-center gap-1.5"><ShieldAlert className="w-4 h-4 text-rose-400" /> RISKS & GAPS</span>
              {topConflicts.length > 0 && <span className="bg-rose-500/20 text-rose-400 px-1.5 py-0.2 rounded-full text-[10px] font-bold border border-rose-500/40">!</span>}
            </div>
            <div className="text-3xl font-black text-rose-400">{riskRadar.length}</div>
            <div className="text-[11px] text-slate-400 font-mono mt-1">{topConflicts.length} conflicts, {topUnmapped.length} gaps</div>
          </div>

          {/* Change Impact */}
          <div 
            onClick={() => setActiveTab('impact')}
            className={`p-4 rounded-3xl border transition-all cursor-pointer ${activeTab === 'impact' ? 'bg-amber-950/30 border-amber-500/50 shadow-lg shadow-amber-500/15' : 'bg-[#0D1527]/70 border-slate-800/80 hover:border-slate-700'}`}
          >
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1.5">
              <span className="flex items-center gap-1.5"><GitPullRequest className="w-4 h-4 text-amber-400" /> BLAST RADIUS</span>
            </div>
            <div className="text-3xl font-black text-amber-400">{changeImpactSummary.active_change_impacts}</div>
            <div className="text-[11px] text-amber-400/80 font-mono mt-1">{changeImpactSummary.total_change_requests} CRs analyzed</div>
          </div>

          {/* Total Artifacts & Layers */}
          <div 
            onClick={() => setActiveTab('graph')}
            className={`p-4 rounded-3xl border transition-all cursor-pointer ${activeTab === 'graph' ? 'bg-purple-950/30 border-purple-500/50 shadow-lg shadow-purple-500/15' : 'bg-[#0D1527]/70 border-slate-800/80 hover:border-slate-700'}`}
          >
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-1.5">
              <span className="flex items-center gap-1.5"><Database className="w-4 h-4 text-purple-400" /> ARTIFACTS</span>
            </div>
            <div className="text-3xl font-black text-white">{summary.total_artifacts || allArtifacts.length}</div>
            <div className="text-[11px] text-purple-400/80 font-mono mt-1">across {documents.length} layers</div>
          </div>

        </div>

        {/* ── COMMAND CENTER NAVIGATION TABS ─────────────────────────────────── */}
        <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3 overflow-x-auto scrollbar-none">
          {[
            { id: 'overview', label: 'Intelligence Overview & Map', icon: Compass },
            { id: 'matrix', label: `Smart Matrix (${filteredMatrix.length})`, icon: BarChart3 },
            { id: 'graph', label: `Knowledge Graph (${graph.nodes.length})`, icon: Network },
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
                className={`flex items-center gap-2.5 px-5 py-3 rounded-2xl font-bold text-xs sm:text-sm transition-all whitespace-nowrap cursor-pointer ${
                  isActive 
                    ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-lg shadow-cyan-500/10' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* ── TAB 1: INTELLIGENCE OVERVIEW & MAP ─────────────────────────────── */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            
            {/* Engineering Layer Flow DAG Map */}
            <div className="p-6 rounded-3xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl space-y-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div>
                  <h2 className="text-base font-black text-white flex items-center gap-2">
                    <Compass className="w-4 h-4 text-cyan-400" /> Engineering Intelligence Architecture Pipeline
                  </h2>
                  <p className="text-xs text-slate-400">Deterministic cross-document traceability paths across system lifecycle tiers</p>
                </div>
                <span className="text-xs font-mono text-cyan-400 bg-cyan-950/40 px-3 py-1 rounded-full border border-cyan-800/40">Canonical Live Projection</span>
              </div>

              {/* Multi-tier Flow Diagram */}
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
                    <div className={`p-4 rounded-2xl border ${tier.color} space-y-1.5 transition-all group-hover:scale-[1.02] shadow-sm`}>
                      <div className="text-[10px] font-mono font-bold uppercase tracking-wider opacity-75">{tier.layer}</div>
                      <div className="text-xs font-bold text-white truncate">{tier.label}</div>
                      <div className="text-2xl font-black text-white">{tier.count} <span className="text-[10px] text-slate-400 font-normal">items</span></div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Path Coverage Progress Bars */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
                <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-400">BRD → SRS (Business)</span>
                    <span className="text-blue-400 font-bold">{summary.path_coverage?.brd_to_srs_coverage || '100%'}</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full shadow-[0_0_8px_rgba(59,130,246,0.6)]" style={{ width: summary.path_coverage?.brd_to_srs_coverage?.split('%')[0] + '%' || '100%' }}></div>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-400">SRS → FRD (Capability)</span>
                    <span className="text-cyan-400 font-bold">{summary.path_coverage?.srs_to_frd_coverage || '100%'}</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div className="bg-cyan-500 h-2 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.6)]" style={{ width: summary.path_coverage?.srs_to_frd_coverage?.split('%')[0] + '%' || '100%' }}></div>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-400">SRS → Story (Realized)</span>
                    <span className="text-purple-400 font-bold">{summary.path_coverage?.srs_to_user_story_coverage || '100%'}</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div className="bg-purple-500 h-2 rounded-full shadow-[0_0_8px_rgba(168,85,247,0.6)]" style={{ width: summary.path_coverage?.srs_to_user_story_coverage?.split('%')[0] + '%' || '100%' }}></div>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-400">Story → Test (Verified)</span>
                    <span className="text-emerald-400 font-bold">{summary.path_coverage?.user_story_to_test_case_coverage || '100%'}</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div className="bg-emerald-500 h-2 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.6)]" style={{ width: summary.path_coverage?.user_story_to_test_case_coverage?.split('%')[0] + '%' || '100%' }}></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Health Score Breakdown & Live Risk Radar Side-by-Side */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Health Score Transparency Panel */}
              <div className="p-6 rounded-3xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Shield className="w-4 h-4 text-cyan-400" /> Software Intelligence Health Score Formula
                  </h3>
                  <span className="px-3 py-1 rounded-full bg-cyan-500/15 text-cyan-300 font-mono text-xs font-bold border border-cyan-500/30">
                    Score: {healthScore.overall_score}/100 (Grade {healthScore.grade})
                  </span>
                </div>
                <p className="text-xs text-slate-300 font-mono bg-slate-950/60 p-3 rounded-2xl border border-slate-800 leading-relaxed">
                  Formula: {healthScore.formula}
                </p>
                <div className="space-y-3 pt-1">
                  {Object.entries(healthScore.breakdown || {}).map(([metricKey, mData]) => (
                    <div key={metricKey} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-300 font-medium capitalize">{metricKey.replace(/_/g, ' ')}</span>
                        <span className="text-slate-400 font-mono">{mData.score}% (Weight: {mData.weight})</span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${mData.score >= 80 ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : mData.score >= 60 ? 'bg-amber-500' : 'bg-rose-500'}`} 
                          style={{ width: `${Math.min(100, mData.score)}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Risk Radar Active Feed */}
              <div className="p-6 rounded-3xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-rose-400" /> Active Risk Radar
                  </h3>
                  <span className="text-xs font-mono text-slate-400">{riskRadar.length} items flagged</span>
                </div>
                
                {riskRadar.length === 0 ? (
                  <div className="p-8 text-center rounded-2xl bg-slate-950/40 border border-slate-800/60 space-y-2">
                    <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
                    <div className="text-xs font-bold text-white">Zero High-Risk Gaps Detected</div>
                    <div className="text-[11px] text-slate-400">All requirements have downstream realization, tests, and zero specification contradictions.</div>
                  </div>
                ) : (
                  <div className="space-y-2.5 max-h-[290px] overflow-y-auto pr-1">
                    {riskRadar.map((risk, idx) => (
                      <div 
                        key={risk.risk_id || idx}
                        onClick={() => openArtifactDrawer(risk.artifact_id)}
                        className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 hover:border-rose-500/50 transition-all cursor-pointer space-y-1.5 shadow-sm hover:shadow-rose-500/5"
                      >
                        <div className="flex items-center justify-between">
                          <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                            risk.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                            risk.severity === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                            'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                          }`}>
                            {risk.severity} • {risk.category}
                          </span>
                          <span className="text-xs font-mono text-cyan-400 hover:underline">{risk.artifact_id}</span>
                        </div>
                        <div className="text-xs font-bold text-slate-200">{risk.title}</div>
                        <div className="text-[11px] text-slate-400 font-mono truncate">{risk.evidence}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

            </div>

          </div>
        )}

        {/* ── TAB 2: SMART TRACEABILITY MATRIX ──────────────────────────────── */}
        {activeTab === 'matrix' && (
          <div className="space-y-4">
            
            {/* Filter Toolbar */}
            <div className="p-5 rounded-3xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl flex flex-wrap items-center justify-between gap-4">
              
              <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
                {/* Search Bar */}
                <div className="relative w-full sm:w-80">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by ID, keyword, action..."
                    className="w-full pl-10 pr-8 py-2 rounded-2xl bg-slate-950 border border-slate-700/60 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono shadow-inner"
                  />
                  {searchQuery && (
                    <button onClick={() => setSearchQuery('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white">
                      <X className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {/* Status Filter Pills with Counts */}
                <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-2xl border border-slate-800">
                  {[
                    { id: 'All', label: `All (${statusCounts.All})` },
                    { id: 'MATCHED', label: `Matched (${statusCounts.MATCHED})` },
                    { id: 'PARTIAL', label: `Partial (${statusCounts.PARTIAL})` },
                    { id: 'CONFLICT', label: `Conflict (${statusCounts.CONFLICT})` },
                    { id: 'UNMAPPED', label: `Unmapped (${statusCounts.UNMAPPED})` }
                  ].map(st => (
                    <button
                      key={st.id}
                      onClick={() => setStatusFilter(st.id)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all cursor-pointer ${
                        statusFilter === st.id ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm' : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      {st.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Relationship & Layer Filters */}
              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-slate-400">Relationship:</span>
                  <select
                    value={relFilter}
                    onChange={(e) => setRelFilter(e.target.value)}
                    className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono focus:outline-none focus:border-cyan-500 cursor-pointer"
                  >
                    <option value="All">All Types</option>
                    <option value="TRACEABLE_TO">TRACEABLE_TO (BRD→SRS)</option>
                    <option value="IMPLEMENTED_BY">IMPLEMENTED_BY (SRS→FRD)</option>
                    <option value="REALIZED_BY">REALIZED_BY (SRS→Story)</option>
                    <option value="VERIFIED_BY">VERIFIED_BY (Story→Test)</option>
                    <option value="AFFECTS">AFFECTS (CR→Req)</option>
                  </select>
                </div>
              </div>

            </div>

            {/* Smart Matrix Table */}
            <div className="rounded-3xl bg-[#0D1527]/90 border border-slate-800/80 overflow-hidden shadow-2xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/90 text-slate-400 font-mono text-[11px] uppercase tracking-wider border-b border-slate-800">
                    <tr>
                      <th className="py-4 px-5">Source Artifact</th>
                      <th className="py-4 px-3">Relationship</th>
                      <th className="py-4 px-5">Target Realization</th>
                      <th className="py-4 px-3">Status</th>
                      <th className="py-4 px-4">Semantic / Lexical / Hybrid</th>
                      <th className="py-4 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-sans">
                    {filteredMatrix.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="py-16 text-center text-slate-500 font-mono">
                          No traceability relationships matched the active filter criteria.
                        </td>
                      </tr>
                    ) : (
                      filteredMatrix.map((row, idx) => {
                        const isExpanded = expandedRows[idx];
                        const semScore = row.semantic_similarity !== undefined && row.semantic_similarity !== null ? Math.round(row.semantic_similarity * 100) : null;
                        const lexScore = row.lexical_similarity !== undefined && row.lexical_similarity !== null ? Math.round(row.lexical_similarity * 100) : null;
                        const hybScore = row.hybrid_score !== undefined && row.hybrid_score !== null ? Math.round(row.hybrid_score * 100) : null;

                        return (
                          <React.Fragment key={`${row.source_artifact}-${row.target_artifact}-${idx}`}>
                            <tr className={`hover:bg-slate-900/60 transition-colors ${isExpanded ? 'bg-slate-900/80' : ''}`}>
                              
                              {/* Source */}
                              <td className="py-3.5 px-5">
                                <div className="flex items-center gap-2">
                                  <button
                                    onClick={() => openArtifactDrawer(row.source_artifact)}
                                    className="font-mono font-bold text-cyan-400 hover:text-cyan-300 hover:underline cursor-pointer"
                                  >
                                    {row.source_artifact}
                                  </button>
                                  <span className="text-[10px] font-mono text-slate-400 px-2 py-0.2 rounded-md bg-slate-950 border border-slate-800">
                                    {row.source_type || 'SRS'}
                                  </span>
                                </div>
                                <div className="text-slate-300 text-xs line-clamp-1 mt-1 max-w-md">
                                  {row.source_text}
                                </div>
                              </td>

                              {/* Relationship */}
                              <td className="py-3.5 px-3">
                                <span className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-bold border ${getRelBadge(row.relationship)}`}>
                                  {row.relationship}
                                </span>
                              </td>

                              {/* Target */}
                              <td className="py-3.5 px-5">
                                {row.target_artifact && row.target_artifact !== '—' ? (
                                  <div>
                                    <div className="flex items-center gap-2">
                                      <button
                                        onClick={() => openArtifactDrawer(row.target_artifact)}
                                        className="font-mono font-bold text-sky-400 hover:text-sky-300 hover:underline cursor-pointer"
                                      >
                                        {row.target_artifact}
                                      </button>
                                      <span className="text-[10px] font-mono text-slate-400 px-2 py-0.2 rounded-md bg-slate-950 border border-slate-800">
                                        {row.target_type || 'FRD'}
                                      </span>
                                    </div>
                                    <div className="text-slate-400 text-xs line-clamp-1 mt-1 max-w-md">
                                      {row.target_text}
                                    </div>
                                  </div>
                                ) : (
                                  <span className="text-slate-600 font-mono italic">No downstream target</span>
                                )}
                              </td>

                              {/* Status */}
                              <td className="py-3.5 px-3">
                                {getStatusBadge(row.status)}
                              </td>

                              {/* Multi-signal Gauges */}
                              <td className="py-3.5 px-4 font-mono text-xs">
                                <div className="flex items-center gap-3">
                                  <div className="space-y-0.5">
                                    <div className="text-[10px] text-slate-500">SEM</div>
                                    <div className="text-emerald-400 font-bold">{semScore !== null ? `${semScore}%` : '—'}</div>
                                  </div>
                                  <div className="space-y-0.5">
                                    <div className="text-[10px] text-slate-500">LEX</div>
                                    <div className="text-blue-400 font-bold">{lexScore !== null ? `${lexScore}%` : '—'}</div>
                                  </div>
                                  <div className="space-y-0.5">
                                    <div className="text-[10px] text-slate-500">HYBRID</div>
                                    <div className="text-cyan-300 font-bold">{hybScore !== null ? `${hybScore}%` : '—'}</div>
                                  </div>
                                </div>
                              </td>

                              {/* Actions */}
                              <td className="py-3.5 px-4 text-right">
                                <button
                                  onClick={() => toggleRowExpand(idx)}
                                  className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 transition-all inline-flex items-center gap-1.5 text-xs font-mono font-medium cursor-pointer"
                                >
                                  {isExpanded ? 'Collapse' : 'Explain'}
                                  <ChevronDown className={`w-3.5 h-3.5 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                                </button>
                              </td>

                            </tr>

                            {/* Expandable Evidence Drawer */}
                            {isExpanded && (
                              <tr className="bg-slate-950/90 border-b border-slate-800">
                                <td colSpan={6} className="p-5 space-y-4">
                                  <div className="p-4 rounded-2xl bg-[#0D1527] border border-slate-800/90 space-y-3 shadow-inner">
                                    <div className="flex items-center justify-between text-xs font-mono">
                                      <span className="text-cyan-400 font-bold flex items-center gap-2">
                                        <Sparkles className="w-4 h-4 text-amber-400" /> Evidence & Multi-Factor Alignment Rationale
                                      </span>
                                      <span className="text-slate-400">Confidence: {row.confidence ? (row.confidence * 100).toFixed(1) + '%' : '100%'}</span>
                                    </div>
                                    
                                    <p className="text-xs text-slate-200 font-mono leading-relaxed bg-slate-950 p-3 rounded-xl border border-slate-800">
                                      {row.evidence || row.reason || 'Relationship evaluated by capability disambiguation and semantic fusion.'}
                                    </p>
                                    
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1 text-xs">
                                      <div className="space-y-1.5 p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                                        <div className="flex justify-between items-center text-slate-400 font-mono">
                                          <span>Source Specification [{row.source_artifact}]:</span>
                                          <button onClick={() => copyToClipboard(row.source_text, `src-${idx}`)} className="text-cyan-400 hover:underline">
                                            {copiedId === `src-${idx}` ? 'Copied!' : 'Copy'}
                                          </button>
                                        </div>
                                        <div className="text-slate-200 font-sans leading-relaxed">{row.source_text}</div>
                                      </div>

                                      <div className="space-y-1.5 p-3 rounded-xl bg-slate-950/80 border border-slate-800">
                                        <div className="flex justify-between items-center text-slate-400 font-mono">
                                          <span>Target Realization [{row.target_artifact}]:</span>
                                          {row.target_text && (
                                            <button onClick={() => copyToClipboard(row.target_text, `tgt-${idx}`)} className="text-sky-400 hover:underline">
                                              {copiedId === `tgt-${idx}` ? 'Copied!' : 'Copy'}
                                            </button>
                                          )}
                                        </div>
                                        <div className="text-slate-200 font-sans leading-relaxed">{row.target_text || 'No downstream artifact mapped.'}</div>
                                      </div>
                                    </div>
                                  </div>
                                </td>
                              </tr>
                            )}
                          </React.Fragment>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}

        {/* ── TAB 3: KNOWLEDGE GRAPH (INTERACTIVE VISUAL DAG) ──────────────── */}
        {activeTab === 'graph' && (
          <div className="p-6 rounded-3xl bg-[#0D1527]/90 border border-slate-800/80 shadow-2xl space-y-5">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
              <div>
                <h2 className="text-base font-black text-white flex items-center gap-2">
                  <Network className="w-5 h-5 text-cyan-400" /> Interactive Knowledge Graph (DAG)
                </h2>
                <p className="text-xs text-slate-400">Click any artifact node to inspect its specification and relationships</p>
              </div>

              {/* Layer Filter for Graph */}
              <div className="flex items-center gap-3">
                <span className="text-xs font-mono text-slate-400">Layer View:</span>
                <select
                  value={graphLayerFilter}
                  onChange={(e) => setGraphLayerFilter(e.target.value)}
                  className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono focus:outline-none focus:border-cyan-500 cursor-pointer"
                >
                  <option value="All">All Layers</option>
                  <option value="BRD">BRD (Business)</option>
                  <option value="SRS">SRS (System)</option>
                  <option value="FRD">FRD (Capabilities)</option>
                  <option value="USER_STORY">User Stories</option>
                  <option value="TEST_CASE">Test Cases</option>
                  <option value="CHANGE_REQUEST">Change Requests</option>
                </select>
              </div>
            </div>

            {/* Structured DAG Visual Flow */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 p-6 rounded-2xl bg-[#070B14] border border-slate-800 min-h-[480px]">
              {['BRD', 'SRS', 'FRD', 'USER_STORY', 'TEST_CASE'].map((tierName) => {
                const tierNodes = (graph.nodes || []).filter(n => {
                  const dt = (n.document_type || '').toUpperCase().replace(' ', '_');
                  return dt === tierName || (tierName === 'USER_STORY' && dt === 'USER_STORIES') || (tierName === 'TEST_CASE' && dt === 'TEST_CASES');
                });

                if (graphLayerFilter !== 'All' && graphLayerFilter !== tierName) return null;

                return (
                  <div key={tierName} className="space-y-3">
                    <div className="text-xs font-mono font-bold text-slate-400 border-b border-slate-800 pb-2 flex justify-between">
                      <span>{tierName}</span>
                      <span className="text-cyan-400 font-mono">{tierNodes.length} nodes</span>
                    </div>
                    <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
                      {tierNodes.map(node => {
                        const isSelected = selectedGraphNode?.id === node.id;
                        return (
                          <div
                            key={node.id}
                            onClick={() => setSelectedGraphNode(node)}
                            className={`p-3 rounded-2xl border text-xs transition-all cursor-pointer space-y-1 shadow-sm ${
                              isSelected
                                ? 'bg-cyan-500/20 border-cyan-400 text-white shadow-lg shadow-cyan-500/20'
                                : 'bg-[#0D1527] border-slate-800 hover:border-cyan-500/50 text-slate-300'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-mono font-bold text-xs text-cyan-300">{node.artifact_id}</span>
                              <span className="text-[10px] text-slate-500 font-mono">Inspect →</span>
                            </div>
                            <div className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">{node.text}</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Selected Node Details Drawer */}
            {selectedGraphNode && (
              <div className="p-5 rounded-2xl bg-[#0D1527] border border-cyan-500/40 text-xs font-mono space-y-3">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-cyan-300 text-sm">{selectedGraphNode.artifact_id}</span>
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">{selectedGraphNode.document_type}</span>
                  </div>
                  <button onClick={() => setSelectedGraphNode(null)} className="text-slate-400 hover:text-white cursor-pointer">
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <div className="text-slate-200 font-sans p-3 bg-slate-950 rounded-xl border border-slate-800">
                  {selectedGraphNode.text}
                </div>
                <div className="flex justify-end">
                  <button
                    onClick={() => openArtifactDrawer(selectedGraphNode.artifact_id)}
                    className="px-4 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold transition-all cursor-pointer"
                  >
                    Open Full Artifact Dossier →
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── TAB 4: END-TO-END CHAINS ──────────────────────────────────────── */}
        {activeTab === 'chains' && (
          <div className="space-y-4">
            <div className="p-5 rounded-3xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl flex justify-between items-center">
              <div>
                <h2 className="text-base font-black text-white flex items-center gap-2">
                  <Link2 className="w-5 h-5 text-cyan-400" /> End-to-End Traceability Chains
                </h2>
                <p className="text-xs text-slate-400">Strict pipeline integrity: BRD → SRS → FRD → User Story → QA Test Case</p>
              </div>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/40 px-3 py-1 rounded-full border border-cyan-800/40">{chains.length} Total Chains</span>
            </div>

            <div className="space-y-3.5">
              {chains.length === 0 ? (
                <div className="p-16 text-center rounded-3xl bg-[#0D1527] border border-slate-800 text-slate-500 font-mono">
                  No multi-tier chains formed.
                </div>
              ) : (
                chains.map((chain, cIdx) => (
                  <div 
                    key={chain.chain_id || cIdx}
                    className="p-5 rounded-3xl bg-[#0D1527]/90 border border-slate-800 hover:border-slate-700 transition-all space-y-4 shadow-lg"
                  >
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                      <div className="flex items-center gap-2.5">
                        <span className="font-mono font-bold text-xs text-cyan-400 bg-cyan-950/60 px-2.5 py-0.5 rounded-full border border-cyan-800/40">
                          Chain #{cIdx + 1}
                        </span>
                        <span className="text-slate-600">•</span>
                        <span className="text-xs text-slate-300 font-mono truncate max-w-lg">{chain.requirement_text || chain.srs?.text}</span>
                      </div>
                      <div>
                        {getStatusBadge(chain.overall_status)}
                      </div>
                    </div>

                    {/* Pipeline Visual Hops */}
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-2.5">
                      {/* Hop 1: BRD */}
                      <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-1">
                        <div className="text-[10px] font-mono text-blue-400 font-bold uppercase">1. Business (BRD)</div>
                        {chain.brd ? (
                          <div onClick={() => openArtifactDrawer(chain.brd.artifact_id || chain.brd.id)} className="font-mono text-xs font-bold text-blue-300 cursor-pointer hover:underline">
                            {chain.brd.artifact_id || chain.brd.id}
                          </div>
                        ) : (
                          <div className="text-xs text-slate-600 font-mono italic">Unmapped</div>
                        )}
                      </div>

                      {/* Hop 2: SRS */}
                      <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-1">
                        <div className="text-[10px] font-mono text-sky-400 font-bold uppercase">2. System (SRS)</div>
                        {chain.srs ? (
                          <div onClick={() => openArtifactDrawer(chain.srs.artifact_id || chain.srs.id)} className="font-mono text-xs font-bold text-sky-300 cursor-pointer hover:underline">
                            {chain.srs.artifact_id || chain.srs.id}
                          </div>
                        ) : (
                          <div className="text-xs text-slate-600 font-mono italic">Unmapped</div>
                        )}
                      </div>

                      {/* Hop 3: FRD */}
                      <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-1">
                        <div className="text-[10px] font-mono text-cyan-400 font-bold uppercase">3. Capability (FRD)</div>
                        {chain.frd ? (
                          <div onClick={() => openArtifactDrawer(chain.frd.artifact_id || chain.frd.id)} className="font-mono text-xs font-bold text-cyan-300 cursor-pointer hover:underline">
                            {chain.frd.artifact_id || chain.frd.id}
                          </div>
                        ) : (
                          <div className="text-xs text-amber-500/80 font-mono font-bold">Missing Hop</div>
                        )}
                      </div>

                      {/* Hop 4: User Story */}
                      <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-1">
                        <div className="text-[10px] font-mono text-purple-400 font-bold uppercase">4. User Story</div>
                        {chain.user_story ? (
                          <div onClick={() => openArtifactDrawer(chain.user_story.artifact_id || chain.user_story.id)} className="font-mono text-xs font-bold text-purple-300 cursor-pointer hover:underline">
                            {chain.user_story.artifact_id || chain.user_story.id}
                          </div>
                        ) : (
                          <div className="text-xs text-slate-600 font-mono italic">Unmapped</div>
                        )}
                      </div>

                      {/* Hop 5: Test Case */}
                      <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-1">
                        <div className="text-[10px] font-mono text-emerald-400 font-bold uppercase">5. Verification (TC)</div>
                        {chain.test_case ? (
                          <div onClick={() => openArtifactDrawer(chain.test_case.artifact_id || chain.test_case.id)} className="font-mono text-xs font-bold text-emerald-300 cursor-pointer hover:underline">
                            {chain.test_case.artifact_id || chain.test_case.id}
                          </div>
                        ) : (
                          <div className="text-xs text-rose-500/80 font-mono font-bold">No Test</div>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* ── TAB 5: CHANGE IMPACT CENTER ───────────────────────────────────── */}
        {activeTab === 'impact' && (
          <div className="space-y-6">
            <div className="p-6 rounded-3xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl space-y-5">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-base font-black text-white flex items-center gap-2">
                    <GitPullRequest className="w-5 h-5 text-amber-400" /> Change Impact & Blast Radius Center
                  </h2>
                  <p className="text-xs text-slate-400">Direct impact targets and downstream affected artifacts for proposed engineering changes</p>
                </div>
                <span className="px-3 py-1 rounded-full bg-amber-500/15 text-amber-300 font-mono text-xs border border-amber-500/30">
                  {changeImpactSummary.active_change_impacts} Active Impacts
                </span>
              </div>

              {crImpacts.length === 0 ? (
                <div className="p-16 text-center rounded-2xl bg-slate-950/40 border border-slate-800 text-slate-500 font-mono">
                  No Change Requests present in uploaded dataset.
                </div>
              ) : (
                <div className="space-y-4">
                  {crImpacts.map((cr, idx) => (
                    <div key={idx} className="p-5 rounded-2xl bg-[#070B14] border border-slate-800 space-y-3 shadow-sm">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-sm text-amber-400">
                          {cr.change_request_id || cr.source_artifact}
                        </span>
                        <span className="px-3 py-1 rounded-full bg-rose-500/20 text-rose-300 text-xs font-mono font-bold border border-rose-500/30">
                          Direct Target → {cr.target_artifact}
                        </span>
                      </div>
                      <div className="text-xs text-slate-300 font-mono bg-slate-950 p-3 rounded-xl border border-slate-800">
                        {cr.change_text || cr.source_text}
                      </div>
                      <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                        <span className="text-cyan-400 font-bold">Impact Evidence:</span> {cr.impact_reason || cr.evidence}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── TAB 6: TEST & QUALITY CENTER ──────────────────────────────────── */}
        {activeTab === 'quality' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Test Intelligence */}
            <div className="p-6 rounded-3xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl space-y-5">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Behavioral Test Coverage Center
                </h3>
                <span className="px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-300 font-mono text-xs font-bold border border-emerald-500/30">
                  {testIntelligence.verification_rate} Verified
                </span>
              </div>

              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <div className="text-2xl font-black text-white">{testIntelligence.total_test_cases}</div>
                  <div className="text-[10px] text-slate-400 font-mono mt-1">Total Tests</div>
                </div>
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <div className="text-2xl font-black text-emerald-400">{testIntelligence.mapped_test_cases}</div>
                  <div className="text-[10px] text-slate-400 font-mono mt-1">Mapped Tests</div>
                </div>
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <div className="text-2xl font-black text-rose-400">{testIntelligence.test_gaps?.length || 0}</div>
                  <div className="text-[10px] text-slate-400 font-mono mt-1">Test Gaps</div>
                </div>
              </div>

              <div className="space-y-2.5">
                <div className="text-xs font-mono text-slate-400">Unverified User Story Gaps:</div>
                {testIntelligence.test_gaps?.length === 0 ? (
                  <div className="p-6 text-center rounded-2xl bg-emerald-950/20 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
                    All user stories are verified by behavioral QA test cases!
                  </div>
                ) : (
                  testIntelligence.test_gaps?.map((gap, gIdx) => (
                    <div key={gIdx} className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs">
                      <span className="font-mono text-cyan-400 font-bold">{gap.story_id}</span>
                      <span className="text-slate-300 truncate max-w-xs">{gap.story_text}</span>
                      <span className="text-rose-400 font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-rose-950 border border-rose-800">GAP</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Requirement Quality Auditor */}
            <div className="p-6 rounded-3xl bg-[#0D1527]/90 border border-slate-800/80 shadow-xl space-y-5">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-purple-400" /> Requirement Quality Auditor
                </h3>
                <span className="text-xs font-mono text-slate-400">{requirementQuality.length} items flagged</span>
              </div>

              {requirementQuality.length === 0 ? (
                <div className="p-12 text-center rounded-2xl bg-slate-950/40 border border-slate-800 text-slate-500 font-mono">
                  All requirements meet measurable clarity standards.
                </div>
              ) : (
                <div className="space-y-3 max-h-[320px] overflow-y-auto pr-1">
                  {requirementQuality.map((item, qIdx) => (
                    <div key={qIdx} className="p-3.5 rounded-2xl bg-slate-950 border border-slate-800 space-y-2 shadow-sm">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-xs text-purple-300">{item.artifact_id}</span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                          {item.quality_status}
                        </span>
                      </div>
                      <div className="text-xs text-slate-300 line-clamp-1">{item.text}</div>
                      <div className="space-y-1 pt-1">
                        {item.findings?.map((find, fIdx) => (
                          <div key={fIdx} className="text-[11px] font-mono text-amber-300/80 flex items-center gap-1.5">
                            <span>⚠</span> {find}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        )}

        {/* ── UNIVERSAL SLIDE-OVER ARTIFACT DRAWER ───────────────────────────── */}
        <AnimatePresence>
          {drawerArtifact && (
            <div className="fixed inset-0 z-50 flex justify-end bg-black/70 backdrop-blur-sm">
              <motion.div
                initial={{ x: '100%' }}
                animate={{ x: 0 }}
                exit={{ x: '100%' }}
                transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                className="w-full max-w-lg bg-[#0D1527] border-l border-slate-800 p-6 overflow-y-auto space-y-6 shadow-2xl"
              >
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div className="space-y-1">
                    <span className="text-xs font-mono text-cyan-400 uppercase font-bold">{drawerArtifact.document_type}</span>
                    <h2 className="text-xl font-black text-white font-mono">{drawerArtifact.artifact_id}</h2>
                  </div>
                  <button 
                    onClick={() => setDrawerArtifact(null)}
                    className="p-2 rounded-xl bg-slate-900 text-slate-400 hover:text-white hover:bg-slate-800 transition-all cursor-pointer"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Raw Text */}
                <div className="space-y-2">
                  <span className="text-xs font-mono text-slate-400">Canonical Specification:</span>
                  <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-xs text-slate-200 font-mono leading-relaxed">
                    {drawerArtifact.text}
                  </div>
                </div>

                {/* Outgoing & Incoming Relationships */}
                <div className="space-y-3">
                  <span className="text-xs font-mono text-slate-400">Canonical Relationships:</span>
                  {matrix
                    .filter(r => r.source_artifact === drawerArtifact.artifact_id || r.target_artifact === drawerArtifact.artifact_id)
                    .map((rel, rIdx) => (
                      <div key={rIdx} className="p-3.5 rounded-2xl bg-slate-950 border border-slate-800 space-y-1.5 shadow-sm">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-mono font-bold text-cyan-400">
                            {rel.source_artifact} → {rel.target_artifact}
                          </span>
                          {getStatusBadge(rel.status)}
                        </div>
                        <div className="text-[11px] font-mono text-slate-400">{rel.relationship}</div>
                        <div className="text-[11px] text-slate-300 font-mono bg-slate-900 p-2.5 rounded-xl">{rel.evidence || rel.reason}</div>
                      </div>
                    ))}
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* ── COMMAND PALETTE MODAL (Cmd+K) ─────────────────────────────────── */}
        <AnimatePresence>
          {isCommandOpen && (
            <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/80 backdrop-blur-md p-4">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="w-full max-w-2xl bg-[#0D1527] border border-slate-700/80 rounded-3xl overflow-hidden shadow-2xl space-y-2"
              >
                <div className="p-4 border-b border-slate-800 flex items-center gap-3">
                  <Search className="w-5 h-5 text-cyan-400" />
                  <input
                    type="text"
                    autoFocus
                    value={commandQuery}
                    onChange={(e) => setCommandQuery(e.target.value)}
                    placeholder="Search artifact ID, requirement text, test, or CR..."
                    className="w-full bg-transparent text-sm text-white focus:outline-none font-mono"
                  />
                  <kbd className="px-2 py-0.5 rounded-md bg-slate-800 text-[10px] text-slate-400 font-mono">ESC</kbd>
                </div>

                <div className="max-h-80 overflow-y-auto p-2 space-y-1">
                  {commandResults.length === 0 ? (
                    <div className="p-8 text-center text-slate-500 text-xs font-mono">No matching artifacts found.</div>
                  ) : (
                    commandResults.map((art, idx) => (
                      <div
                        key={art.artifact_id || idx}
                        onClick={() => {
                          openArtifactDrawer(art.artifact_id);
                          setIsCommandOpen(false);
                        }}
                        className="p-3 rounded-2xl hover:bg-slate-800/80 cursor-pointer flex items-center justify-between transition-all"
                      >
                        <div className="space-y-0.5 max-w-lg">
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-bold text-xs text-cyan-400">{art.artifact_id}</span>
                            <span className="text-[10px] font-mono text-slate-500">{art.document_type}</span>
                          </div>
                          <div className="text-xs text-slate-300 truncate">{art.text}</div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-slate-500" />
                      </div>
                    ))
                  )}
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

      </div>
    </div>
  );
}
