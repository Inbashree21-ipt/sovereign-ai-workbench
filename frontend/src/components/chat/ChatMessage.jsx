import React from 'react';
import { User, ShieldCheck, FileText, CheckCircle2, ChevronRight } from 'lucide-react';
import { Badge } from '../common/Badge';

export const ChatMessage = ({ message }) => {
  const isAi = message.sender === 'ai';

  return (
    <div className={`flex gap-4 p-4 rounded-xl transition-colors ${
      isAi ? 'bg-slate-900/90 border border-slate-800' : 'bg-slate-800/40 border border-slate-800/60'
    }`}>
      {/* Avatar */}
      <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
        isAi 
          ? 'bg-gradient-to-br from-cyan-500 to-emerald-600 text-slate-950 font-bold shadow-md shadow-cyan-500/10' 
          : 'bg-slate-700 text-slate-200'
      }`}>
        {isAi ? <ShieldCheck className="w-5 h-5" /> : <User className="w-5 h-5" />}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 space-y-2">
        {/* Header line */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-200">
              {isAi ? message.model || 'Sovereign AI Assistant' : 'Confidential User'}
            </span>
            {isAi && (
              <Badge variant="emerald" className="text-[10px] py-0 px-2">
                AIR-GAPPED MODEL
              </Badge>
            )}
          </div>
          <span className="text-[11px] text-slate-400 font-mono">{message.timestamp}</span>
        </div>

        {/* Reasoning Steps (if AI) */}
        {isAi && message.reasoningSteps && message.reasoningSteps.length > 0 && (
          <details className="text-xs bg-slate-950/80 rounded-lg border border-slate-800 p-2.5 group">
            <summary className="font-mono text-cyan-400 cursor-pointer flex items-center gap-1.5 select-none hover:text-cyan-300">
              <ChevronRight className="w-3.5 h-3.5 transition-transform group-open:rotate-90" />
              <span>Local Agentic Reasoning ({message.reasoningSteps.length} steps)</span>
            </summary>
            <ul className="mt-2 pl-4 space-y-1 text-slate-400 font-mono text-[11px] border-l border-slate-800 ml-1">
              {message.reasoningSteps.map((step, idx) => (
                <li key={idx} className="flex items-center gap-2">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                  <span>{step}</span>
                </li>
              ))}
            </ul>
          </details>
        )}

        {/* Text body */}
        <div className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap font-sans">
          {message.text}
        </div>

        {/* RAG Citations */}
        {isAi && message.citations && message.citations.length > 0 && (
          <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
            <span className="text-[11px] text-slate-400 font-semibold uppercase tracking-wider">RAG Context:</span>
            {message.citations.map((cit, idx) => (
              <div key={idx} className="flex items-center gap-1.5 px-2 py-1 rounded bg-slate-950 border border-cyan-500/20 text-[11px] text-cyan-300 font-mono">
                <FileText className="w-3 h-3 text-cyan-400" />
                <span>{cit.docName}</span>
                <span className="text-slate-400">({cit.chunkId})</span>
                <span className="text-emerald-400 text-[10px] font-bold">{cit.similarity}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
