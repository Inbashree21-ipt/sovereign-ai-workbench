
import React, { useState, useEffect } from 'react';
import {
  Database,
  Search,
  FileText,
  Layers,
  ShieldCheck,
  CheckCircle2
} from 'lucide-react';

import { Badge } from '../components/common/Badge';
import {
  searchKnowledgeBase,
  getSystemStatus
} from '../services/api';

export const KnowledgeBasePage = () => {
  const [query, setQuery] = useState('');
  const [chunks, setChunks] = useState([]);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const sys = await getSystemStatus();
      setStatus(sys);

      // Do not search with an empty query.
      // Results are loaded only after the user enters a question.
      setChunks([]);
    } catch (error) {
      console.error('Failed to load Knowledge Base:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query.trim()) {
      setChunks([]);
      return;
    }

    try {
      const res = await searchKnowledgeBase(query);
      setChunks(res);
    } catch (error) {
      console.error('RAG search failed:', error);
      setChunks([]);
    }
  };

  return (
    <div className="p-6 space-y-6">

      {/* =====================================================
          RAG INFORMATION & TELEMETRY
          ===================================================== */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-4">

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">

          <div>
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-cyan-400" />

              <h2 className="text-xl font-bold text-slate-100">
                RAG Vector Knowledge Store
              </h2>
            </div>

            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Internal documents are processed locally and used as context
              for AI responses. Text chunking, embedding generation, and
              vector indexing are performed locally using FAISS and
              HuggingFace embeddings.
            </p>
          </div>


          {/* TELEMETRY */}
          <div className="flex flex-wrap items-center gap-3">

            <div className="px-4 py-2 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                Total Documents
              </span>

              <span className="text-sm font-bold text-slate-100 font-mono">
                {status ? status.totalDocuments : 0} Files
              </span>
            </div>


            <div className="px-4 py-2 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                Vector Chunks
              </span>

              <span className="text-sm font-bold text-cyan-400 font-mono">
                {status?.indexedChunksTotal || 0} Chunks
              </span>
            </div>


            <div className="px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-1.5">

              <ShieldCheck className="w-4 h-4" />

              <span>
                FAISS + Local HuggingFace Embeddings
              </span>

            </div>

          </div>
        </div>


        {/* PRIVACY INFORMATION */}
        <div className="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-xs text-cyan-200 flex items-start gap-3">

          <Layers className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />

          <div>

            <span className="font-bold block text-slate-100">
              Confidential Vector Privacy Guarantee
            </span>

            Internal documents are processed locally and used as context
            for AI responses. Document contents and generated embeddings
            remain within the local application workflow.

          </div>

        </div>

      </div>


      {/* =====================================================
          SEARCH BAR
          ===================================================== */}
      <form onSubmit={handleSearch} className="flex gap-3">

        <div className="relative flex-1">

          <Search className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />

          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search knowledge base (e.g., socket programming, file transfer, chat application)..."
            className="w-full bg-slate-900 text-slate-100 text-sm rounded-xl pl-11 pr-4 py-3 border border-slate-800 focus:outline-none focus:border-cyan-500 transition-colors shadow-inner"
          />

        </div>


        <button
          type="submit"
          className="px-6 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-sm transition-colors shadow-md shadow-cyan-500/10"
        >
          Vector Search
        </button>

      </form>


      {/* =====================================================
          SEARCH RESULTS
          ===================================================== */}
      <div className="space-y-4">

        <div className="flex items-center justify-between">

          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
            Vector Store Search Chunks ({chunks.length} Results)
          </h3>

          <span className="text-xs text-slate-400 font-mono">
            Top-K Retrieval: 3
          </span>

        </div>


        {/* NO RESULTS MESSAGE */}
        {chunks.length === 0 && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center">

            <Database className="w-8 h-8 text-slate-600 mx-auto mb-3" />

            <p className="text-sm text-slate-400">
              Enter a question above to search the local knowledge base.
            </p>

          </div>
        )}


        {/* RESULTS */}
        <div className="grid grid-cols-1 gap-4">

          {chunks.map((chunk) => (

            <div
              key={chunk.id}
              className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-3 hover:border-cyan-500/30 transition-all"
            >

              {/* RESULT HEADER */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">

                <div className="flex items-center gap-2.5">

                  <div className="p-1.5 rounded bg-slate-950 border border-slate-800 text-cyan-400">

                    <FileText className="w-4 h-4" />

                  </div>


                  <div>

                    <h4 className="text-xs font-bold text-slate-100 font-mono">
                      {chunk.docName}
                    </h4>

                    <span className="text-[10px] text-slate-400">
                      Page {chunk.page} | Chunk ID: {chunk.id}
                    </span>

                  </div>

                </div>


                {/* DISTANCE SCORE */}
                <div className="flex items-center gap-2">

                  <span className="text-xs text-slate-400">
                    Distance:
                  </span>

                  <Badge
                    variant="emerald"
                    className="font-mono text-xs font-bold"
                  >
                    {typeof chunk.distance === 'number'
                      ? chunk.distance.toFixed(4)
                      : 'N/A'}
                  </Badge>

                </div>

              </div>


              {/* CHUNK CONTENT */}
              <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono leading-relaxed whitespace-pre-wrap">

                {chunk.chunkText}

              </div>


              {/* RESULT FOOTER */}
              <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono pt-1">

                <span>
                  FAISS Vector Retrieval
                </span>

                <span className="flex items-center gap-1 text-emerald-400">

                  <CheckCircle2 className="w-3 h-3" />

                  Indexed & Verified

                </span>

              </div>

            </div>

          ))}

        </div>

      </div>

    </div>
  );
};

