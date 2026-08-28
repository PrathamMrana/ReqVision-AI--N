import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  UploadCloud, FileText, ArrowRight, Loader2, X, Plus, Sparkles, Database, 
  Layers, CheckCircle2, ShieldCheck, Activity, BrainCircuit, GitPullRequest, 
  HelpCircle, RefreshCw, Server
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

// 7-Document Preset matching the User's Acceptance Scenario
const SAMPLE_7_DOCS = [
  {
    name: "01_BRD_Online_Library.docx",
    ext: "docx",
    text: `BUSINESS REQUIREMENTS DOCUMENT - ONLINE LIBRARY SYSTEM
BR-001: The system shall provide a unified online catalog for members to search, borrow, and renew digital books.
BR-002: The platform shall support automated late fee calculations and online payment settlement.
BR-003: The system must enforce role-based access control for Librarians, Members, and System Administrators.
BR-004: The platform shall generate monthly inventory and circulation reports for library management.`
  },
  {
    name: "02_SRS_Online_Library.docx",
    ext: "docx",
    text: `SOFTWARE REQUIREMENTS SPECIFICATION - ONLINE LIBRARY
REQ-101: The system shall authenticate users via OAuth 2.0 and email/password with JWT tokens expiring in 3600 seconds.
REQ-102: The search module shall index book metadata using Elasticsearch with sub-200ms query response.
REQ-103: The borrowing service shall verify user active loan quota before approving book checkout.
REQ-104: The payment gateway shall process Visa, Mastercard, and Stripe transactions with SSL encryption.
REQ-105: All database records shall be encrypted at rest using AES-256 standards.`
  },
  {
    name: "03_FRD_Online_Library.docx",
    ext: "docx",
    text: `FUNCTIONAL REQUIREMENTS DOCUMENT - CIRCULATION SUBSYSTEM
FR-201: The checkout workflow shall validate borrower membership status and outstanding fine balance.
FR-202: When a book is reserved, the inventory status shall transition from AVAILABLE to ON_HOLD.
FR-203: Automated reminder emails shall be dispatched 48 hours prior to the loan due date via SMTP.
FR-204: The system shall log all book status transitions to an immutable audit trail table.`
  },
  {
    name: "04_User_Stories_Online_Library.docx",
    ext: "docx",
    text: `USER STORIES - ONLINE LIBRARY SPRINT BACKLOG
US-301: As a Member, I want to search books by title, author, or ISBN so that I can quickly find my reading material.
US-302: As a Member, I want to renew my active loan online so that I avoid overdue penalties.
US-303: As a Librarian, I want to scan return barcodes so that books are returned to the catalog instantly.
US-304: As an Administrator, I want to export monthly circulation statistics as PDF reports.`
  },
  {
    name: "05_Test_Cases_Online_Library.docx",
    ext: "docx",
    text: `TEST SPECIFICATION - VERIFICATION & ASSURANCE
TC-401: Verify successful user login with valid credentials and verify JWT token generation in header.
TC-402: Verify search query execution under 200ms latency for catalog with 100,000 book records.
TC-403: Verify loan checkout rejection when member has more than $10.00 in outstanding fines.
TC-404: Verify automated due-date reminder email dispatch trigger 48 hours before expiry.`
  },
  {
    name: "06_Change_Request_Online_Library.docx",
    ext: "docx",
    text: `CHANGE REQUEST - CR-2026-08 (MANDATORY MFA & AUDIOBOOK INTEGRATION)
CR-501: Upgrade user authentication to enforce Multi-Factor Authentication (MFA) via TOTP for all Librarian and Admin logins.
CR-502: Extend search and borrow capabilities to support streaming Audiobook formats (.m4b, .mp3).
CR-503: Update payment gateway to support Apple Pay and Google Pay digital wallets.`
  },
  {
    name: "07_Meeting_Minutes_Online_Library.docx",
    ext: "docx",
    text: `MEETING MINUTES - ARCHITECTURE REVIEW BOARD
Date: August 28, 2026
Attendees: Lead Architect, Product Owner, QA Lead
MOM-601: Team agreed to prioritize CR-501 (MFA) in Sprint 14 to meet enterprise compliance guidelines.
MOM-602: QA lead confirmed TC-401 through TC-404 test coverage matrix is mapped to Master SRS.`
  }
];

export default function UploadBox() {
  // Mode selection: 'project' (Phase 2 Project Intelligence) vs 'version' (V1 Baseline/Updated Comparison)
  const [activeMode, setActiveMode] = useState('project');
  
  // Phase 2: Unified Project Document Collection
  const [projectDocs, setProjectDocs] = useState([]);
  const [isClassifying, setIsClassifying] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);

  // V1: Legacy Baseline vs Updated Documents
  const [baselineDocs, setBaselineDocs] = useState([{ id: 'b-1', type: 'text', name: 'SRS_v1.0_Master.txt', content: '' }]);
  const [updatedDocs, setUpdatedDocs] = useState([{ id: 'u-1', type: 'text', name: 'SRS_v2.0_Draft.txt', content: '' }]);
  const [v1Loading, setV1Loading] = useState(false);

  const navigate = useNavigate();

  // ----------------------------------------------------
  // PHASE 2: Multi-File Ingestion & Automatic Detection
  // ----------------------------------------------------
  const handleProjectFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    e.target.value = "";

    setIsClassifying(true);
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
        setProjectDocs(prev => [...prev, ...response.data.documents]);
        toast.success(`Successfully classified ${response.data.documents.length} document(s)`, { id: toastId });
      } else {
        toast.error("Failed to classify uploaded documents", { id: toastId });
      }
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.error || "Error connecting to project classification engine", { id: toastId });
    } finally {
      setIsClassifying(false);
    }
  };

  // Pre-load the 7-document Online Library scenario
  const handleLoadSampleProject = async () => {
    setIsClassifying(true);
    const toastId = toast.loading("Loading 7-Document Online Library Sample Collection...");

    try {
      const payload = {
        documents: SAMPLE_7_DOCS.map(doc => ({
          name: doc.name,
          text: doc.text
        }))
      };

      const apiUrl = import.meta.env?.VITE_API_URL || 'http://localhost:5001/api/compare';
      const detectUrl = apiUrl.replace('/api/compare', '/api/project/detect').replace('/compare', '/project/detect');

      const response = await axios.post(detectUrl, payload, {
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.data.success && response.data.documents) {
        setProjectDocs(response.data.documents);
        toast.success("Loaded 7 project documents with auto-classification!", { id: toastId });
      } else {
        toast.error("Failed to classify sample collection", { id: toastId });
      }
    } catch (err) {
      console.error(err);
      toast.error("Failed to load sample collection. Ensure backend is running.", { id: toastId });
    } finally {
      setIsClassifying(false);
    }
  };

  const removeProjectDoc = (docId) => {
    setProjectDocs(prev => prev.filter(d => d.document_id !== docId));
  };

  // Run Cross-Document Semantic Verification and open Dashboard
  const handleRunPhase2Verification = async () => {
    if (projectDocs.length === 0) {
      toast.error("Please upload at least one project document.");
      return;
    }

    setIsVerifying(true);
    const toastId = toast.loading(`Generating Cross-Document Semantic Verification Matrix for ${projectDocs.length} documents...`);

    try {
      const apiUrl = import.meta.env?.VITE_API_URL || 'http://localhost:5001/api/compare';
      const verifyUrl = apiUrl.replace('/api/compare', '/api/project/verify').replace('/compare', '/project/verify');

      const response = await axios.post(verifyUrl, {
        documents: projectDocs
      });

      toast.success("Cross-Document Traceability Matrix Generated!", { id: toastId });
      navigate('/dashboard', { state: { result: response.data } });
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.error || "Error running cross-document verification", { id: toastId });
    } finally {
      setIsVerifying(false);
    }
  };

  // ----------------------------------------------------
  // V1: Legacy Baseline vs Updated Logic (100% Intact)
  // ----------------------------------------------------
  const handleV1FileUpload = async (e, setDocs) => {
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
          toast.success(`${file.name} loaded`);
        };
        reader.readAsText(file);
      } else if (ext === 'pdf' || ext === 'docx') {
        const formData = new FormData();
        formData.append('file', file);
        const loadToast = toast.loading(`Extracting text from ${file.name}...`);
        try {
          const rawApiUrl = import.meta.env?.VITE_API_URL || 'http://localhost:5001/api/compare';
          const extractUrl = rawApiUrl.replace('/api/compare', '/api/extract-text').replace('/compare', '/extract-text');
          const response = await axios.post(extractUrl, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          if (response.data.success) {
            setDocs(prev => [...prev, { id, type: 'file', name: file.name, ext, content: response.data.text }]);
            toast.success(`${file.name} extracted`, { id: loadToast });
          } else {
            toast.error(`Failed to extract text from ${file.name}`, { id: loadToast });
          }
        } catch (err) {
          toast.error(`Parse Error: ${err.message}`, { id: loadToast });
        }
      }
    }
  };

  const handleV1Compare = async () => {
    const validBaseline = baselineDocs.filter(d => d.type === 'file' || (d.type === 'text' && d.content.trim()));
    const validUpdated = updatedDocs.filter(d => d.type === 'file' || (d.type === 'text' && d.content.trim()));

    if (validBaseline.length === 0 || validUpdated.length === 0) {
      toast.error('Please provide at least one Baseline and one Updated document.');
      return;
    }

    const baselinePayload = validBaseline.map(d => ({ name: d.name, text: d.content }));
    const updatedPayload = validUpdated.map(d => ({ name: d.name, text: d.content }));

    setV1Loading(true);
    try {
      const apiUrl = import.meta.env?.VITE_API_URL || 'http://localhost:5001/api/compare';
      const response = await axios.post(apiUrl, {
        baseline: baselinePayload,
        updated: updatedPayload
      });
      navigate('/dashboard', { state: { result: response.data } });
      toast.success('Analysis complete!');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Analysis failed. Is backend running?');
    } finally {
      setV1Loading(false);
    }
  };

  // Helper color map for Document Types
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
    <div className="w-full max-w-6xl mx-auto rounded-3xl bg-slate-900/70 border border-slate-800 shadow-2xl backdrop-blur-2xl p-6 sm:p-10 relative overflow-hidden">
      
      {/* 1. Mode Switcher Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-6 mb-8 border-b border-slate-800/80">
        <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-slate-950/80 border border-slate-800">
          <button
            onClick={() => setActiveMode('project')}
            className={`px-5 py-2.5 rounded-xl font-extrabold text-xs sm:text-sm transition-all flex items-center gap-2 ${
              activeMode === 'project'
                ? 'bg-neon-blue/20 text-white border border-neon-blue/40 shadow-lg shadow-neon-blue/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-4 h-4 text-neon-blue" />
            Project Intelligence (Phase 2)
          </button>
          
          <button
            onClick={() => setActiveMode('version')}
            className={`px-5 py-2.5 rounded-xl font-extrabold text-xs sm:text-sm transition-all flex items-center gap-2 ${
              activeMode === 'version'
                ? 'bg-indigo-500/20 text-white border border-indigo-500/40 shadow-lg shadow-indigo-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <RefreshCw className="w-4 h-4 text-indigo-400" />
            Version Comparison (V1)
          </button>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3.5 py-1 rounded-full bg-slate-950 border border-slate-800 text-[11px] font-mono font-semibold text-slate-400 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            {activeMode === 'project' ? 'Multi-Doc Classification Active' : 'TF-IDF Lexical Drift Active'}
          </span>
        </div>
      </div>

      {/* ======================================================== */}
      {/* PHASE 2 MODE: Unified Project Documents Collection       */}
      {/* ======================================================== */}
      {activeMode === 'project' && (
        <div>
          {/* Header & Subtitle */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
            <div>
              <h3 className="text-xl sm:text-2xl font-black text-white tracking-tight flex items-center gap-2.5">
                <Database className="w-6 h-6 text-neon-blue" />
                PROJECT DOCUMENTS
              </h3>
              <p className="text-slate-400 text-xs sm:text-sm mt-1 font-medium">
                Upload all project artifacts for cross-document intelligence (BRDs, SRS, FRDs, User Stories, Test Cases, Change Requests, Meeting Minutes).
              </p>
            </div>

            <button
              onClick={handleLoadSampleProject}
              disabled={isClassifying}
              className="px-4 py-2 bg-indigo-950/60 hover:bg-indigo-900/80 border border-indigo-500/40 text-indigo-300 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-sm hover:shadow-[0_0_15px_rgba(99,102,241,0.3)] shrink-0"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              Load 7-Doc Library Sample Set
            </button>
          </div>

          {/* Unified Upload Target (Supports Multi-File Drag & Drop) */}
          <div className="relative group rounded-2xl bg-slate-950/60 border-2 border-dashed border-slate-700/80 hover:border-neon-blue/60 transition-all p-8 text-center cursor-pointer mb-8">
            <input
              type="file"
              multiple
              accept=".txt,.pdf,.docx"
              onChange={handleProjectFileUpload}
              disabled={isClassifying}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
            />
            <div className="flex flex-col items-center justify-center">
              <div className="w-14 h-14 rounded-2xl bg-neon-blue/10 border border-neon-blue/30 flex items-center justify-center mb-3 group-hover:scale-110 group-hover:shadow-[0_0_20px_var(--color-neon-blue)] transition-all">
                {isClassifying ? (
                  <Loader2 className="w-7 h-7 text-neon-blue animate-spin" />
                ) : (
                  <UploadCloud className="w-7 h-7 text-neon-blue" />
                )}
              </div>
              <h4 className="text-base font-bold text-slate-100 mb-1">
                {isClassifying ? "Ingesting & Classifying Documents..." : "Upload Project Documents"}
              </h4>
              <p className="text-xs text-slate-400 max-w-md">
                Select multiple files simultaneously (.docx, .pdf, .txt). The engine automatically classifies each document type.
              </p>
            </div>
          </div>

          {/* Document Cards Grid */}
          {projectDocs.length > 0 ? (
            <div className="space-y-3 mb-8">
              <div className="flex items-center justify-between text-xs font-mono font-bold text-slate-400 px-1">
                <span>{projectDocs.length} PROJECT DOCUMENTS CLASSIFIED</span>
                <span>CONTENT-BASED DETECTION</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {projectDocs.map((doc, idx) => (
                  <div 
                    key={doc.document_id || idx}
                    className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between shadow-sm relative group"
                  >
                    <div>
                      {/* Top row: Name & Delete */}
                      <div className="flex items-start justify-between gap-3 mb-3">
                        <div className="flex items-center gap-2.5 overflow-hidden">
                          <div className="w-9 h-9 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-300 shrink-0">
                            <FileText className="w-4 h-4 text-neon-blue" />
                          </div>
                          <div className="overflow-hidden">
                            <span className="font-bold text-sm text-slate-100 truncate block" title={doc.filename}>
                              {doc.filename}
                            </span>
                            <span className="text-[10px] font-mono text-slate-500 uppercase">
                              {doc.filename.split('.').pop() || 'TXT'} Document
                            </span>
                          </div>
                        </div>

                        <button
                          onClick={() => removeProjectDoc(doc.document_id)}
                          className="p-1 hover:bg-red-500/20 text-slate-500 hover:text-red-400 rounded-lg transition-colors"
                          title="Remove document"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>

                      {/* Middle row: Badges & Confidence */}
                      <div className="flex flex-wrap items-center gap-2 mb-3">
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-extrabold border ${getTypeBadgeStyle(doc.document_type)}`}>
                          {doc.document_type}
                        </span>

                        <span className="text-[11px] font-mono text-slate-400 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-full">
                          {doc.confidence_score}% confidence
                        </span>

                        <span className="text-[11px] font-medium text-emerald-400 flex items-center gap-1 bg-emerald-950/40 border border-emerald-500/30 px-2 py-0.5 rounded-full">
                          <CheckCircle2 className="w-3 h-3" /> Extracted & Ready
                        </span>
                      </div>
                    </div>

                    {/* Bottom: Artifact Count */}
                    <div className="pt-3 border-t border-slate-900 flex items-center justify-between text-xs font-semibold text-slate-400">
                      <span className="text-slate-300">
                        {doc.artifact_label || `${doc.artifact_count || 0} Normalized Artifacts`}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500">
                        ID: {doc.document_id?.substring(0, 8)}...
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-8 rounded-2xl bg-slate-950/40 border border-slate-800/80 text-center mb-8">
              <p className="text-slate-400 text-sm font-medium">
                No documents uploaded yet. Click <span className="text-neon-blue font-bold">Upload Files</span> above or load the <span className="text-indigo-400 font-bold">7-Doc Library Sample Set</span> to see independent automatic classification in action.
              </p>
            </div>
          )}

          {/* Phase 2 Action Button */}
          <div className="pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-xs text-slate-400 font-medium">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Zero Baseline/Updated assumptions · Independent content classification</span>
            </div>

            <button
              onClick={handleRunPhase2Verification}
              disabled={projectDocs.length === 0 || isVerifying}
              className="w-full sm:w-auto px-8 py-3.5 bg-neon-blue/15 hover:bg-neon-blue/25 text-white neon-border rounded-xl font-bold text-base shadow-xl shadow-neon-glow hover:shadow-[0_0_25px_var(--color-neon-blue)] transition-all flex items-center justify-center gap-2 group disabled:opacity-40"
            >
              {isVerifying ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating Verification Matrix...
                </>
              ) : (
                <>
                  <span>Run Cross-Document Semantic Verification</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-neon-blue" />
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* V1 MODE: Version Comparison (Baseline vs Updated)        */}
      {/* ======================================================== */}
      {activeMode === 'version' && (
        <div>
          <div className="mb-6">
            <h3 className="text-xl sm:text-2xl font-black text-white tracking-tight flex items-center gap-2.5">
              <RefreshCw className="w-6 h-6 text-indigo-400" />
              VERSION COMPARISON (V1)
            </h3>
            <p className="text-slate-400 text-xs sm:text-sm mt-1 font-medium">
              Compare baseline specification against updated changes to compute TF-IDF lexical drift, requirement modifications, and scope creep.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Baseline Column */}
            <div className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-neon-blue"></span>
                  Baseline Documents
                </span>
                <span className="text-[10px] font-mono text-neon-blue bg-neon-blue/10 border border-neon-blue/20 px-2 py-0.5 rounded-full uppercase">
                  Source of Truth
                </span>
              </div>
              
              {baselineDocs.map((doc, i) => (
                <textarea
                  key={doc.id || i}
                  className="w-full h-36 p-3 bg-slate-900/60 border border-slate-800 rounded-xl text-xs font-mono text-slate-200 focus:outline-none resize-none mb-3"
                  placeholder="Paste original requirements here..."
                  value={doc.content}
                  onChange={(e) => setBaselineDocs(prev => prev.map(d => d.id === doc.id ? { ...d, content: e.target.value } : d))}
                />
              ))}

              <label className="flex items-center justify-center gap-2 h-10 border border-dashed border-slate-700 hover:border-neon-blue/60 rounded-xl cursor-pointer bg-slate-900/40 text-xs font-bold text-slate-300">
                <UploadCloud className="w-4 h-4 text-neon-blue" />
                Upload Baseline Files (.txt, .pdf, .docx)
                <input type="file" multiple className="hidden" accept=".txt,.pdf,.docx" onChange={(e) => handleV1FileUpload(e, setBaselineDocs)} />
              </label>
            </div>

            {/* Updated Column */}
            <div className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-indigo-400"></span>
                  Updated Documents
                </span>
                <span className="text-[10px] font-mono text-indigo-300 bg-indigo-950/60 border border-indigo-500/30 px-2 py-0.5 rounded-full uppercase">
                  Delta Candidate
                </span>
              </div>

              {updatedDocs.map((doc, i) => (
                <textarea
                  key={doc.id || i}
                  className="w-full h-36 p-3 bg-slate-900/60 border border-slate-800 rounded-xl text-xs font-mono text-slate-200 focus:outline-none resize-none mb-3"
                  placeholder="Paste updated requirements here..."
                  value={doc.content}
                  onChange={(e) => setUpdatedDocs(prev => prev.map(d => d.id === doc.id ? { ...d, content: e.target.value } : d))}
                />
              ))}

              <label className="flex items-center justify-center gap-2 h-10 border border-dashed border-slate-700 hover:border-indigo-400/60 rounded-xl cursor-pointer bg-slate-900/40 text-xs font-bold text-slate-300">
                <UploadCloud className="w-4 h-4 text-indigo-400" />
                Upload Updated Files (.txt, .pdf, .docx)
                <input type="file" multiple className="hidden" accept=".txt,.pdf,.docx" onChange={(e) => handleV1FileUpload(e, setUpdatedDocs)} />
              </label>
            </div>
          </div>

          <div className="pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-xs text-slate-400">
              Preserves legacy TF-IDF baseline-versus-updated lexical difference engine.
            </div>

            <button
              onClick={handleV1Compare}
              disabled={v1Loading}
              className="w-full sm:w-auto px-8 py-3.5 bg-indigo-600/20 hover:bg-indigo-600/30 text-white neon-border rounded-xl font-bold text-base shadow-xl transition-all flex items-center justify-center gap-2 group disabled:opacity-40"
            >
              {v1Loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Running V1 Comparison...
                </>
              ) : (
                <>
                  <span>Run Version Drift Analysis</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-indigo-400" />
                </>
              )}
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
