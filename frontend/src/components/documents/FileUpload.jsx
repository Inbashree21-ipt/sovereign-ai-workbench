import React, { useState } from 'react';
import { UploadCloud, File, ShieldCheck, CheckCircle2 } from 'lucide-react';

export const FileUpload = ({ onUpload }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedSuccess, setUploadedSuccess] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = async (file) => {
    setUploading(true);
    await onUpload(file);
    setUploading(false);
    setUploadedSuccess(true);
    setTimeout(() => setUploadedSuccess(false), 3000);
  };

  return (
    <div className="w-full">
      <form
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-2xl transition-all duration-300 ${
          dragActive
            ? 'border-cyan-400 bg-cyan-500/10 scale-[0.99]'
            : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
        }`}
      >
        <input
          type="file"
          id="file-upload-input"
          multiple={false}
          onChange={handleChange}
          accept=".pdf,.docx,.xlsx,.txt"
          className="hidden"
        />

        <label htmlFor="file-upload-input" className="cursor-pointer flex flex-col items-center text-center">
          <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700/80 text-cyan-400 mb-3 shadow-lg shadow-cyan-500/5">
            {uploading ? (
              <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
            ) : uploadedSuccess ? (
              <CheckCircle2 className="w-8 h-8 text-emerald-400" />
            ) : (
              <UploadCloud className="w-8 h-8" />
            )}
          </div>

          <h4 className="text-base font-semibold text-slate-100">
            {uploading ? 'Processing & Vectorizing File Locally...' : uploadedSuccess ? 'Document Ingested & Vectorized!' : 'Click to Upload or Drag & Drop Documents'}
          </h4>
          <p className="text-xs text-slate-400 mt-1 max-w-sm">
            Supports PDF, DOCX, XLSX, TXT. Files are processed air-gapped on your local hardware using ChromaDB embeddings.
          </p>

          <div className="mt-4 flex items-center gap-2 text-[11px] text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 font-medium">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Zero External Cloud Transmission</span>
          </div>
        </label>
      </form>
    </div>
  );
};
