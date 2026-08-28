import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, ArrowRight, Loader2, X, Plus, Sparkles, Database, Layers, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

export default function UploadBox() {
  const [baselineDocs, setBaselineDocs] = useState([
    { 
      id: 'base-sample-1', 
      type: 'text', 
      name: 'SRS_v1.0_Master.txt', 
      content: `REQ-101: The system shall authenticate users via OAuth 2.0 with JWT tokens expiring in 3600 seconds.
REQ-102: The payment gateway shall process Visa, Mastercard, and American Express transactions with sub-2s latency.
REQ-103: All database records shall be encrypted at rest using AES-256 standards.
REQ-104: The system shall support up to 5,000 concurrent active WebSocket connections.` 
    }
  ]);
  
  const [updatedDocs, setUpdatedDocs] = useState([
    { 
      id: 'upd-sample-1', 
      type: 'text', 
      name: 'SRS_v2.0_Draft_CR.txt', 
      content: `REQ-101: The system shall authenticate users via OAuth 2.0 and SAML 2.0 SSO with JWT tokens expiring in 1800 seconds and mandatory MFA.
REQ-102: The payment gateway shall process Visa, Mastercard, AMEX, and Stripe Direct with sub-1s latency and Apple Pay support.
REQ-103: All database records and cache layers shall be encrypted at rest using AES-256 and TLS 1.3 in transit.
REQ-104: The system shall support up to 25,000 concurrent active WebSocket connections with Redis clustering.
REQ-105: The system shall automatically stream audit logs to external SIEM systems via gRPC.` 
    }
  ]);
  
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleFileUpload = async (e, docs, setDocs) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    e.target.value = "";
    
    for (const file of files) {
      const ext = file.name.split('.').pop().toLowerCase();
      const id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
      
      if (ext === 'txt') {
        const reader = new FileReader();
        reader.onload = (ev) => {
          setDocs(prev => [...prev, { id, type: 'file', name: file.name, ext, content: ev.target.result }]);
          toast.success(`${file.name} loaded successfully`);
        };
        reader.readAsText(file);
      } else if (ext === 'pdf' || ext === 'docx') {
        const formData = new FormData();
        formData.append('file', file);
        
        const loadToast = toast.loading(`Extracting text from ${file.name}...`);
        
        try {
          const rawApiUrl = import.meta.env?.VITE_API_URL || 'http://localhost:5001/api/compare';
          let extractUrl = 'http://localhost:5001/api/extract-text';
          if (rawApiUrl.includes('/api/compare')) {
              extractUrl = rawApiUrl.replace('/api/compare', '/api/extract-text');
          } else if (rawApiUrl.endsWith('/api')) {
              extractUrl = rawApiUrl + '/extract-text';
          }
          const response = await axios.post(extractUrl, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          if (response.data.success) {
            setDocs(prev => [...prev, { id, type: 'file', name: file.name, ext, content: response.data.text }]);
            toast.success(`${file.name} extracted successfully`, { id: loadToast });
          } else {
            toast.error(`Failed to extract text from ${file.name}`, { id: loadToast });
          }
        } catch (err) {
          console.error(err);
          const errMsg = err.response?.data?.error || err.message;
          toast.error(`Parse Error (${file.name}): ${errMsg}`, { id: loadToast });
        }
      } else {
        toast.error(`Skipped ${file.name}: Only .txt, .pdf, or .docx supported`);
      }
    }
  };

  const addTextDoc = (setDocs) => {
    setDocs(prev => [...prev, { id: Date.now().toString() + Math.random().toString(36).substr(2, 9), type: 'text', name: 'Requirement_Specification.txt', content: '' }]);
  };

  const removeDoc = (id, setDocs) => {
    setDocs(prev => prev.filter(d => d.id !== id));
  };

  const updateTextDoc = (id, content, setDocs) => {
    setDocs(prev => prev.map(d => d.id === id ? { ...d, content } : d));
  };

  const handleCompare = async () => {
    const validBaseline = baselineDocs.filter(d => d.type === 'file' || (d.type === 'text' && d.content.trim()));
    const validUpdated = updatedDocs.filter(d => d.type === 'file' || (d.type === 'text' && d.content.trim()));

    if (validBaseline.length === 0 || validUpdated.length === 0) {
      toast.error('Please provide at least one Baseline and one Updated document.');
      return;
    }

    const baselinePayload = validBaseline.map(d => ({ name: d.name, text: d.content }));
    const updatedPayload = validUpdated.map(d => ({ name: d.name, text: d.content }));

    setLoading(true);
    try {
      const apiUrl = import.meta.env?.VITE_API_URL || 'http://localhost:5001/api/compare';
      const response = await axios.post(apiUrl, {
        baseline: baselinePayload,
        updated: updatedPayload
      });
      
      navigate('/dashboard', { state: { result: response.data } });
      toast.success('Analysis complete!');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to analyze requirements. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const renderDocList = (docs, setDocs, isBaseline) => (
    <div className="space-y-3 mt-3">
      {docs.map(doc => {
        if (doc.type === 'text') {
          return (
            <div key={doc.id} className="relative group rounded-2xl bg-slate-950/80 border border-slate-800 focus-within:border-neon-blue/60 transition-all p-3 shadow-inner">
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-900 text-xs font-mono text-slate-400">
                <span className="flex items-center gap-1.5 text-slate-300 font-semibold">
                  <FileText className={`w-3.5 h-3.5 ${isBaseline ? 'text-neon-blue' : 'text-indigo-400'}`} />
                  {doc.name}
                </span>
                {docs.length > 1 && (
                  <button 
                    onClick={() => removeDoc(doc.id, setDocs)}
                    className="p-1 hover:bg-red-500/20 text-slate-500 hover:text-red-400 rounded transition-all"
                    title="Remove item"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
              <textarea
                className="w-full h-36 bg-transparent text-slate-200 focus:outline-none resize-none font-mono text-xs sm:text-sm leading-relaxed"
                placeholder="Paste or type atomic requirements (e.g. REQ-101: The system shall...)"
                value={doc.content}
                onChange={(e) => updateTextDoc(doc.id, e.target.value, setDocs)}
              />
            </div>
          );
        } else {
          return (
            <div key={doc.id} className="flex items-center justify-between p-3.5 bg-slate-950/80 border border-slate-800 rounded-2xl shadow-sm">
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
                  <FileText className="w-4 h-4" />
                </div>
                <div className="overflow-hidden">
                  <span className="font-semibold text-slate-200 text-sm truncate block" title={doc.name}>{doc.name}</span>
                  <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Extracted & Ready
                  </span>
                </div>
              </div>
              <button 
                onClick={() => removeDoc(doc.id, setDocs)}
                className="p-1.5 hover:bg-red-500/20 text-slate-500 hover:text-red-400 rounded-lg transition-colors ml-2 shrink-0"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          );
        }
      })}
    </div>
  );

  return (
    <div className="w-full max-w-6xl mx-auto rounded-3xl bg-slate-900/60 border border-slate-800/90 shadow-2xl backdrop-blur-2xl p-6 sm:p-10 relative overflow-hidden">
      
      {/* Top Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-6 mb-8 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-neon-blue/10 border border-neon-blue/40 flex items-center justify-center shadow-lg shadow-neon-blue/20">
            <Database className="w-5 h-5 text-neon-blue" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">Intelligence Ingestion Engine</h3>
            <p className="text-xs text-slate-400">Multi-source comparison across Master baseline & Updated changes</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full bg-slate-950 border border-slate-800 text-[11px] font-mono font-semibold text-slate-400">
            Engine: TF-IDF · Scikit-Learn
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Baseline Input Column */}
        <div className="flex flex-col justify-between p-6 rounded-2xl bg-slate-950/50 border border-slate-800/80">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-neon-blue shadow-[0_0_8px_var(--color-neon-blue)]"></span>
                <h4 className="text-slate-100 font-bold text-base">Baseline Master Documents</h4>
              </div>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-neon-blue bg-neon-blue/10 border border-neon-blue/20 px-2 py-0.5 rounded-full">
                Source of Truth
              </span>
            </div>
            <p className="text-xs text-slate-400 mb-4">Original BRD, Master SRS, or Approved Specifications</p>
            
            <div className="max-h-[420px] overflow-y-auto pr-1">
              {renderDocList(baselineDocs, setBaselineDocs, true)}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 mt-5 pt-4 border-t border-slate-900">
            <label className="flex-1 flex items-center justify-center gap-2 h-11 border border-dashed border-slate-700 hover:border-neon-blue/60 rounded-xl cursor-pointer bg-slate-900/60 hover:bg-slate-800/80 transition-all text-xs font-bold text-slate-300">
              <UploadCloud className="w-4 h-4 text-neon-blue" />
              Upload (.txt, .pdf, .docx)
              <input type="file" multiple className="hidden" accept=".txt,.pdf,.docx" onChange={(e) => handleFileUpload(e, baselineDocs, setBaselineDocs)} />
            </label>
            <button 
              onClick={() => addTextDoc(setBaselineDocs)}
              className="flex items-center justify-center gap-1.5 px-4 h-11 border border-slate-800 hover:border-slate-700 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 transition-all text-xs font-bold text-slate-300"
            >
              <Plus className="w-4 h-4 text-slate-400" />
              Add Text
            </button>
          </div>
        </div>

        {/* Updated Input Column */}
        <div className="flex flex-col justify-between p-6 rounded-2xl bg-slate-950/50 border border-slate-800/80">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-400 shadow-[0_0_8px_rgba(129,140,248,0.8)]"></span>
                <h4 className="text-slate-100 font-bold text-base">Updated / Proposed Documents</h4>
              </div>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-indigo-300 bg-indigo-950/60 border border-indigo-500/30 px-2 py-0.5 rounded-full">
                Delta Candidate
              </span>
            </div>
            <p className="text-xs text-slate-400 mb-4">New Version Drafts, Client Change Requests, or User Stories</p>
            
            <div className="max-h-[420px] overflow-y-auto pr-1">
              {renderDocList(updatedDocs, setUpdatedDocs, false)}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 mt-5 pt-4 border-t border-slate-900">
            <label className="flex-1 flex items-center justify-center gap-2 h-11 border border-dashed border-slate-700 hover:border-indigo-400/60 rounded-xl cursor-pointer bg-slate-900/60 hover:bg-slate-800/80 transition-all text-xs font-bold text-slate-300">
              <UploadCloud className="w-4 h-4 text-indigo-400" />
              Upload (.txt, .pdf, .docx)
              <input type="file" multiple className="hidden" accept=".txt,.pdf,.docx" onChange={(e) => handleFileUpload(e, updatedDocs, setUpdatedDocs)} />
            </label>
            <button 
              onClick={() => addTextDoc(setUpdatedDocs)}
              className="flex items-center justify-center gap-1.5 px-4 h-11 border border-slate-800 hover:border-slate-700 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 transition-all text-xs font-bold text-slate-300"
            >
              <Plus className="w-4 h-4 text-slate-400" />
              Add Text
            </button>
          </div>
        </div>

      </div>

      {/* Action Footer */}
      <div className="mt-8 pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs text-slate-400 font-medium">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Multi-Document Pre-Loaded Demo Ready</span>
        </div>

        <button
          onClick={handleCompare}
          disabled={loading}
          className="w-full sm:w-auto px-8 py-3.5 bg-neon-blue/15 hover:bg-neon-blue/25 text-white neon-border rounded-xl font-bold text-base shadow-xl shadow-neon-glow hover:shadow-[0_0_25px_var(--color-neon-blue)] transition-all flex items-center justify-center gap-2 group disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Executing Software Intelligence Audit...
            </>
          ) : (
            <>
              <span>Run Intelligence Analysis</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-neon-blue" />
            </>
          )}
        </button>
      </div>

    </div>
  );
}
