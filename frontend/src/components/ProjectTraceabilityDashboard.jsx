import React, { useState, useMemo } from 'react';
import { 
  FileText, Database, Layers, CheckCircle2, AlertTriangle, AlertCircle, 
  Search, ShieldAlert, Download, Sparkles, Filter, ChevronRight, Activity,
  GitPullRequest, Clock, Server, Check, X, Network, Link2, ArrowRight
} from 'lucide-react';
import { motion } from 'framer-motion';

export default function ProjectTraceabilityDashboard({ result }) {
  const [viewTab, setViewTab] = useState('matrix'); // 'matrix' | 'chains' | 'graph'
  const [statusFilter, setStatusFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGraphNode, setSelectedGraphNode] = useState(null);

  const summary = result.summary || {};
  const matrix = result.traceability_matrix || [];
  const chains = result.traceability_chains || [];
  const graph = result.traceability_graph || { nodes: [], edges: [] };
  const topConflicts = result.top_conflicts || [];
  const topUnmapped = result.top_unmapped || [];
  const crImpacts = result.change_request_impacts || [];
  const momLinks = result.meeting_minutes_links || [];
  const docList = result.documents || [];
  const pathCoverage = summary.path_coverage || {};

  // Filter pairwise direct relationship rows
  const filteredMatrix = useMemo(() => {
    return matrix.filter(row => {
      const matchFilter = statusFilter === 'All' || row.status === statusFilter;
      const term = searchQuery.toLowerCase();
      
      const sId = row.source_artifact ? row.source_artifact.toLowerCase() : '';
      const sDoc = row.source_document ? row.source_document.toLowerCase() : '';
      const sText = row.source_text ? row.source_text.toLowerCase() : '';
      const tId = row.target_artifact ? row.target_artifact.toLowerCase() : '';
      const tDoc = row.target_document ? row.target_document.toLowerCase() : '';
      const tText = row.target_text ? row.target_text.toLowerCase() : '';
      const rel = row.relationship ? row.relationship.toLowerCase() : '';
      const ev = row.evidence ? row.evidence.toLowerCase() : '';

      const matchSearch = term === '' || sId.includes(term) || sDoc.includes(term) || sText.includes(term) || 
                          tId.includes(term) || tDoc.includes(term) || tText.includes(term) || rel.includes(term) || ev.includes(term);

      return matchFilter && matchSearch;
    });
  }, [matrix, statusFilter, searchQuery]);

  const handlePrint = () => {
    window.print();
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'MATCHED':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1 w-fit">
            <CheckCircle2 className="w-3 h-3" /> MATCHED
          </span>
        );
      case 'PARTIAL':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30 flex items-center gap-1 w-fit">
            <AlertTriangle className="w-3 h-3" /> PARTIAL
          </span>
        );
      case 'CONFLICT':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center gap-1 w-fit">
            <AlertCircle className="w-3 h-3" /> CONFLICT
          </span>
        );
      case 'UNMAPPED':
      default:
        return (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-slate-800 text-slate-400 border border-slate-700 flex items-center gap-1 w-fit">
            <X className="w-3 h-3" /> UNMAPPED
          </span>
        );
    }
  };

  const getRelBadge = (rel) => {
    switch (rel) {
      case 'TRACEABLE_TO':
        return 'bg-blue-500/10 text-blue-300 border-blue-500/30';
      case 'IMPLEMENTED_BY':
        return 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30';
      case 'REALIZED_BY':
        return 'bg-purple-500/10 text-purple-300 border-purple-500/30';
      case 'VERIFIED_BY':
        return 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
      case 'AFFECTS':
        return 'bg-rose-500/10 text-rose-300 border-rose-500/30';
      case 'RELATED_TO':
        return 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  // Group nodes by tier for structured visual DAG
  const nodesByTier = useMemo(() => {
    const tiers = {
      "BRD": [],
      "SRS": [],
      "FRD": [],
      "User Story": [],
      "Test Case": [],
      "Change Request": [],
      "Meeting Minutes": []
    };
    (graph.nodes || []).forEach(node => {
      const type = node.document_type || "Other";
      if (tiers[type]) {
        tiers[type].push(node);
      }
    });
    return tiers;
  }, [graph.nodes]);

  return (
    <div className="bg-transparent min-h-screen py-8 text-slate-100 font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Top Header & Export */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4 print:hidden">
          <div>
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-neon-blue/10 border border-neon-blue/30 text-neon-blue text-xs font-mono font-bold uppercase mb-2">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Mode 2: Project Intelligence
            </div>
            <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
              ReqVision AI — <span className="text-gradient">Software Intelligence Report</span>
            </h1>
            <p className="text-slate-400 mt-1 text-sm sm:text-base font-medium">
              Cross-Document Lexical Traceability Analysis across all {summary.total_documents || 7} project artifacts
            </p>
          </div>

          <button 
            onClick={handlePrint}
            className="flex items-center gap-2 bg-slate-900 border border-slate-700 hover:border-neon-blue/60 text-slate-200 hover:text-white px-5 py-2.5 rounded-xl shadow-lg font-bold text-sm transition-all glass-card"
          >
            <Download className="w-4 h-4 text-neon-blue" />
            Export Traceability Report
          </button>
        </div>

        {/* Print Header (Visible only when printing/exporting to PDF) */}
        <div className="hidden print:flex fixed top-0 left-0 w-full justify-between items-center text-[10px] text-slate-400 border-b border-slate-700 pb-1.5 pt-1.5 bg-slate-900 z-50 px-8">
          <span className="font-bold text-slate-200">ReqVision AI | Software Intelligence & Cross-Document Traceability Report</span>
          <span>Generated on {new Date().toLocaleDateString()}</span>
        </div>

        {/* 1. Project High-Level Metrics Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-sm">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase">Project Documents</div>
            <div className="text-2xl font-black text-white mt-1">{summary.total_documents || docList.length}</div>
            <div className="text-[10px] text-slate-400 mt-1">Single collection</div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-sm">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase">Total Artifacts</div>
            <div className="text-2xl font-black text-neon-blue mt-1">{summary.total_artifacts || 0}</div>
            <div className="text-[10px] text-slate-400 mt-1">Extracted & normalized</div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-sm">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase">Traceability Coverage</div>
            <div className="text-2xl font-black text-emerald-400 mt-1">{summary.coverage_percentage}%</div>
            <div className="text-[10px] text-slate-400 mt-1">Root requirements mapped</div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-sm">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase">Matched Links</div>
            <div className="text-2xl font-black text-emerald-400 mt-1">{summary.status_breakdown?.MATCHED || 0}</div>
            <div className="text-[10px] text-emerald-400/80 mt-1">Verified relationships</div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-sm">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase">Contradictions</div>
            <div className="text-2xl font-black text-rose-400 mt-1">{summary.status_breakdown?.CONFLICT || 0}</div>
            <div className="text-[10px] text-rose-400/80 mt-1">Detected conflicts</div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-sm">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase">Unmapped Artifacts</div>
            <div className="text-2xl font-black text-slate-400 mt-1">{summary.status_breakdown?.UNMAPPED || 0}</div>
            <div className="text-[10px] text-slate-500 mt-1">Gaps in downstream spec</div>
          </div>
        </div>

        {/* 2. Path-Specific Traceability Coverage Bars */}
        <div className="mb-8 p-6 rounded-3xl bg-slate-900/40 border border-slate-800 backdrop-blur-xl">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Layers className="w-4 h-4 text-neon-blue" />
            Engineering Traceability Path Coverage
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800">
              <div className="text-[10px] font-mono text-slate-400 uppercase">BRD → SRS (Traceable)</div>
              <div className="text-lg font-black text-blue-400 mt-1">{pathCoverage.brd_to_srs_coverage || 'N/A'}</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800">
              <div className="text-[10px] font-mono text-slate-400 uppercase">SRS → FRD (Implemented)</div>
              <div className="text-lg font-black text-cyan-400 mt-1">{pathCoverage.srs_to_frd_coverage || 'N/A'}</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800">
              <div className="text-[10px] font-mono text-slate-400 uppercase">SRS → User Story (Realized)</div>
              <div className="text-lg font-black text-purple-400 mt-1">{pathCoverage.srs_to_user_story_coverage || 'N/A'}</div>
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800">
              <div className="text-[10px] font-mono text-slate-400 uppercase">User Story → Test Case (Verified)</div>
              <div className="text-lg font-black text-emerald-400 mt-1">{pathCoverage.user_story_to_test_case_coverage || 'N/A'}</div>
            </div>
          </div>
        </div>

        {/* 3. Top Conflicts & Unmapped Alerts */}
        {topConflicts.length > 0 && (
          <div className="mb-8 p-6 rounded-3xl bg-rose-950/20 border border-rose-500/40 backdrop-blur-xl shadow-xl">
            <div className="flex items-center gap-2.5 text-rose-400 font-black text-lg mb-3">
              <ShieldAlert className="w-5 h-5" />
              <span>Critical Requirement Contradictions Detected ({topConflicts.length})</span>
            </div>
            <div className="space-y-3">
              {topConflicts.map((conf, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-slate-950/80 border border-rose-900/60 text-sm">
                  <div className="flex items-center gap-2 text-rose-300 font-bold mb-1">
                    <span className="px-2 py-0.5 rounded bg-rose-900/40 text-xs font-mono">{conf.source_id}</span>
                    <span>{conf.source_doc}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-rose-500" />
                    <span className="px-2 py-0.5 rounded bg-rose-900/40 text-xs font-mono">{conf.target_id}</span>
                    <span>{conf.target_doc}</span>
                  </div>
                  <p className="text-slate-300 text-xs mb-2 italic">"{conf.source_text}"</p>
                  <div className="p-2.5 rounded-xl bg-rose-950/40 border border-rose-900/40 text-rose-200 text-xs font-semibold">
                    <strong>Contradiction Reason:</strong> {conf.reason}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {topUnmapped.length > 0 && (
          <div className="mb-8 p-6 rounded-3xl bg-amber-950/20 border border-amber-500/30 backdrop-blur-xl">
            <div className="flex items-center gap-2.5 text-amber-300 font-black text-base mb-3">
              <AlertTriangle className="w-5 h-5" />
              <span>Unmapped Requirements / Specification Gaps ({topUnmapped.length})</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {topUnmapped.map((unm, idx) => (
                <div key={idx} className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-bold text-amber-300">{unm.artifact_id}</span>
                    <span className="text-[10px] text-slate-500">{unm.document_name}</span>
                  </div>
                  <p className="text-slate-300 mb-1.5 italic">"{unm.text}"</p>
                  <span className="text-[11px] text-amber-400/80 font-medium block">Gap: {unm.reason}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 4. Tab Selector: Traceability Matrix vs. Traceability Chains vs. Traceability Graph */}
        <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-slate-950/80 border border-slate-800 mb-6 w-fit">
          <button
            onClick={() => setViewTab('matrix')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              viewTab === 'matrix' ? 'bg-neon-blue/20 text-white border border-neon-blue/40 shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Database className="w-4 h-4 text-neon-blue" />
            Source → Target Matrix ({matrix.length})
          </button>
          <button
            onClick={() => setViewTab('chains')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              viewTab === 'chains' ? 'bg-purple-500/20 text-white border border-purple-500/40 shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Layers className="w-4 h-4 text-purple-400" />
            End-to-End Chains ({chains.length})
          </button>
          <button
            onClick={() => setViewTab('graph')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
              viewTab === 'graph' ? 'bg-indigo-500/20 text-white border border-indigo-500/40 shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Network className="w-4 h-4 text-indigo-400" />
            Visual Traceability Network Graph ({graph.edges?.length || 0} Edges)
          </button>
        </div>

        {/* TAB 1: Source -> Target Traceability Matrix */}
        {viewTab === 'matrix' && (
          <div className="mb-12 rounded-3xl bg-slate-950/90 border border-slate-800 shadow-2xl overflow-hidden backdrop-blur-2xl">
            {/* Filter bar */}
            <div className="p-5 border-b border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-900/60">
              <div>
                <h2 className="text-base sm:text-lg font-black text-white tracking-tight flex items-center gap-2">
                  <Database className="w-5 h-5 text-neon-blue" />
                  Pairwise Traceability Matrix
                </h2>
                <p className="text-xs text-slate-400">Explicit direct mappings with lexical evidence</p>
              </div>

              <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
                <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
                  {['All', 'MATCHED', 'PARTIAL', 'CONFLICT', 'UNMAPPED'].map(st => (
                    <button
                      key={st}
                      onClick={() => setStatusFilter(st)}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                        statusFilter === st ? 'bg-neon-blue/20 text-white border border-neon-blue/40' : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      {st}
                    </button>
                  ))}
                </div>

                <div className="relative flex-1 sm:w-60">
                  <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="Search artifact or keyword..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-neon-blue/60"
                  />
                </div>
              </div>
            </div>

            {/* Matrix Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs sm:text-sm">
                <thead>
                  <tr className="bg-slate-900/90 border-b border-slate-800 text-[11px] font-mono font-bold text-slate-400 uppercase tracking-wider">
                    <th className="p-3.5 pl-6">Source Artifact</th>
                    <th className="p-3.5">Relationship</th>
                    <th className="p-3.5">Target Artifact</th>
                    <th className="p-3.5">Status</th>
                    <th className="p-3.5">Lexical Sim</th>
                    <th className="p-3.5">Confidence</th>
                    <th className="p-3.5 pr-6">Evidence / Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredMatrix.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-900/50 transition-colors">
                      {/* Source Artifact */}
                      <td className="p-3.5 pl-6 align-top">
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono font-bold text-neon-blue">{row.source_artifact}</span>
                          <span className="text-[10px] font-mono text-slate-500">[{row.source_type}]</span>
                        </div>
                        <span className="text-xs text-slate-300 line-clamp-2 mt-0.5" title={row.source_text}>{row.source_text}</span>
                      </td>

                      {/* Relationship */}
                      <td className="p-3.5 align-top">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border ${getRelBadge(row.relationship)}`}>
                          {row.relationship}
                        </span>
                      </td>

                      {/* Target Artifact */}
                      <td className="p-3.5 align-top">
                        {row.target_artifact !== '—' ? (
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span className="font-mono font-bold text-indigo-300">{row.target_artifact}</span>
                              <span className="text-[10px] font-mono text-slate-500">[{row.target_type}]</span>
                            </div>
                            <span className="text-xs text-slate-300 line-clamp-2 mt-0.5" title={row.target_text}>{row.target_text}</span>
                          </div>
                        ) : (
                          <span className="text-slate-600 font-mono">—</span>
                        )}
                      </td>

                      {/* Status */}
                      <td className="p-3.5 align-top">
                        {getStatusBadge(row.status)}
                      </td>

                      {/* Lexical Sim */}
                      <td className="p-3.5 align-top font-mono text-slate-300">
                        {row.similarity > 0 ? (
                          <span className="font-bold text-xs">{row.similarity.toFixed(2)}</span>
                        ) : (
                          <span className="text-slate-600">—</span>
                        )}
                      </td>

                      {/* Confidence */}
                      <td className="p-3.5 align-top font-mono text-xs">
                        <span className={row.confidence === 'High' ? 'text-emerald-400 font-bold' : row.confidence === 'Medium' ? 'text-amber-400 font-semibold' : 'text-slate-500'}>
                          {row.confidence}
                        </span>
                      </td>

                      {/* Evidence */}
                      <td className="p-3.5 pr-6 align-top text-xs text-slate-400 italic">
                        {row.evidence}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 2: End-to-End Traceability Chains */}
        {viewTab === 'chains' && (
          <div className="mb-12 space-y-4">
            {chains.map((chain, idx) => (
              <div key={chain.chain_id || idx} className="p-5 rounded-2xl bg-slate-950/90 border border-slate-800 shadow-md">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-mono font-bold text-xs text-neon-blue">{chain.chain_id}</span>
                  {getStatusBadge(chain.overall_status)}
                </div>

                <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs font-mono mb-3">
                  <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-amber-300 font-bold block">{chain.brd?.id || '—'}</span>
                    <span className="text-[10px] text-slate-400">BRD</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                  <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-blue-300 font-bold block">{chain.srs?.id || '—'}</span>
                    <span className="text-[10px] text-slate-400">SRS</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                  <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-cyan-300 font-bold block">{chain.frd?.id || '—'}</span>
                    <span className="text-[10px] text-slate-400">FRD</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                  <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-purple-300 font-bold block">{chain.user_story?.id || '—'}</span>
                    <span className="text-[10px] text-slate-400">User Story</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                  <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-emerald-300 font-bold block">{chain.test_case?.id || '—'}</span>
                    <span className="text-[10px] text-slate-400">Test Case</span>
                  </div>
                </div>

                {chain.evidence_chain && chain.evidence_chain.length > 0 && (
                  <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80 text-[11px] text-slate-400">
                    <strong>Trace Evidence:</strong> {chain.evidence_chain.join(' → ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* TAB 3: Visual Traceability Network Graph (Visual Multi-Tier DAG) */}
        {viewTab === 'graph' && (
          <div className="mb-12 p-6 rounded-3xl bg-slate-950/90 border border-slate-800 shadow-2xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Network className="w-5 h-5 text-indigo-400" />
                  Visual Traceability Network Graph ({graph.edges?.length || 0} Directed Edges)
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">Interactive multi-tier engineering dependency network discovered by lexical verification</p>
              </div>

              {selectedGraphNode && (
                <div className="p-2 px-3 rounded-xl bg-neon-blue/10 border border-neon-blue/30 text-xs flex items-center gap-2">
                  <span className="text-slate-400">Selected Node:</span>
                  <span className="font-mono font-bold text-neon-blue">{selectedGraphNode.artifact_id}</span>
                  <button onClick={() => setSelectedGraphNode(null)} className="text-slate-400 hover:text-white ml-2">×</button>
                </div>
              )}
            </div>

            {/* Multi-Tier Directed Flow Visualization */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 overflow-x-auto pb-4">
              {['BRD', 'SRS', 'FRD', 'User Story', 'Test Case'].map(tierName => (
                <div key={tierName} className="p-3.5 rounded-2xl bg-slate-900/50 border border-slate-800 flex flex-col gap-2 min-w-[170px]">
                  <div className="text-[11px] font-mono font-bold text-slate-400 uppercase border-b border-slate-800 pb-1.5 flex items-center justify-between">
                    <span>{tierName}</span>
                    <span className="text-[10px] text-slate-500">{(nodesByTier[tierName] || []).length}</span>
                  </div>
                  
                  <div className="space-y-2 mt-1">
                    {(nodesByTier[tierName] || []).map(node => {
                      const isSelected = selectedGraphNode?.id === node.id;
                      return (
                        <div
                          key={node.id}
                          onClick={() => setSelectedGraphNode(node)}
                          className={`p-2 rounded-xl text-xs font-mono cursor-pointer transition-all border ${
                            isSelected 
                              ? 'bg-neon-blue/20 border-neon-blue text-white shadow-lg' 
                              : 'bg-slate-950/80 border-slate-800/80 text-slate-300 hover:border-slate-600'
                          }`}
                        >
                          <div className="font-bold flex items-center justify-between">
                            <span className={tierName === 'BRD' ? 'text-amber-400' : tierName === 'SRS' ? 'text-blue-400' : tierName === 'FRD' ? 'text-cyan-400' : tierName === 'User Story' ? 'text-purple-400' : 'text-emerald-400'}>
                              {node.artifact_id}
                            </span>
                          </div>
                          <p className="text-[10px] text-slate-400 line-clamp-2 mt-1">{node.text}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            {/* Edge Connections List for Selected Node or All */}
            <div className="mt-6 pt-4 border-t border-slate-800">
              <h4 className="text-xs font-mono font-bold text-slate-400 uppercase mb-3">
                {selectedGraphNode ? `Direct Links for ${selectedGraphNode.artifact_id}` : 'All Discovered Direct Graph Links'}
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
                {(graph.edges || [])
                  .filter(e => !selectedGraphNode || e.source === selectedGraphNode.id || e.target === selectedGraphNode.id)
                  .map((edge, i) => (
                    <div key={i} className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs flex items-center justify-between">
                      <span className="font-mono text-neon-blue font-bold truncate max-w-[100px]">{edge.source.split('::')[1] || edge.source}</span>
                      <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border ${getRelBadge(edge.relationship)}`}>
                        {edge.relationship}
                      </span>
                      <span className="font-mono text-indigo-300 font-bold truncate max-w-[100px]">{edge.target.split('::')[1] || edge.target}</span>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        )}

        {/* 5. Supporting Artifact Impacts: Change Requests & Meeting Minutes */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Change Request Impact Links */}
          <div className="p-6 rounded-3xl bg-slate-950/80 border border-slate-800 backdrop-blur-xl">
            <div className="flex items-center gap-2.5 mb-4">
              <GitPullRequest className="w-5 h-5 text-rose-400" />
              <div>
                <h3 className="text-base font-bold text-white">Change Request Impact Matrix</h3>
                <p className="text-xs text-slate-400">Explicit AFFECTS relationships to master specifications</p>
              </div>
            </div>

            {crImpacts.length > 0 ? (
              <div className="space-y-3">
                {crImpacts.map((cr, i) => (
                  <div key={i} className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono font-bold text-rose-300">{cr.cr_id}</span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-rose-950 text-rose-300 border border-rose-800">
                        {cr.status} ({Math.round(cr.similarity * 100)}% overlap)
                      </span>
                    </div>
                    <p className="text-slate-300 font-medium mb-2">"{cr.cr_text}"</p>
                    {cr.affected_req_id !== '—' ? (
                      <div className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 flex items-center gap-2">
                        <Link2 className="w-3.5 h-3.5 text-neon-blue shrink-0" />
                        <span><strong>Affects:</strong> {cr.affected_doc} [{cr.affected_req_id}]</span>
                      </div>
                    ) : (
                      <span className="text-slate-500 italic">No specific software requirement affected (Unmapped)</span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">No Change Requests uploaded in collection.</p>
            )}
          </div>

          {/* Meeting Minutes Governance Links */}
          <div className="p-6 rounded-3xl bg-slate-950/80 border border-slate-800 backdrop-blur-xl">
            <div className="flex items-center gap-2.5 mb-4">
              <Clock className="w-5 h-5 text-indigo-400" />
              <div>
                <h3 className="text-base font-bold text-white">Meeting Minutes Governance</h3>
                <p className="text-xs text-slate-400">Decisions & action items referencing project artifacts</p>
              </div>
            </div>

            {momLinks.length > 0 ? (
              <div className="space-y-3">
                {momLinks.map((mom, i) => (
                  <div key={i} className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono font-bold text-indigo-300">{mom.mom_id}</span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-indigo-950 text-indigo-300 border border-indigo-800">
                        {mom.status}
                      </span>
                    </div>
                    <p className="text-slate-300 font-medium mb-2">"{mom.mom_text}"</p>
                    {mom.referenced_req_id !== '—' ? (
                      <div className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 flex items-center gap-2">
                        <Link2 className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                        <span><strong>References:</strong> {mom.referenced_doc} [{mom.referenced_req_id}]</span>
                      </div>
                    ) : (
                      <span className="text-slate-500 italic">General governance note</span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">No Meeting Minutes uploaded in collection.</p>
            )}
          </div>
        </div>

        {/* Phase 2 Clean Footer */}
        <footer className="mt-16 pt-8 border-t border-slate-800 pb-12 print:hidden">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6 text-xs text-slate-400 font-medium">
            <div className="flex flex-wrap items-center gap-6">
              <span className="flex items-center gap-1.5"><Layers className="w-4 h-4 text-neon-blue"/> ReqVision AI — Software Intelligence Platform</span>
              <span className="flex items-center gap-1.5"><Database className="w-4 h-4 text-purple-400"/> Cross-Document Lexical Traceability Matrix</span>
            </div>
            <div className="text-slate-500">
              Deterministic Lexical Verification • 100% Anti-Hallucination Safe
            </div>
          </div>
        </footer>

      </div>
    </div>
  );
}
