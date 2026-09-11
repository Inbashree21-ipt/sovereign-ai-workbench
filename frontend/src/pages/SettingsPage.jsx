import React, { useState } from 'react';
import {
  Settings,
  Server,
  Radio,
  ShieldCheck,
  Lock,
  CheckCircle2,
  Code2
} from 'lucide-react';

import { Badge } from '../components/common/Badge';

export const SettingsPage = () => {
  const [serverUrl, setServerUrl] = useState(
    'http://localhost:8000'
  );

  const [defaultModel, setDefaultModel] = useState(
    'qwen2.5-coder:3b'
  );

  const [airGappedMode] = useState(true);
  const [cloudApiDisabled] = useState(true);

  const [localVectorDb] = useState(
    'ChromaDB (Local Persistent)'
  );

  return (
    <div className="p-6 space-y-6 max-w-5xl">

      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">

        <div>
          <div className="flex items-center gap-2">
            <Settings className="w-6 h-6 text-cyan-400" />

            <h2 className="text-xl font-bold text-slate-100">
              System & Security Settings
            </h2>
          </div>

          <p className="text-xs text-slate-400 mt-1">
            Configure local server bindings, air-gap policy,
            default LLM router parameters, and FastAPI connection
            endpoints.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge
            variant="emerald"
            className="py-1 px-3"
          >
            AIR-GAPPED COMPLIANT
          </Badge>
        </div>

      </div>

      {/* Security Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        {/* Processing Mode */}
        <div className="p-4 rounded-xl bg-slate-900 border border-emerald-500/30 flex items-center justify-between">

          <div>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">
              Processing Mode
            </span>

            <span className="text-xs font-bold text-emerald-400">
              Data Processing: On-Premise
            </span>
          </div>

          <ShieldCheck className="w-5 h-5 text-emerald-400" />

        </div>

        {/* Cloud Status */}
        <div className="p-4 rounded-xl bg-slate-900 border border-rose-500/30 flex items-center justify-between">

          <div>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">
              Cloud Status
            </span>

            <span className="text-xs font-bold text-rose-400">
              Cloud API: Disabled
            </span>
          </div>

          <Lock className="w-5 h-5 text-rose-400" />

        </div>

        {/* Network Guard */}
        <div className="p-4 rounded-xl bg-slate-900 border border-cyan-500/30 flex items-center justify-between">

          <div>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">
              Network Guard
            </span>

            <span className="text-xs font-bold text-cyan-400">
              External Network Access: Disabled
            </span>
          </div>

          <Radio className="w-5 h-5 text-cyan-400" />

        </div>

      </div>

      {/* Connection & Server Settings */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">

        <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider border-b border-slate-800 pb-3 flex items-center gap-2">

          <Server className="w-4 h-4 text-cyan-400" />

          <span>
            Local Server & FastAPI Backend Connection
          </span>

        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">

          {/* Backend URL */}
          <div>

            <label className="block font-semibold text-slate-300 uppercase mb-1">
              FastAPI Backend Server URL
            </label>

            <input
              type="text"
              value={serverUrl}
              onChange={(e) =>
                setServerUrl(e.target.value)
              }
              className="w-full bg-slate-950 text-cyan-300 font-mono text-xs rounded-xl p-3 border border-slate-800 focus:outline-none focus:border-cyan-500"
            />

            <p className="text-[11px] text-slate-500 mt-1">
              Local FastAPI backend connected to Ollama.
            </p>

          </div>

          {/* Connection Status */}
          <div>

            <label className="block font-semibold text-slate-300 uppercase mb-1">
              API Backend Connection Status
            </label>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">

              <span className="text-slate-300 font-mono text-xs">
                FastAPI Backend
              </span>

              <span className="flex items-center gap-1 text-emerald-400 text-xs font-bold">

                <CheckCircle2 className="w-4 h-4" />

                CONNECTED

              </span>

            </div>

          </div>

          {/* Default Local LLM */}
          <div>

            <label className="block font-semibold text-slate-300 uppercase mb-1">
              Default Local LLM Model
            </label>

            <select
              value={defaultModel}
              onChange={(e) =>
                setDefaultModel(e.target.value)
              }
              className="w-full bg-slate-950 text-slate-200 text-xs rounded-xl p-3 border border-slate-800 focus:outline-none focus:border-cyan-500"
            >

              <option value="qwen2.5-coder:3b">
                qwen2.5-coder:3b — Coding
              </option>

              <option value="llama3.2:3b">
                llama3.2:3b — General / Documents
              </option>

              <option value="gemma3:4b">
                gemma3:4b — Vision / Multimodal
              </option>

            </select>

          </div>

          {/* Vector DB */}
          <div>

            <label className="block font-semibold text-slate-300 uppercase mb-1">
              Local Vector Store Backend
            </label>

            <input
              type="text"
              value={localVectorDb}
              readOnly
              className="w-full bg-slate-950 text-slate-400 font-mono text-xs rounded-xl p-3 border border-slate-800"
            />

          </div>

        </div>

      </div>

      {/* Local Model Information */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">

        <div className="flex items-center gap-2 border-b border-slate-800 pb-3">

          <Server className="w-5 h-5 text-cyan-400" />

          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
            Local Ollama Models
          </h3>

        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">

          {/* Coding Model */}
          <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl">

            <div className="text-cyan-400 text-xs font-bold mb-2">
              CODING
            </div>

            <div className="text-slate-100 font-mono text-sm">
              qwen2.5-coder:3b
            </div>

            <div className="text-slate-500 text-[11px] mt-1">
              Local code generation and programming
            </div>

          </div>

          {/* General Model */}
          <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl">

            <div className="text-emerald-400 text-xs font-bold mb-2">
              GENERAL / DOCUMENTS
            </div>

            <div className="text-slate-100 font-mono text-sm">
              llama3.2:3b
            </div>

            <div className="text-slate-500 text-[11px] mt-1">
              General questions and document tasks
            </div>

          </div>

          {/* Vision Model */}
          <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl">

            <div className="text-purple-400 text-xs font-bold mb-2">
              VISION / MULTIMODAL
            </div>

            <div className="text-slate-100 font-mono text-sm">
              gemma3:4b
            </div>

            <div className="text-slate-500 text-[11px] mt-1">
              Image analysis and multimodal tasks
            </div>

          </div>

        </div>

      </div>

      {/* Developer Integration Guide */}
      <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 space-y-4 font-mono text-xs">

        <div className="flex items-center justify-between border-b border-slate-800 pb-3">

          <div className="flex items-center gap-2 text-cyan-400 font-bold">

            <Code2 className="w-5 h-5" />

            <span>
              FastAPI Backend Connection Guide
            </span>

          </div>

          <Badge variant="cyan">
            DEV GUIDE
          </Badge>

        </div>

        <p className="text-slate-400 leading-relaxed font-sans text-xs">
          This frontend is connected to the local FastAPI +
          Ollama backend used by the Sovereign AI Workbench.
        </p>

        <div className="bg-slate-900 p-4 rounded-xl border border-slate-800 space-y-3 text-slate-300">

          {/* API Base */}
          <div className="text-cyan-400 font-bold">
            Backend:
          </div>

          <pre className="bg-slate-950 p-3 rounded text-[11px] text-slate-300 border border-slate-800 overflow-x-auto">
{`http://localhost:8000`}
          </pre>

          {/* Routes */}
          <div className="text-cyan-400 font-bold pt-2">
            Active FastAPI Routes:
          </div>

          <ul className="list-disc pl-5 space-y-1 text-slate-400 text-[11px]">

            <li>
              <code>POST /ask</code> — AI chat with automatic model routing
            </li>

            <li>
              <code>POST /vision</code> — Local image analysis using gemma3:4b
            </li>

            <li>
              <code>POST /agent</code> — Agentic workflow execution
            </li>

            <li>
              <code>GET /models</code> — List locally available Ollama models
            </li>

            <li>
              <code>GET /deliverables</code> — List generated files
            </li>

            <li>
              <code>GET /deliverables/download/filename</code> — Download generated files
            </li>

          </ul>

          {/* Models */}
          <div className="text-cyan-400 font-bold pt-2">
            Local Model Router:
          </div>

          <pre className="bg-slate-950 p-3 rounded text-[11px] text-slate-300 border border-slate-800 overflow-x-auto">
{`Coding      -> qwen2.5-coder:3b
General     -> llama3.2:3b
Vision      -> gemma3:4b`}
          </pre>

        </div>

      </div>

    </div>
  );
};