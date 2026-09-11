import React, { useState, useEffect } from 'react';
import { FolderArchive, ShieldCheck, HardDrive } from 'lucide-react';
import { GeneratedFileCard } from '../components/files/GeneratedFileCard';
import { getGeneratedFiles, deleteGeneratedFile } from '../services/api';

export const GeneratedFilesPage = () => {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const data = await getGeneratedFiles();
      setFiles(data);
    } catch (error) {
      console.error('Failed to load generated files:', error);
      alert('Failed to load generated files. Please check whether the backend is running.');
    }
  };

  const handleDelete = async (id) => {
    await deleteGeneratedFile(id);
    await loadFiles();
  };

  const handleDownload = (filename) => {
    const downloadUrl =
      `http://127.0.0.1:8000/deliverables/download/${encodeURIComponent(filename)}`;

    window.open(downloadUrl, '_blank');
  };

  return (
    <div className="p-6 space-y-6">

      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">

        <div>
          <div className="flex items-center gap-2">
            <FolderArchive className="w-6 h-6 text-emerald-400" />

            <h2 className="text-xl font-bold text-slate-100">
              Generated Industrial Deliverables
            </h2>
          </div>

          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Output reports, executive approval notes, calculation spreadsheets,
            and automation code synthesized by autonomous local agents.
          </p>
        </div>

        <div className="flex items-center gap-3">

          <div className="px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-2 text-xs text-slate-300">
            <HardDrive className="w-4 h-4 text-cyan-400" />

            <span>Deliverables:</span>

            <span className="font-bold text-cyan-300 font-mono">
              {files.length} Files
            </span>
          </div>

          <div className="px-3.5 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-2 text-xs text-emerald-400 font-semibold">
            <ShieldCheck className="w-4 h-4" />

            <span>Local AES-256 Storage</span>
          </div>

        </div>
      </div>

      {/* Generated Deliverable Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        {files.map((file) => (

          <GeneratedFileCard
            key={file.name}
            file={file}
            onDelete={handleDelete}
            onDownload={handleDownload}
          />

        ))}

      </div>

    </div>
  );
};