import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, ArrowRight, Loader2, X, Plus } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

export default function UploadBox() {
  const [baselineDocs, setBaselineDocs] = useState([{ id: Date.now().toString(), type: 'text', name: 'Text Input', content: '' }]);
  const [updatedDocs, setUpdatedDocs] = useState([{ id: (Date.now()+1).toString(), type: 'text', name: 'Text Input', content: '' }]);
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
    setDocs(prev => [...prev, { id: Date.now().toString() + Math.random().toString(36).substr(2, 9), type: 'text', name: 'Text Input', content: '' }]);
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

    // Updated API expects array of documents with names
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

  const renderDocList = (docs, setDocs) => (
    <div className="space-y-3 mt-4">
      {docs.map(doc => {
        if (doc.type === 'text') {
          return (
            <div key={doc.id} className="relative group">
              <textarea
                className="w-full h-40 p-4 border border-slate-700 rounded-xl bg-slate-900/50 focus:bg-slate-900 focus:shadow-[0_0_15px_rgba(0,243,255,0.2)] focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all outline-none resize-none font-mono text-sm"
                placeholder="Paste original requirements here..."
                value={doc.content}
                onChange={(e) => updateTextDoc(doc.id, e.target.value, setDocs)}
              />
              <button 
                onClick={() => removeDoc(doc.id, setDocs)}
                className="absolute top-2 right-2 p-1.5 bg-slate-800/80 hover:bg-red-500/20 text-slate-400 hover:text-red-400 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                title="Remove text area"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          );
        } else {
          return (
            <div key={doc.id} className="flex items-center justify-between p-4 bg-slate-900/50 border border-slate-700 rounded-xl shadow-sm">
              <div className="flex items-center gap-3 overflow-hidden">
                <FileText className="w-5 h-5 text-emerald-500 shrink-0" />
                <span className="font-medium text-slate-200 truncate" title={doc.name}>{doc.name}</span>
                <span className="text-xs font-bold px-2 py-0.5 bg-slate-800 text-slate-400 rounded uppercase shrink-0">
                  {doc.ext}
                </span>
                <span className="text-xs font-medium text-emerald-400 flex items-center gap-1 shrink-0">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div> Ready
                </span>
              </div>
              <button 
                onClick={() => removeDoc(doc.id, setDocs)}
                className="p-1.5 hover:bg-red-500/20 text-slate-400 hover:text-red-400 rounded-lg transition-colors ml-2 shrink-0"
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
    <div className="w-full max-w-5xl mx-auto mt-12 glass-panel p-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Baseline Input */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-slate-200 font-semibold text-lg">
            <FileText className="text-primary-500" />
            <h3>Baseline Documents</h3>
          </div>
          <p className="text-xs text-slate-400 mb-2">Upload or paste one or more baseline project documents</p>
          
          <div className="max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
            {renderDocList(baselineDocs, setBaselineDocs)}
          </div>

          <div className="flex flex-col sm:flex-row gap-3 mt-4">
            <label className="flex-1 flex items-center justify-center gap-2 h-12 border border-dashed border-slate-600 rounded-xl cursor-pointer bg-slate-900/30 hover:bg-slate-800 transition-colors text-sm text-slate-300 font-medium">
              <UploadCloud className="w-4 h-4" />
              Upload Files
              <input type="file" multiple className="hidden" accept=".txt,.pdf,.docx" onChange={(e) => handleFileUpload(e, baselineDocs, setBaselineDocs)} />
            </label>
            <button 
              onClick={() => addTextDoc(setBaselineDocs)}
              className="flex-1 flex items-center justify-center gap-2 h-12 border border-slate-700 rounded-xl bg-slate-900/30 hover:bg-slate-800 transition-colors text-sm text-slate-300 font-medium"
            >
              <Plus className="w-4 h-4" />
              Add another document
            </button>
          </div>
        </div>

        {/* Updated Input */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-slate-200 font-semibold text-lg">
            <FileText className="text-accent-500" />
            <h3>Updated Documents</h3>
          </div>
          <p className="text-xs text-slate-400 mb-2">Upload or paste one or more updated project documents</p>
          
          <div className="max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
            {renderDocList(updatedDocs, setUpdatedDocs)}
          </div>

          <div className="flex flex-col sm:flex-row gap-3 mt-4">
            <label className="flex-1 flex items-center justify-center gap-2 h-12 border border-dashed border-slate-600 rounded-xl cursor-pointer bg-slate-900/30 hover:bg-slate-800 transition-colors text-sm text-slate-300 font-medium">
              <UploadCloud className="w-4 h-4" />
              Upload Files
              <input type="file" multiple className="hidden" accept=".txt,.pdf,.docx" onChange={(e) => handleFileUpload(e, updatedDocs, setUpdatedDocs)} />
            </label>
            <button 
              onClick={() => addTextDoc(setUpdatedDocs)}
              className="flex-1 flex items-center justify-center gap-2 h-12 border border-slate-700 rounded-xl bg-slate-900/30 hover:bg-slate-800 transition-colors text-sm text-slate-300 font-medium"
            >
              <Plus className="w-4 h-4" />
              Add another document
            </button>
          </div>
        </div>

      </div>

      <div className="mt-10 flex justify-center">
        <button
          onClick={handleCompare}
          disabled={loading}
          className="flex items-center gap-3 bg-neon-blue/20 hover:bg-neon-blue/30 text-white neon-border px-10 py-4 rounded-full font-bold text-lg shadow-xl shadow-neon-glow hover:shadow-[0_0_30px_var(--color-neon-blue)] transition-all hover:-translate-y-1 disabled:opacity-70 disabled:hover:translate-y-0"
        >
          {loading ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              Analyzing Impact...
            </>
          ) : (
            <>
              Run AI Analysis
              <ArrowRight className="w-6 h-6" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
