import { motion } from 'framer-motion';
import { CheckCircle2, AlertCircle, PlusCircle, XCircle, ArrowRight, Lightbulb, Award, Zap, AlertTriangle, MessageSquareWarning, Layers, Clock, GitBranch, Link2, GitPullRequest } from 'lucide-react';

export default function DiffCard({ change, index }) {
  const { 
    req_id, old: oldText, new: newText, status, similarity, module, risk, 
    confidence, quality, priority, complexity, recommendations, detected_changes, 
    engineering_impact, baseline_source, updated_source, relationship,
    linked_change_requests, linked_brd_requirements 
  } = change;

  const getStatusConfig = () => {
    switch (status) {
      case 'Unchanged':
        return { color: 'text-emerald-400', bg: 'bg-emerald-900/40', border: 'border-emerald-900', icon: <CheckCircle2 className="w-5 h-5" /> };
      case 'Modified':
        return { color: 'text-amber-400', bg: 'bg-amber-900/40', border: 'border-amber-900', icon: <AlertCircle className="w-5 h-5" /> };
      case 'Added':
        return { color: 'text-primary-400', bg: 'bg-primary-900/40', border: 'border-primary-900', icon: <PlusCircle className="w-5 h-5" /> };
      case 'Removed':
        return { color: 'text-red-400', bg: 'bg-red-900/40', border: 'border-red-900', icon: <XCircle className="w-5 h-5" /> };
      default:
        return { color: 'text-slate-400', bg: 'bg-slate-800', border: 'border-slate-700', icon: null };
    }
  };

  const getConfidenceColor = (conf) => {
    switch (conf) {
      case 'Very High': return 'text-emerald-400 bg-emerald-950/40 border-emerald-900/50';
      case 'High': return 'text-blue-400 bg-blue-950/40 border-blue-900/50';
      case 'Medium': return 'text-amber-400 bg-amber-950/40 border-amber-900/50';
      case 'Low': return 'text-red-400 bg-red-950/40 border-red-900/50';
      default: return 'text-slate-400 bg-slate-900/40 border-slate-800';
    }
  };
  
  const getPriorityColor = (pri) => {
    switch(pri) {
      case 'Must Have': return 'bg-purple-900/40 text-purple-400 border-purple-900';
      case 'Should Have': return 'bg-indigo-900/40 text-indigo-400 border-indigo-900';
      case 'Could Have': return 'bg-cyan-900/40 text-cyan-400 border-cyan-900';
      default: return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  const getSimilarityBadge = (sim) => {
    if (!sim) return <span className="text-slate-400 font-bold">—</span>;
    const val = Math.round(sim * 100);
    let colorClass = "bg-red-950/40 text-red-400 border-red-900/50";
    if (val >= 95) colorClass = "bg-emerald-950/40 text-emerald-400 border-emerald-900/50";
    else if (val >= 75) colorClass = "bg-blue-950/40 text-blue-400 border-blue-900/50";
    else if (val >= 50) colorClass = "bg-orange-950/40 text-orange-400 border-orange-900/50";
    
    return <span className={`px-3 py-1 rounded-full border text-sm font-extrabold shadow-sm ${colorClass}`}>{val}%</span>;
  };

  const config = getStatusConfig();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ delay: index * 0.05, duration: 0.4, ease: "easeOut" }}
      whileHover={{ y: -2, shadow: "0 10px 15px -3px rgba(0, 0, 0, 0.05)" }}
      className={`relative rounded-2xl p-6 border border-slate-800 shadow-sm border-l-4 ${config.border} mb-6 hover:shadow-xl hover:border-neon-blue/50 transition-all duration-300 group glass-card`}
    >
      <div className="flex justify-between items-start mb-6 border-b border-slate-800 pb-4">
        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
          <span className="font-mono text-sm font-extrabold text-slate-200 bg-slate-950 px-3 py-1 rounded-lg border border-slate-700 shadow-sm mr-1 group-hover:bg-slate-800 transition-colors">
            {req_id}
          </span>
          <div className={`px-3 py-1 rounded-full flex items-center gap-1.5 text-xs font-bold shadow-sm ${config.bg} ${config.color}`}>
            {config.icon}
            {status}
          </div>
          {module && (
            <span className="text-xs font-bold bg-slate-950 text-slate-400 px-3 py-1 rounded-full border border-slate-700 shadow-sm">
              {module}
            </span>
          )}
          {priority && (
            <span className={`text-xs font-bold px-3 py-1 rounded-full border shadow-sm ${getPriorityColor(priority)}`}>
              {priority}
            </span>
          )}
          {complexity && (
            <span className="text-xs font-bold px-3 py-1 rounded-full border bg-slate-950 text-slate-400 flex items-center gap-1.5 shadow-sm">
              <Zap className="w-3 h-3 text-amber-500" /> {complexity} Complexity
            </span>
          )}
          {quality?.score !== undefined && (
            <div className="relative group/tooltip">
              <span className={`cursor-help text-xs font-bold px-3 py-1 rounded-full border flex items-center gap-1.5 shadow-sm ${quality.score >= 90 ? 'bg-emerald-950/40 text-emerald-400 border-emerald-900/50' : quality.score >= 70 ? 'bg-amber-950/40 text-amber-400 border-amber-900/50' : 'bg-red-950/40 text-red-400 border-red-900/50'}`}>
                <Award className="w-3 h-3" /> Q: {quality.score}/100
              </span>
              <div className="absolute top-full mt-2 left-0 w-48 p-3 bg-slate-800 text-slate-100 text-[10px] rounded-lg opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all z-20 shadow-xl border border-slate-700">
                <div className="font-bold mb-1 border-b border-slate-600 pb-1 text-slate-300 uppercase tracking-widest">Quality Factors</div>
                <ul className="space-y-1.5 mt-2 font-medium">
                  <li className="flex justify-between items-center"><span>Grammar/Passive</span> <span className="text-emerald-400">Pass</span></li>
                  <li className="flex justify-between items-center"><span>Atomicity</span> <span className={quality.atomic ? 'text-emerald-400' : 'text-amber-400'}>{quality.atomic ? 'Pass' : 'Fail'}</span></li>
                  <li className="flex justify-between items-center"><span>Ambiguity</span> <span className={quality.ambiguous_words?.length === 0 ? 'text-emerald-400' : 'text-amber-400'}>{quality.ambiguous_words?.length || 0} issues</span></li>
                </ul>
              </div>
            </div>
          )}
          {confidence && (
            <div className="relative group/conf inline-block">
              <span className={`text-xs font-bold px-3 py-1 rounded-full border flex items-center gap-1.5 shadow-sm ${change.similarity_breakdown ? 'cursor-help' : ''} ${getConfidenceColor(confidence)}`}>
                {confidence} Match Confidence
              </span>
              {change.similarity_breakdown && (
                <div className="absolute top-full mt-2 left-0 w-56 p-3 bg-slate-800 text-slate-100 text-[10px] rounded-lg opacity-0 invisible group-hover/conf:opacity-100 group-hover/conf:visible transition-all z-20 shadow-xl border border-slate-700 text-left">
                  <div className="font-bold mb-1 border-b border-slate-600 pb-1 text-slate-300 uppercase tracking-widest">Confidence Score Basis</div>
                  <ul className="space-y-1.5 mt-2 font-medium">
                    <li className="flex justify-between items-center"><span>Semantic Similarity</span> <span className="text-emerald-400">{Math.round(change.similarity_breakdown.semantic * 100)}%</span></li>
                    <li className="flex justify-between items-center"><span>Keyword Overlap</span> <span className="text-emerald-400">{Math.round(change.similarity_breakdown.keyword * 100)}%</span></li>
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="text-right hidden sm:block pl-4 relative group/sim">
          <div className="text-xs text-slate-400 font-bold uppercase tracking-widest mb-1.5">Similarity</div>
          <div className="cursor-help inline-block">{getSimilarityBadge(similarity)}</div>
          
          <div className="absolute right-0 top-full mt-2 w-56 p-3 bg-slate-800 text-slate-100 text-[10px] rounded-lg opacity-0 invisible group-hover/sim:opacity-100 group-hover/sim:visible transition-all z-20 shadow-xl border border-slate-700 text-left font-normal">
            <div className="font-bold mb-1 border-b border-slate-600 pb-1 text-slate-300 uppercase tracking-widest">Similarity Basis</div>
            <p className="text-slate-300 mb-2 italic">Calculated using TF-IDF cosine similarity & Jaccard token overlap.</p>
            {change.similarity_breakdown && (
              <ul className="space-y-1.5 mt-2 font-medium border-t border-slate-700 pt-2">
                <li className="flex justify-between items-center"><span>Semantic Match</span> <span className="font-bold text-primary-400">{Math.round(change.similarity_breakdown.semantic * 100)}%</span></li>
                <li className="flex justify-between items-center"><span>Keyword Match</span> <span className="font-bold text-primary-400">{Math.round(change.similarity_breakdown.keyword * 100)}%</span></li>
                <li className="flex justify-between items-center border-t border-slate-700 pt-1 mt-1"><span>Overall Match</span> <span className="font-extrabold text-amber-400">{Math.round(change.similarity_breakdown.overall * 100)}%</span></li>
              </ul>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-6 items-center mb-6 relative">
        {/* Old Requirement (Baseline) */}
        <div className={`p-5 rounded-2xl transition-all ${status === 'Added' ? 'bg-slate-900/30 border border-slate-800/50 opacity-60' : 'bg-red-950/20 border border-red-900/40 shadow-[inset_0_0_20px_rgba(153,27,27,0.1)] hover:border-red-500/50 hover:bg-red-950/30'}`}>
          <div className={`text-xs font-bold mb-2 uppercase tracking-widest flex items-center gap-2 ${status === 'Added' ? 'text-slate-500' : 'text-red-400'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${status === 'Added' ? 'bg-slate-500' : 'bg-red-500 animate-pulse'}`}></span> Baseline
            {baseline_source && <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-0.5 rounded ml-auto normal-case tracking-normal border border-slate-700" title={baseline_source}>Source: {baseline_source}</span>}
          </div>
          <p className={`text-sm font-medium leading-relaxed ${status === 'Added' ? 'text-slate-500 italic' : 'text-slate-200'}`}>
            {oldText || "New capability introduced in updated documents. No corresponding requirement exists in baseline documents."}
          </p>
        </div>

        {/* Arrow */}
        <div className="hidden md:flex justify-center items-center text-slate-500 bg-slate-900/50 w-10 h-10 rounded-full border border-slate-800 shadow-lg z-10">
          <ArrowRight className="w-5 h-5" />
        </div>

        {/* New Requirement (Updated) */}
        <div className={`p-5 rounded-2xl transition-all ${status === 'Removed' ? 'bg-slate-900/30 border border-slate-800/50 opacity-60' : 'bg-emerald-950/20 border border-emerald-900/40 shadow-[inset_0_0_20px_rgba(6,78,59,0.1)] hover:border-emerald-500/50 hover:bg-emerald-950/30'}`}>
          <div className={`text-xs font-bold mb-2 uppercase tracking-widest flex items-center gap-2 ${status === 'Removed' ? 'text-slate-500' : 'text-emerald-400'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${status === 'Removed' ? 'bg-slate-500' : 'bg-emerald-500 animate-pulse'}`}></span> Updated
            {updated_source && <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-0.5 rounded ml-auto normal-case tracking-normal border border-slate-700" title={updated_source}>Source: {updated_source}</span>}
          </div>
          <p className={`text-sm font-medium leading-relaxed ${status === 'Removed' ? 'text-slate-500 italic' : 'text-slate-200'}`}>
            {newText || "— Requirement removed —"}
          </p>
        </div>
      </div>

      {/* Cross-Document Links (Change Request / BRD) */}
      {((linked_change_requests && linked_change_requests.length > 0) || (linked_brd_requirements && linked_brd_requirements.length > 0)) && (
        <div className="mb-4 bg-slate-950/80 rounded-xl p-3 border border-slate-800 flex flex-wrap gap-3 items-center">
          <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Link2 className="w-3.5 h-3.5 text-neon-blue" /> Cross-Document Links:
          </div>
          {linked_change_requests?.map((cr, i) => (
            <span key={`cr-${i}`} className="text-xs bg-purple-950/80 text-purple-300 border border-purple-800 px-2.5 py-1 rounded-lg font-mono flex items-center gap-1 shadow-sm">
              <GitPullRequest className="w-3 h-3 text-purple-400" /> Affected by {cr.cr_id} in {cr.cr_doc} ({Math.round(cr.similarity * 100)}%)
            </span>
          ))}
          {linked_brd_requirements?.map((brd, i) => (
            <span key={`brd-${i}`} className="text-xs bg-cyan-950/80 text-cyan-300 border border-cyan-800 px-2.5 py-1 rounded-lg font-mono flex items-center gap-1 shadow-sm">
              <Layers className="w-3 h-3 text-cyan-400" /> Traced from {brd.brd_id} in {brd.brd_doc} ({Math.round(brd.similarity * 100)}%)
            </span>
          ))}
        </div>
      )}
      
      {/* Quality Warnings */}
      {quality?.ambiguous_words?.length > 0 && (
        <div className="mb-4 bg-amber-950/30 rounded-xl p-4 border border-amber-900">
          <h4 className="text-sm font-semibold text-amber-400 mb-1 flex items-center gap-2">
            <MessageSquareWarning className="w-4 h-4 text-amber-500" /> Ambiguous Language Detected
          </h4>
          <p className="text-xs text-amber-300 mb-2">The terms <strong>{quality.ambiguous_words.join(', ')}</strong> are highly subjective and unmeasurable.</p>
          <p className="text-xs text-amber-400 italic">Recommendation: Replace subjective adjectives with measurable metrics.</p>
        </div>
      )}
      
      <div className="grid md:grid-cols-2 gap-4 mb-4">
        {/* Detected Changes */}
        {status === 'Modified' && detected_changes && (
          <div className="bg-slate-950 rounded-xl p-4 border border-slate-700">
            <h4 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-amber-500" /> Change Insight
            </h4>
            <ul className="space-y-1 mb-2">
              {detected_changes.highlights.map((hl, i) => (
                <li key={i} className={`text-xs font-medium ${hl.startsWith('+') ? 'text-primary-400' : hl.startsWith('-') ? 'text-red-400' : 'text-emerald-400'}`}>
                  {hl}
                </li>
              ))}
            </ul>
            <div className="text-xs text-slate-400 italic">
              <span className="font-semibold not-italic text-slate-300">Reason:</span> {detected_changes.reason}
            </div>
          </div>
        )}
        
        {/* Recommendations */}
        {recommendations && status !== 'Removed' && (
          <div className="bg-indigo-950/30 rounded-xl p-4 border border-indigo-900">
            <h4 className="text-sm font-semibold text-indigo-400 mb-2 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-indigo-500" /> Engineering Recommendations
            </h4>
            <p className="text-xs text-indigo-200 mb-2 font-medium">{recommendations.review}</p>
            <div className="flex gap-2 mb-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">Components:</span>
              <span className="text-[10px] font-medium text-indigo-400">{recommendations.components.join(', ')}</span>
            </div>
            <div className="flex gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">Testing:</span>
              <span className="text-[10px] font-medium text-indigo-400">{recommendations.tests.join(', ')}</span>
            </div>
          </div>
        )}
      </div>

      {/* Engineering Impact & Architecture Analysis */}
      {engineering_impact && (
        <div className="mt-4 text-slate-100 rounded-xl p-5 border border-slate-800 shadow-lg glass-card">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-800">
            <h4 className="text-sm font-bold flex items-center gap-2 text-primary-400">
              <Layers className="w-4 h-4 text-primary-400" /> Engineering Impact & Architecture Analysis
            </h4>
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-mono font-bold bg-slate-800 text-primary-300 px-3 py-1 rounded-lg border border-slate-700 flex items-center gap-1.5 shadow-sm">
                <Clock className="w-3.5 h-3.5 text-amber-400" /> {engineering_impact.story_points} Story Points
              </span>
              <span className="text-xs font-semibold bg-slate-800 text-slate-300 px-3 py-1 rounded-lg border border-slate-700 shadow-sm">
                Est: {engineering_impact.sprint_effort}
              </span>
              <span className={`text-xs font-bold px-3 py-1 rounded-lg border flex items-center gap-1 shadow-sm ${engineering_impact.backward_compatible ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800' : 'bg-red-950/80 text-red-300 border-red-800'}`}>
                {engineering_impact.backward_compatible ? '✓ Backward Compatible' : '⚠️ Breaking Change'}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-4">
            {Object.entries(engineering_impact.stars).map(([layer, count]) => (
              <div key={layer} className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60 text-center">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">{layer}</div>
                <div className="flex justify-center text-amber-400 text-xs tracking-tighter">
                  {"★".repeat(count)}{"☆".repeat(5 - count)}
                </div>
              </div>
            ))}
          </div>

          <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/80">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
              <GitBranch className="w-3.5 h-3.5 text-indigo-400" /> Architecture Dependency Graph
            </div>
            <div className="flex flex-wrap items-center gap-1.5 text-xs text-slate-200 font-mono">
              {engineering_impact.dependency_chain.map((comp, i) => (
                <span key={i} className="flex items-center gap-1.5">
                  <span className="bg-indigo-950/80 text-indigo-300 border border-indigo-800/80 px-2 py-0.5 rounded shadow-sm">
                    {comp}
                  </span>
                  {i < engineering_impact.dependency_chain.length - 1 && (
                    <span className="text-slate-400 font-bold">→</span>
                  )}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
