import { useState } from 'react';
import { Table, ArrowUpDown, Search, FileText, GitPullRequest, ArrowRight, Layers, CheckCircle2, AlertTriangle, PlusCircle, XCircle, Link2 } from 'lucide-react';

export default function TraceabilityMatrix({ changes, cross_document_analysis, onRowClick }) {
  const [sortConfig, setSortConfig] = useState({ key: 'req_id', direction: 'ascending' });
  const [filter, setFilter] = useState('');
  const [activeTab, setActiveTab] = useState('all');

  // Use traceability items from cross_document_analysis if available, otherwise fallback to changes
  const rawItems = cross_document_analysis?.traceability || changes.map(c => ({
    req_id: c.req_id,
    text: c.new || c.old || '',
    source_document: c.source_document || c.updated_source || c.baseline_source || 'Unknown',
    matched_req_id: c.matched_requirement_id || (c.status === 'Modified' || c.status === 'Unchanged' ? c.req_id : null),
    matched_document: c.matched_document || c.baseline_source || (c.status === 'Modified' || c.status === 'Unchanged' ? 'Baseline' : null),
    relationship: c.relationship || (c.status === 'Unchanged' ? 'SAME_REQUIREMENT' : c.status === 'Modified' ? 'MODIFIED_FROM' : c.status === 'Added' ? 'ADDED_IN' : 'REMOVED_FROM'),
    status: c.status,
    similarity: c.similarity || 0,
    confidence: c.confidence || 'N/A',
    module: c.module || 'Other',
    linked_change_requests: c.linked_change_requests || [],
    linked_brd_requirements: c.linked_brd_requirements || []
  }));

  const tabFiltered = rawItems.filter(item => {
    if (activeTab === 'all') return true;
    if (activeTab === 'drift') return ['Modified', 'Unchanged', 'Added', 'Removed'].includes(item.status);
    if (activeTab === 'cr') return item.relationship === 'AFFECTS' || (item.linked_change_requests && item.linked_change_requests.length > 0);
    if (activeTab === 'brd') return item.relationship === 'TRACEABLE_TO' || (item.linked_brd_requirements && item.linked_brd_requirements.length > 0);
    return true;
  });

  const sortedItems = [...tabFiltered].sort((a, b) => {
    let aVal = a[sortConfig.key] ?? '';
    let bVal = b[sortConfig.key] ?? '';
    if (typeof aVal === 'string') aVal = aVal.toLowerCase();
    if (typeof bVal === 'string') bVal = bVal.toLowerCase();

    if (aVal < bVal) return sortConfig.direction === 'ascending' ? -1 : 1;
    if (aVal > bVal) return sortConfig.direction === 'ascending' ? 1 : -1;
    return 0;
  });

  const filteredItems = sortedItems.filter((item) => {
    const term = filter.toLowerCase();
    const reqText = (item.text || "").toLowerCase();
    const idText = (item.req_id || "").toLowerCase();
    const srcDoc = (item.source_document || "").toLowerCase();
    const matchDoc = (item.matched_document || "").toLowerCase();
    const matchId = (item.matched_req_id || "").toLowerCase();
    const relText = (item.relationship || "").toLowerCase();
    return reqText.includes(term) || idText.includes(term) || srcDoc.includes(term) || matchDoc.includes(term) || matchId.includes(term) || relText.includes(term);
  });

  const requestSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const getRelationshipBadge = (rel, status) => {
    switch (rel) {
      case 'SAME_REQUIREMENT':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold border bg-emerald-950/60 text-emerald-400 border-emerald-800">SAME_REQUIREMENT</span>;
      case 'MODIFIED_FROM':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold border bg-amber-950/60 text-amber-400 border-amber-800">MODIFIED_FROM</span>;
      case 'ADDED_IN':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold border bg-blue-950/60 text-blue-400 border-blue-800">ADDED_IN</span>;
      case 'REMOVED_FROM':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold border bg-red-950/60 text-red-400 border-red-800">REMOVED_FROM</span>;
      case 'AFFECTS':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold border bg-purple-950/60 text-purple-300 border-purple-800">AFFECTS</span>;
      case 'TRACEABLE_TO':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold border bg-cyan-950/60 text-cyan-300 border-cyan-800">TRACEABLE_TO</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-bold border bg-slate-800 text-slate-300 border-slate-700">{status || rel}</span>;
    }
  };

  const getConfidenceBadge = (conf) => {
    switch (conf) {
      case 'Very High':
      case 'High':
        return <span className="text-emerald-400 font-semibold text-xs">{conf}</span>;
      case 'Medium':
        return <span className="text-amber-400 font-semibold text-xs">{conf}</span>;
      case 'Low':
        return <span className="text-red-400 font-semibold text-xs">{conf}</span>;
      case 'New Requirement':
        return <span className="text-blue-400 font-semibold text-xs">New</span>;
      default:
        return <span className="text-slate-400 text-xs">{conf || '—'}</span>;
    }
  };

  return (
    <div className="glass-card p-6 border-t-4 border-slate-700 break-inside-avoid mt-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
        <div className="flex items-center gap-2">
          <Table className="w-5 h-5 text-neon-blue" />
          <div>
            <h3 className="text-lg font-bold text-slate-100">Cross-Document Traceability Matrix</h3>
            <p className="text-xs text-slate-400">Provenance tracking across all uploaded baseline and updated documents</p>
          </div>
        </div>
        <div className="relative w-full sm:w-64 print:hidden">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search matrix, doc, or ID..." 
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-700 text-sm focus:ring-2 focus:ring-primary-500 outline-none bg-slate-900/80 text-slate-200"
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-4 border-b border-slate-800 pb-3 print:hidden">
        <button
          onClick={() => setActiveTab('all')}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${activeTab === 'all' ? 'bg-primary-600 text-white shadow-sm' : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800'}`}
        >
          All Records ({rawItems.length})
        </button>
        <button
          onClick={() => setActiveTab('drift')}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${activeTab === 'drift' ? 'bg-primary-600 text-white shadow-sm' : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800'}`}
        >
          Requirement Drift
        </button>
        <button
          onClick={() => setActiveTab('cr')}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${activeTab === 'cr' ? 'bg-purple-600 text-white shadow-sm' : 'bg-slate-800/60 text-purple-300 hover:bg-slate-800'}`}
        >
          Change Request Links (AFFECTS)
        </button>
        <button
          onClick={() => setActiveTab('brd')}
          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${activeTab === 'brd' ? 'bg-cyan-600 text-white shadow-sm' : 'bg-slate-800/60 text-cyan-300 hover:bg-slate-800'}`}
        >
          BRD Traceability (TRACEABLE_TO)
        </button>
      </div>

      <div className="overflow-x-auto overflow-y-auto max-h-[520px] rounded-xl border border-slate-700 shadow-sm custom-scrollbar glass-card">
        <table className="w-full text-left border-collapse text-sm relative">
          <thead className="sticky top-0 z-10 shadow-sm">
            <tr className="bg-slate-800 text-slate-300 uppercase tracking-wider text-xs font-semibold">
              <th className="p-3 cursor-pointer hover:bg-slate-700/50 transition-colors whitespace-nowrap" onClick={() => requestSort('req_id')}>
                <div className="flex items-center gap-1">Req ID <ArrowUpDown className="w-3 h-3 text-slate-400" /></div>
              </th>
              <th className="p-3 cursor-pointer hover:bg-slate-700/50 transition-colors whitespace-nowrap" onClick={() => requestSort('source_document')}>
                <div className="flex items-center gap-1">Source Document <ArrowUpDown className="w-3 h-3 text-slate-400" /></div>
              </th>
              <th className="p-3">Requirement Text</th>
              <th className="p-3 cursor-pointer hover:bg-slate-700/50 transition-colors whitespace-nowrap" onClick={() => requestSort('matched_document')}>
                <div className="flex items-center gap-1">Matched Target <ArrowUpDown className="w-3 h-3 text-slate-400" /></div>
              </th>
              <th className="p-3 cursor-pointer hover:bg-slate-700/50 transition-colors whitespace-nowrap" onClick={() => requestSort('relationship')}>
                <div className="flex items-center gap-1">Relationship <ArrowUpDown className="w-3 h-3 text-slate-400" /></div>
              </th>
              <th className="p-3 cursor-pointer hover:bg-slate-700/50 transition-colors whitespace-nowrap" onClick={() => requestSort('similarity')}>
                <div className="flex items-center gap-1">Similarity <ArrowUpDown className="w-3 h-3 text-slate-400" /></div>
              </th>
              <th className="p-3 whitespace-nowrap">Confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {filteredItems.map((item, i) => (
              <tr 
                key={i} 
                onClick={() => onRowClick && onRowClick(item.req_id)}
                className={`cursor-pointer ${i % 2 === 0 ? 'bg-slate-900/50' : 'bg-slate-800/30'} hover:bg-slate-700/70 transition-all duration-200`}
              >
                <td className="p-3 font-mono text-xs font-bold text-slate-200 whitespace-nowrap align-middle">
                  <span className="bg-slate-950 px-2.5 py-1 rounded border border-slate-700 inline-block shadow-sm">
                    {item.req_id}
                  </span>
                </td>
                <td className="p-3 text-xs text-slate-300 whitespace-nowrap align-middle">
                  <div className="flex items-center gap-1.5 font-mono text-[11px] bg-slate-950/70 px-2 py-1 rounded border border-slate-800 max-w-[180px] truncate" title={item.source_document}>
                    <FileText className="w-3 h-3 text-primary-400 shrink-0" />
                    <span className="truncate">{item.source_document || '—'}</span>
                  </div>
                </td>
                <td className="p-3 text-slate-200 align-middle">
                  <div className="max-w-[180px] sm:max-w-xs md:max-w-sm truncate text-xs font-medium" title={item.text}>
                    {item.text || '—'}
                  </div>
                  {item.linked_change_requests && item.linked_change_requests.length > 0 && (
                    <div className="mt-1 flex flex-wrap gap-1">
                      {item.linked_change_requests.map((cr, idx) => (
                        <span key={idx} className="text-[10px] bg-purple-950 text-purple-300 border border-purple-800 px-1.5 py-0.5 rounded font-mono">
                          ⚡ Affected by {cr.cr_id} ({Math.round(cr.similarity * 100)}%)
                        </span>
                      ))}
                    </div>
                  )}
                  {item.linked_brd_requirements && item.linked_brd_requirements.length > 0 && (
                    <div className="mt-1 flex flex-wrap gap-1">
                      {item.linked_brd_requirements.map((brd, idx) => (
                        <span key={idx} className="text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800 px-1.5 py-0.5 rounded font-mono">
                          🔗 Traced from {brd.brd_id} ({Math.round(brd.similarity * 100)}%)
                        </span>
                      ))}
                    </div>
                  )}
                </td>
                <td className="p-3 text-xs text-slate-300 whitespace-nowrap align-middle">
                  {item.matched_document ? (
                    <div className="flex items-center gap-1 font-mono text-[11px]">
                      <span className="font-bold text-slate-200">{item.matched_req_id || item.req_id}</span>
                      <span className="text-slate-500">in</span>
                      <span className="text-slate-400 max-w-[120px] truncate" title={item.matched_document}>{item.matched_document}</span>
                    </div>
                  ) : (
                    <span className="text-slate-500 italic text-xs">— None —</span>
                  )}
                </td>
                <td className="p-3 align-middle whitespace-nowrap">
                  {getRelationshipBadge(item.relationship, item.status)}
                </td>
                <td className="p-3 font-extrabold text-slate-300 align-middle whitespace-nowrap">
                  {item.similarity > 0 ? `${Math.round(item.similarity * 100)}%` : '—'}
                </td>
                <td className="p-3 align-middle whitespace-nowrap">
                  {getConfidenceBadge(item.confidence)}
                </td>
              </tr>
            ))}
            {filteredItems.length === 0 && (
              <tr>
                <td colSpan="7" className="p-8 text-center text-slate-400 font-medium">No matching traceability records found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
