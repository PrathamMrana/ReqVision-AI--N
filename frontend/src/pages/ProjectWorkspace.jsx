import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle, Search, Layers, Server, Activity, ArrowRight, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';

export default function ProjectWorkspace() {
  const [documents, setDocuments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  
  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    
    setIsUploading(true);
    
    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
      
      // Call backend Phase 1 API (multipart/form-data)
      const apiUrl = import.meta.env?.VITE_API_URL || 'http://localhost:5001/api';
      const response = await fetch(`${apiUrl.replace('/api', '')}/api/project/detect`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      if (data.success) {
        setDocuments(prev => [...prev, ...data.documents]);
      } else {
        alert("Error analyzing documents");
      }
    } catch (error) {
      console.error(error);
      alert("Failed to connect to backend");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020205] text-slate-200 font-sans p-8 pt-24 overflow-hidden relative">
      {/* Background glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[80vw] h-[50vw] bg-blue-900/10 rounded-full blur-[120px] -z-10 pointer-events-none" />
      
      <div className="max-w-6xl mx-auto relative z-10">
        <div className="mb-10">
          <h1 className="text-4xl font-black text-white tracking-tight mb-3">Multi-Document Intelligence</h1>
          <p className="text-slate-400 text-lg">Upload project documents. The AI engine automatically detects document types and normalizes artifacts.</p>
        </div>
        
        {/* Upload Zone */}
        <div className="relative group cursor-pointer w-full bg-slate-900/40 border border-slate-700/50 rounded-3xl p-12 text-center hover:bg-slate-900/60 transition-all duration-300 backdrop-blur-md mb-12 shadow-2xl">
          <input 
            type="file" 
            multiple 
            accept=".txt,.pdf,.docx" 
            onChange={handleFileUpload} 
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
            disabled={isUploading}
          />
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 bg-blue-500/10 rounded-full flex items-center justify-center group-hover:bg-blue-500/20 transition-colors">
              <UploadCloud className="w-10 h-10 text-blue-400" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-slate-100 mb-2">
            {isUploading ? "Analyzing Documents..." : "Upload Project Documents"}
          </h3>
          <p className="text-slate-400">Drag & drop PDF, DOCX, or TXT files here (Native Extraction)</p>
        </div>
        
        {/* Document List */}
        {documents.length > 0 && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <Layers className="w-6 h-6 text-blue-400" />
              Project Workspace
            </h2>
            
            <div className="grid gap-6">
              {documents.map((doc, idx) => (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  key={doc.document_id} 
                  className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 hover:border-blue-500/30 transition-all backdrop-blur-md"
                >
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 bg-slate-800 rounded-xl flex items-center justify-center shadow-inner">
                        <FileText className="w-7 h-7 text-indigo-400" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-slate-100">{doc.filename}</h3>
                        <div className="flex items-center gap-3 mt-1.5">
                          <span className="text-xs font-mono font-bold bg-blue-900/40 text-blue-300 border border-blue-800/50 px-2 py-0.5 rounded flex items-center gap-1.5">
                            <Server className="w-3.5 h-3.5" /> {doc.document_type}
                          </span>
                          <span className="text-xs font-semibold text-slate-400 flex items-center gap-1">
                            <Activity className="w-3.5 h-3.5" /> Confidence: {doc.confidence_score}%
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 flex gap-8 items-center min-w-[280px]">
                      <div>
                        <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Normalized Artifacts</div>
                        <div className="text-2xl font-black text-white">{doc.artifact_count}</div>
                      </div>
                      <div className="w-[1px] h-10 bg-slate-800"></div>
                      <div>
                        <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Status</div>
                        <div className="flex items-center gap-1.5 text-sm font-semibold text-emerald-400">
                          <CheckCircle className="w-4 h-4" /> Ready
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Signals Matched */}
                  {doc.signals_matched && doc.signals_matched.length > 0 && (
                    <div className="mt-5 pt-4 border-t border-slate-800/50">
                      <div className="text-xs font-semibold text-slate-500 mb-2 flex items-center gap-1.5">
                        <Search className="w-3.5 h-3.5" /> Rule-based Classification Signals
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {doc.signals_matched.map((sig, i) => (
                          <span key={i} className="text-[10px] font-medium bg-slate-800/60 text-slate-400 px-2 py-1 rounded border border-slate-700/50">
                            {sig}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
            
            <div className="mt-12 p-6 bg-indigo-950/20 border border-indigo-900/40 rounded-2xl flex items-center justify-between">
              <div>
                <h4 className="text-lg font-bold text-indigo-300 flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5" /> Phase 2: Cross-Document Traceability
                </h4>
                <p className="text-sm text-indigo-400/80 mt-1 font-medium">Verify consistency across these {documents.length} documents using Content-Based Mapping.</p>
              </div>
              <button disabled className="px-6 py-3 bg-indigo-900/50 text-indigo-400 font-bold rounded-xl border border-indigo-800/50 opacity-50 cursor-not-allowed flex items-center gap-2">
                Locked (Pending Phase 1 Approval) <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
