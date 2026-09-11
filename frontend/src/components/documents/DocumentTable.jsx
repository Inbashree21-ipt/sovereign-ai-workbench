import React from 'react';
import { FileText, Trash2, Database, Search, HardDrive, CheckCircle2, Clock } from 'lucide-react';
import { Badge } from '../common/Badge';

export const DocumentTable = ({ documents = [], onDelete, searchQuery = '', setSearchQuery }) => {
  const filtered = documents.filter(d => 
    d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
      {/* Table Header Controls */}
      <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-900/50">
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search confidential documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 text-slate-200 text-xs rounded-lg pl-9 pr-4 py-2 border border-slate-800 focus:outline-none focus:border-cyan-500 transition-colors placeholder:text-slate-500"
          />
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
          <HardDrive className="w-3.5 h-3.5 text-cyan-400" />
          <span>Local Storage: </span>
          <span className="text-slate-200 font-bold">{documents.length} Files</span>
        </div>
      </div>

      {/* Table Body */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
            <tr>
              <th className="py-3 px-4">Document Name</th>
              <th className="py-3 px-4">Category</th>
              <th className="py-3 px-4">Type</th>
              <th className="py-3 px-4">Size</th>
              <th className="py-3 px-4">Upload Date</th>
              <th className="py-3 px-4">RAG Chunks</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan="8" className="py-8 text-center text-slate-500">
                  No confidential documents found matching "{searchQuery}".
                </td>
              </tr>
            ) : (
              filtered.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-800/40 transition-colors group">
                  <td className="py-3 px-4 font-semibold text-slate-100 flex items-center gap-2.5">
                    <div className="p-1.5 rounded bg-slate-800 text-cyan-400 border border-slate-700">
                      <FileText className="w-4 h-4" />
                    </div>
                    <span className="truncate max-w-xs">{doc.name}</span>
                  </td>
                  <td className="py-3 px-4 text-slate-400">{doc.category}</td>
                  <td className="py-3 px-4 font-mono text-[11px] text-cyan-300">{doc.type}</td>
                  <td className="py-3 px-4 font-mono text-slate-400">{doc.size}</td>
                  <td className="py-3 px-4 font-mono text-slate-400">{doc.uploadDate}</td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 font-mono text-slate-300 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                      <Database className="w-3 h-3 text-cyan-400" />
                      {doc.chunksCount} chunks
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    {doc.status === 'Indexed' ? (
                      <Badge variant="emerald" className="py-0.5">
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                        Indexed
                      </Badge>
                    ) : (
                      <Badge variant="amber" className="py-0.5">
                        <Clock className="w-3 h-3 mr-1 animate-spin" />
                        Processing
                      </Badge>
                    )}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => onDelete(doc.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                      title="Delete local document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
