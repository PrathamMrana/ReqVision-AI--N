import { Layers, Crosshair, AlertOctagon } from 'lucide-react';

export default function ImpactAnalysis({ impact_analysis }) {
  if (!impact_analysis) return null;
  const { impacted_modules, review_areas, testing_focus } = impact_analysis;

  return (
    <div className="glass-card p-6 mb-8 border-t-4 border-indigo-500 break-inside-avoid mt-8">
      <div className="flex items-center gap-2 mb-6">
        <Layers className="w-5 h-5 text-indigo-500" />
        <h3 className="text-lg font-bold text-slate-200">Impact Analysis</h3>
      </div>
      
      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-indigo-950/40 p-4 rounded-xl border border-indigo-900">
          <h4 className="text-sm font-bold text-indigo-900 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-500" /> Impacted Modules
          </h4>
          <ul className="space-y-2">
            {impacted_modules.map((mod, i) => (
              <li key={i} className="text-sm text-indigo-300 font-medium bg-slate-900 px-3 py-1.5 rounded-lg border border-indigo-900 shadow-sm">
                {mod}
              </li>
            ))}
            {impacted_modules.length === 0 && (
              <li className="text-sm text-indigo-400 italic">No significant module impact detected.</li>
            )}
          </ul>
        </div>

        <div className="bg-amber-950/40 p-4 rounded-xl border border-amber-900">
          <h4 className="text-sm font-bold text-amber-900 uppercase tracking-wider mb-3 flex items-center gap-2">
            <AlertOctagon className="w-4 h-4 text-amber-500" /> Recommended Review Areas
          </h4>
          <ul className="space-y-2">
            {review_areas.map((area, i) => (
              <li key={i} className="text-sm text-amber-300 font-medium bg-slate-900 px-3 py-1.5 rounded-lg border border-amber-900 shadow-sm leading-relaxed">
                {area}
              </li>
            ))}
            {review_areas.length === 0 && (
              <li className="text-sm text-amber-400 italic">No specific review areas flagged.</li>
            )}
          </ul>
        </div>

        <div className="bg-emerald-950/40 p-4 rounded-xl border border-emerald-900">
          <h4 className="text-sm font-bold text-emerald-900 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Crosshair className="w-4 h-4 text-emerald-500" /> Suggested Testing Focus
          </h4>
          <ul className="space-y-2">
            {testing_focus.map((test, i) => (
              <li key={i} className="text-sm text-emerald-300 font-medium bg-slate-900 px-3 py-1.5 rounded-lg border border-emerald-900 shadow-sm">
                {test}
              </li>
            ))}
            {testing_focus.length === 0 && (
              <li className="text-sm text-emerald-400 italic">No specific testing focus flagged.</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
