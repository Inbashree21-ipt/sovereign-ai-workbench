import React, { useState, useEffect } from 'react';
import { FileText, ShieldCheck, Database, HardDrive } from 'lucide-react';
import { FileUpload } from '../components/documents/FileUpload';
import { DocumentTable } from '../components/documents/DocumentTable';
import { getDocuments, uploadDocument, deleteDocument } from '../services/api';

export const DocumentsPage = () => {
  const [documents, setDocuments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadDocs();
  }, []);

  const loadDocs = async () => {
    const data = await getDocuments();
    setDocuments(data);
  };

  const handleUpload = async (fileObj) => {
    await uploadDocument(fileObj);
    await loadDocs();
  };

  const handleDelete = async (id) => {
    await deleteDocument(id);
    await loadDocs();
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Confidential Document Management</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Upload technical SOPs, engineering drawings, and inspection logs. Documents are parsed and vectorized into your local ChromaDB store.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-2.5 text-xs text-slate-300">
            <HardDrive className="w-4 h-4 text-cyan-400" />
            <span>Indexed Documents:</span>
            <span className="font-bold text-cyan-300 font-mono">{documents.length}</span>
          </div>
          <div className="px-3.5 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-2 text-xs text-emerald-400 font-semibold">
            <ShieldCheck className="w-4 h-4" />
            <span>Air-Gapped Embedding</span>
          </div>
        </div>
      </div>

      {/* Drag & Drop Upload Zone */}
      <FileUpload onUpload={handleUpload} />

      {/* Uploaded Documents List */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">Repository Files & Vector Status</h3>
        <DocumentTable
          documents={documents}
          onDelete={handleDelete}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
        />
      </div>
    </div>
  );
};
