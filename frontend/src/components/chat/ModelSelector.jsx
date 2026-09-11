import React from 'react';
import { Cpu, ChevronDown } from 'lucide-react';

export const ModelSelector = ({ selectedModel, onSelectModel, models = [] }) => {
  return (
    <div className="relative inline-block text-left">
      <div className="flex items-center gap-2">
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Model:</label>
        <div className="relative">
          <select
            value={selectedModel}
            onChange={(e) => onSelectModel(e.target.value)}
            className="appearance-none bg-slate-900 text-cyan-300 font-medium text-xs rounded-lg pl-8 pr-8 py-2 border border-slate-700 hover:border-cyan-500/50 focus:outline-none focus:border-cyan-500 transition-all cursor-pointer shadow-sm"
          >
            {models.map((m) => (
              <option key={m.id} value={m.id} className="bg-slate-900 text-slate-200">
                {m.name} ({m.quantization || m.parameterSize})
              </option>
            ))}
          </select>
          <Cpu className="w-4 h-4 text-cyan-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>
      </div>
    </div>
  );
};
