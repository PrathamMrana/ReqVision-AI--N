import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { 
  UploadCloud, FileText, CheckCircle, Search, Layers, Server, Activity, 
  ArrowRight, ShieldAlert, Sparkles, BrainCircuit, CheckCircle2, ChevronRight,
  Database, Network, GitPullRequest, ArrowLeft, Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import axios from 'axios';

export default function ProjectWorkspace() {
  const location = useLocation();
  const navigate = useNavigate();
  const [documents, setDocuments] = useState(location.state?.documents || []);
  const [isUploading, setIsUploading] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  
  useEffect(() => {
    if (location.state?.documents) {
      setDocuments(location.state.documents);
    }
  }, [location.state]);

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    
    setIsUploading(true);
    const toastId = toast.loading(`Ingesting and classifying ${files.length} project document(s)...`);
    
    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
      
      const apiUrl = import.meta.env?.VITE_API_URL || 'http://localhost:5001/api/compare';
      const detectUrl = apiUrl.replace('/api/compare', '/api/project/detect').replace('/compare', '/project/detect');

      const response = await axios.post(detectUrl, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (response.data.success && response.data.documents) {
        setDocuments(prev => [...prev, ...response.data.documents]);
        toast.success(`Classified ${response.data.documents.length} document(s)`, { id: toastId });
      } else {
        toast.error("Error analyzing documents", { id: toastId });
      }
    } catch (error) {
      console.error(error);
      toast.error("Failed to connect to backend", { id: toastId });
    } finally {
      setIsUploading(false);
    }
  };

  const handleGenerateMatrix = async () => {
    if (documents.length === 0) {
      toast.error("Please upload at least one project document.");
      return;
    }

    setIsVerifying(true);
    const toastId = toast.loading(`Generating Cross-Document Traceability Matrix for ${documents.length} documents...`);

    try {
      const apiUrl = import.meta.env?.VITE_API_URL || 'http://localhost:5001/api/compare';
      const verifyUrl = apiUrl.replace('/api/compare', '/api/project/verify').replace('/compare', '/project/verify');

      const response = await axios.post(verifyUrl, {
        documents: documents
      });

      toast.success("Traceability Matrix Generated!", { id: toastId });
      navigate('/dashboard', { state: { result: response.data } });
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.error || "Failed to generate cross-document matrix", { id: toastId });
    } finally {
      setIsVerifying(false);
    }
  };

  const getTypeBadgeStyle = (type) => {
    switch (type) {
      case 'BRD':
        return 'bg-amber-500/10 text-amber-300 border-amber-500/30';
      case 'SRS':
        return 'bg-blue-500/10 text-blue-300 border-blue-500/30';
      case 'FRD':
        return 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30';
      case 'User Story':
        return 'bg-purple-500/10 text-purple-300 border-purple-500/30';
      case 'Test Case':
        return 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
      case 'Change Request':
        return 'bg-rose-500/10 text-rose-300 border-rose-500/30';
      case 'Meeting Minutes':
        return 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30';
      case 'Release Notes':
        return 'bg-teal-500/10 text-teal-300 border-teal-500/30';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="min-h-screen bg-[#05050A] text-slate-100 font-sans p-6 sm:p-8 pt-24 overflow-hidden relative selection:bg-neon-blue/30 selection:text-white">
      {/* Ambient background glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[90vw] h-[60vw] bg-indigo-950/20 rounded-full blur-[140px] -z-10 pointer-events-none" />
      
      <div className="max-w-6xl mx-auto relative z-10">
        
        {/* Navigation Breadcrumb */}
        <div className="mb-8 flex items-center justify-between">
          <Link to="/" className="inline-flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-white transition-colors bg-slate-900/80 border border-slate-800 px-3.5 py-1.5 rounded-full">
            <ArrowLeft className="w-3.5 h-3.5 text-neon-blue" /> Back to Home
          </Link>
          <span className="text-xs font-mono font-bold text-neon-blue bg-neon-blue/10 border border-neon-blue/30 px-3 py-1 rounded-full">
            Phase 2: Project Intelligence
          </span>
        </div>

        {/* Page Header */}
        <div className="mb-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-neon-blue text-xs font-mono font-bold tracking-widest uppercase mb-3">
            <Layers className="w-3.5 h-3.5 text-amber-400" /> Unified Workspace
          </div>
          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight mb-3">
            Project Document <span className="text-gradient">Intelligence</span>
          </h1>
          <p className="text-slate-400 text-base sm:text-lg max-w-3xl font-medium">
            All project artifacts reside in a single unified collection with automated, filename-independent classification and modular artifact extraction.
          </p>
        </div>
        
        {/* Upload Dropzone */}
        <div className="relative group cursor-pointer w-full bg-slate-900/50 border-2 border-dashed border-slate-700/80 rounded-3xl p-8 sm:p-12 text-center hover:bg-slate-900/70 hover:border-neon-blue/60 transition-all duration-300 backdrop-blur-xl mb-12 shadow-2xl">
          <input 
            type="file" 
            multiple 
            accept=".txt,.pdf,.docx" 
            onChange={handleFileUpload} 
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
            disabled={isUploading || isVerifying}
          />
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-neon-blue/10 border border-neon-blue/30 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:shadow-[0_0_25px_var(--color-neon-blue)] transition-all">
              {isUploading ? (
                <Loader2 className="w-8 h-8 text-neon-blue animate-spin" />
              ) : (
                <UploadCloud className="w-8 h-8 text-neon-blue" />
              )}
            </div>
          </div>
          <h3 className="text-xl font-bold text-slate-100 mb-1">
            {isUploading ? "Ingesting & Classifying Documents..." : "Upload Project Documents"}
          </h3>
          <p className="text-xs sm:text-sm text-slate-400">
            Select multiple files simultaneously (.docx, .pdf, or .txt). Zero baseline vs. updated assumptions.
          </p>
        </div>
        
        {/* Document Cards List */}
        {documents.length > 0 ? (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2.5">
                <Database className="w-5 h-5 text-neon-blue" />
                Project Document Collection ({documents.length})
              </h2>
              <span className="text-xs font-mono font-bold text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1 rounded-full">
                Independent Modular Extraction
              </span>
            </div>
            
            <div className="grid gap-4">
              {documents.map((doc, idx) => (
                <motion.div 
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  key={doc.document_id || idx} 
                  className="bg-slate-950/80 border border-slate-800/90 rounded-2xl p-5 sm:p-6 hover:border-neon-blue/40 transition-all backdrop-blur-xl shadow-lg"
                >
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-center shadow-inner shrink-0">
                        <FileText className="w-6 h-6 text-neon-blue" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-slate-100">{doc.filename}</h3>
                        <div className="flex flex-wrap items-center gap-2 mt-1.5">
                          <span className={`text-xs font-mono font-extrabold border px-2.5 py-0.5 rounded-full ${getTypeBadgeStyle(doc.document_type)}`}>
                            {doc.document_type}
                          </span>
                          <span className="text-xs font-mono font-semibold text-slate-400 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-full">
                            Confidence: {doc.confidence_score}%
                          </span>
                          <span className="text-[10px] font-mono text-slate-500 uppercase">
                            ID: {doc.document_id?.substring(0, 8)}...
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3.5 flex gap-6 items-center min-w-[260px]">
                      <div>
                        <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-0.5">
                          Normalized Artifacts
                        </div>
                        <div className="text-xl font-black text-white">
                          {doc.artifact_label || `${doc.artifact_count || 0} Artifacts`}
                        </div>
                      </div>
                      <div className="w-[1px] h-8 bg-slate-800"></div>
                      <div>
                        <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-0.5">
                          Status
                        </div>
                        <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                          <CheckCircle className="w-3.5 h-3.5" /> Extracted & Ready
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Signals Matched */}
                  {doc.signals_matched && doc.signals_matched.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-900">
                      <div className="text-xs font-semibold text-slate-500 mb-2 flex items-center gap-1.5">
                        <Search className="w-3.5 h-3.5" /> Rule-based Classification Signals
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {doc.signals_matched.map((sig, i) => (
                          <span key={i} className="text-[10px] font-mono bg-slate-900/90 text-slate-400 px-2 py-0.5 rounded border border-slate-800">
                            {sig}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
            
            {/* Cross-Document Verification Action Card */}
            <div className="mt-10 p-6 sm:p-8 bg-indigo-950/30 border border-indigo-500/30 rounded-3xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 backdrop-blur-xl">
              <div>
                <h4 className="text-lg font-bold text-indigo-200 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-400" /> Cross-Document Semantic Verification
                </h4>
                <p className="text-sm text-indigo-300/80 mt-1 font-medium max-w-xl">
                  Construct bi-directional semantic mappings across BRD → SRS → FRD → User Stories → Test Cases with automated conflict and coverage verification.
                </p>
              </div>
              <button 
                onClick={handleGenerateMatrix}
                disabled={isVerifying}
                className="px-6 py-3.5 bg-neon-blue/15 hover:bg-neon-blue/25 text-white neon-border rounded-xl font-bold text-sm shadow-lg shadow-neon-glow hover:shadow-[0_0_20px_var(--color-neon-blue)] transition-all flex items-center gap-2 group shrink-0 disabled:opacity-50"
              >
                {isVerifying ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-neon-blue" />
                    <span>Generating Dashboard...</span>
                  </>
                ) : (
                  <>
                    <span>Generate Traceability Matrix</span>
                    <ArrowRight className="w-4 h-4 text-neon-blue group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          <div className="p-12 text-center bg-slate-950/60 border border-slate-800 rounded-3xl">
            <p className="text-slate-400 text-sm font-medium">
              No project documents loaded yet. Use the upload area above to ingest your project files.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
