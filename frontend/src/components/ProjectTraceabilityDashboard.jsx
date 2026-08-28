import React, { useState, useMemo } from 'react';
import { 
  FileText, Database, Layers, CheckCircle2, AlertTriangle, AlertCircle, 
  Search, ShieldAlert, Download, Sparkles, Filter, ChevronRight, Activity,
  GitPullRequest, Clock, Server, Check, X, Network, Link2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ProjectTraceabilityDashboard({ result }) {
  const [statusFilter, setStatusFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedChain, setSelectedChain] = useState(null);

  const summary = result.summary || {};
  const matrix = result.traceability_matrix || [];
  const graph = result.traceability_graph || { nodes: [], edges: [] };
  const topConflicts = result.top_conflicts || [];
  const topUnmapped = result.top_unmapped || [];
  const crImpacts = result.change_request_impacts || [];
  const momLinks = result.meeting_minutes_links || [];
  const docList = result.documents || [];

  const filteredMatrix = useMemo(() => {
    return matrix.filter(row => {
      const matchFilter = statusFilter === 'All' || row.overall_status === statusFilter;
      const term = searchQuery.toLowerCase();
      
      const brdMatch = row.brd && (row.brd.id.toLowerCase().includes(term) || row.brd.text.toLowerCase().includes(term));
      const srsMatch = row.srs && (row.srs.id.toLowerCase().includes(term) || row.srs.text.toLowerCase().includes(term));
      const frdMatch = row.frd && (row.frd.id.toLowerCase().includes(term) || row.frd.text.toLowerCase().includes(term));
      const usMatch = row.user_story && (row.user_story.id.toLowerCase().includes(term) || row.user_story.text.toLowerCase().includes(term));
      const tcMatch = row.test_case && (row.test_case.id.toLowerCase().includes(term) || row.test_case.text.toLowerCase().includes(term));
      const evMatch = row.evidence_chain && row.evidence_chain.some(e => e.toLowerCase().includes(term));

      return matchFilter && (brdMatch || srsMatch || frdMatch || usMatch || tcMatch || evMatch || term === '');
    });
  }, [matrix, statusFilter, searchQuery]);

  const handlePrint = () => {
    window.print();
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'MATCHED':
        return (
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5 w-fit">
            <CheckCircle2 className="w-3.5 h-3.5" /> MATCHED
          </span>
        );
      case 'PARTIAL':
        return (
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30 flex items-center gap-1.5 w-fit">
            <AlertTriangle className="w-3.5 h-3.5" /> PARTIAL
          </span>
        );
      case 'CONFLICT':
        return (
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center gap-1.5 w-fit">
            <AlertCircle className="w-3.5 h-3.5" /> CONFLICT
          </span>
        );
      case 'UNMAPPED':
      default:
        return (
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-slate-800 text-slate-400 border border-slate-700 flex items-center gap-1.5 w-fit">
            <X className="w-3.5 h-3.5" /> UNMAPPED
          </span>
        );
    }
  };

  return (
    <div className="bg-transparent min-h-screen py-8 text-slate-100 font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Top Header & Actions */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4 print:hidden">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-neon-blue/10 border border-neon-blue/30 text-neon-blue text-xs font-mono font-bold uppercase mb-2">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Phase 2 Project Intelligence
            </div>
            <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
              Cross-Document <span className="text-gradient">Traceability Matrix</span>
            </h1>
            <p className="text-slate-400 mt-1 text-sm sm:text-base font-medium">
              Multi-document semantic verification across BRD → SRS → FRD → User Stories → Test Cases
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

        {/* 1. Project High-Level Metrics Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-sm">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase">Total Documents</div>
            <div className="text-2xl font-black text-white mt-1">{summary.total_documents || docList.length}</div>
            <div className="text-[10px] text-slate-400 mt-1">Project artifacts</div>
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
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase">Fully Matched</div>
            <div className="text-2xl font-black text-emerald-400 mt-1">{summary.status_breakdown?.MATCHED || 0}</div>
            <div className="text-[10px] text-emerald-400/80 mt-1">Verified chains</div>
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

        {/* 2. Top Conflict & Unmapped Alerts (If Any) */}
        {topConflicts.length > 0 && (
          <div className="mb-8 p-6 rounded-3xl bg-rose-950/20 border border-rose-500/40 backdrop-blur-xl shadow-xl shadow-rose-950/20">
            <div className="flex items-center gap-2.5 text-rose-400 font-black text-lg mb-3">
              <ShieldAlert className="w-5 h-5" />
              <span>Critical Requirement Contradiction Detected ({topConflicts.length})</span>
            </div>
            <div className="space-y-3">
              {topConflicts.map((conf, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-slate-950/80 border border-rose-900/60 text-sm">
                  <div className="flex items-center gap-2 text-rose-300 font-bold mb-1">
                    <span className="px-2 py-0.5 rounded bg-rose-900/40 text-xs font-mono">{conf.source_id}</span>
                    <span>{conf.source_doc}</span>
                  </div>
                  <p className="text-slate-300 text-xs mb-2 italic">"{conf.source_text}"</p>
                  <div className="p-2.5 rounded-xl bg-rose-950/40 border border-rose-900/40 text-rose-200 text-xs font-semibold">
                    <strong>Contradiction Evidence:</strong> {conf.reason}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 3. Document Collection Overview */}
        <div className="mb-8 p-6 rounded-3xl bg-slate-900/40 border border-slate-800 backdrop-blur-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Database className="w-4 h-4 text-neon-blue" />
              Project Document Artifacts Overview
            </h3>
            <span className="text-xs font-mono text-slate-400">Zero Baseline/Updated Partitioning</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
            {Object.entries(summary.document_types || {}).map(([type, count]) => (
              <div key={type} className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800/80 text-center">
                <span className="text-xs font-mono font-bold text-slate-300 block">{type}</span>
                <span className="text-xl font-black text-white mt-1 block">{count}</span>
                <span className="text-[10px] text-slate-500 font-medium">Artifacts</span>
              </div>
            ))}
          </div>
        </div>

        {/* 4. Traceability Matrix Table */}
        <div className="mb-12 rounded-3xl bg-slate-950/90 border border-slate-800 shadow-2xl overflow-hidden backdrop-blur-2xl">
          
          {/* Controls Bar */}
          <div className="p-6 border-b border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-900/60">
            <div>
              <h2 className="text-lg sm:text-xl font-black text-white tracking-tight flex items-center gap-2">
                <Network className="w-5 h-5 text-neon-blue" />
                End-to-End Traceability Matrix
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">Showing {filteredMatrix.length} discovered requirement chains</p>
            </div>

            <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
              {/* Status Filter */}
              <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
                {['All', 'MATCHED', 'PARTIAL', 'CONFLICT', 'UNMAPPED'].map(st => (
                  <button
                    key={st}
                    onClick={() => setStatusFilter(st)}
                    className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                      statusFilter === st 
                        ? 'bg-neon-blue/20 text-white border border-neon-blue/40 shadow-sm' 
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {st}
                  </button>
                ))}
              </div>

              {/* Search Box */}
              <div className="relative flex-1 sm:w-64">
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search requirement ID or text..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-neon-blue/60"
                />
              </div>
            </div>
          </div>

          {/* Table Container */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs sm:text-sm">
              <thead>
                <tr className="bg-slate-900/90 border-b border-slate-800 text-[11px] font-mono font-bold text-slate-400 uppercase tracking-wider">
                  <th className="p-4 pl-6">BRD Artifact</th>
                  <th className="p-4">SRS Requirement</th>
                  <th className="p-4">FRD Spec</th>
                  <th className="p-4">User Story</th>
                  <th className="p-4">Test Case</th>
                  <th className="p-4 pr-6">Status & Evidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredMatrix.map((row, idx) => (
                  <tr 
                    key={row.chain_id || idx}
                    onClick={() => setSelectedChain(row)}
                    className="hover:bg-slate-900/50 transition-colors cursor-pointer group"
                  >
                    {/* BRD Cell */}
                    <td className="p-4 pl-6 align-top">
                      {row.brd ? (
                        <div>
                          <span className="font-mono font-bold text-amber-300 block">{row.brd.id}</span>
                          <span className="text-xs text-slate-300 line-clamp-2 mt-0.5" title={row.brd.text}>{row.brd.text}</span>
                        </div>
                      ) : (
                        <span className="text-slate-600 font-mono">—</span>
                      )}
                    </td>

                    {/* SRS Cell */}
                    <td className="p-4 align-top">
                      {row.srs ? (
                        <div>
                          <span className="font-mono font-bold text-blue-300 block">{row.srs.id}</span>
                          <span className="text-xs text-slate-300 line-clamp-2 mt-0.5" title={row.srs.text}>{row.srs.text}</span>
                        </div>
                      ) : (
                        <span className="text-slate-600 font-mono">—</span>
                      )}
                    </td>

                    {/* FRD Cell */}
                    <td className="p-4 align-top">
                      {row.frd ? (
                        <div>
                          <span className="font-mono font-bold text-cyan-300 block">{row.frd.id}</span>
                          <span className="text-xs text-slate-300 line-clamp-2 mt-0.5" title={row.frd.text}>{row.frd.text}</span>
                        </div>
                      ) : (
                        <span className="text-slate-600 font-mono">—</span>
                      )}
                    </td>

                    {/* User Story Cell */}
                    <td className="p-4 align-top">
                      {row.user_story ? (
                        <div>
                          <span className="font-mono font-bold text-purple-300 block">{row.user_story.id}</span>
                          <span className="text-xs text-slate-300 line-clamp-2 mt-0.5" title={row.user_story.text}>{row.user_story.text}</span>
                        </div>
                      ) : (
                        <span className="text-slate-600 font-mono">—</span>
                      )}
                    </td>

                    {/* Test Case Cell */}
                    <td className="p-4 align-top">
                      {row.test_case ? (
                        <div>
                          <span className="font-mono font-bold text-emerald-300 block">{row.test_case.id}</span>
                          <span className="text-xs text-slate-300 line-clamp-2 mt-0.5" title={row.test_case.text}>{row.test_case.text}</span>
                        </div>
                      ) : (
                        <span className="text-slate-600 font-mono">—</span>
                      )}
                    </td>

                    {/* Status & Evidence Cell */}
                    <td className="p-4 pr-6 align-top">
                      <div className="flex flex-col gap-1.5">
                        {getStatusBadge(row.overall_status)}
                        {row.evidence_chain && row.evidence_chain.length > 0 && (
                          <span className="text-[11px] text-slate-400 line-clamp-1 italic" title={row.evidence_chain.join(' | ')}>
                            {row.evidence_chain[0]}
                          </span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

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
                    {cr.affected_req_id ? (
                      <div className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 flex items-center gap-2">
                        <Link2 className="w-3.5 h-3.5 text-neon-blue shrink-0" />
                        <span><strong>Affects:</strong> {cr.affected_doc} [{cr.affected_req_id}]</span>
                      </div>
                    ) : (
                      <span className="text-slate-500 italic">No specific requirement affected</span>
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
                    {mom.referenced_req_id ? (
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

      </div>
    </div>
  );
}
