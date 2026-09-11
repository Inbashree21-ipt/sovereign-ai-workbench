import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Server, 
  Cpu, 
  FileText, 
  ShieldCheck, 
  Radio, 
  ArrowRight, 
  Bot, 
  Database, 
  FolderArchive, 
  Activity, 
  Lock,
  MessageSquareText,
  Plus
} from 'lucide-react';
import { StatusCard } from '../components/common/StatusCard';
import { Badge } from '../components/common/Badge';
import { getSystemStatus, getAgentTasks, getGeneratedFiles, getDocuments } from '../services/api';

export const DashboardPage = () => {
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [files, setFiles] = useState([]);
  const [docs, setDocs] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const sys = await getSystemStatus();
      const t = await getAgentTasks();
      const f = await getGeneratedFiles();
      const d = await getDocuments();
      setStatus(sys);
      setTasks(t);
      setFiles(f);
      setDocs(d);
    };
    fetchData();
  }, []);

  if (!status) {
    return <div className="p-8 text-center text-slate-400">Loading Sovereign AI Telemetry...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Page Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Sovereign AI Workbench</h1>
            <Badge variant="emerald" className="py-1 px-3 text-xs">
              AIR-GAPPED INDUSTRIAL V1.0
            </Badge>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Confidential on-premise AI platform engineered for refineries, defense manufacturing, PSUs, and secure government offices. All LLMs & RAG vectors run locally.
          </p>
        </div>

        {/* Highlighted Status Cards */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="px-4 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-3">
            <Server className="w-5 h-5 text-emerald-400" />
            <div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">System Mode</span>
              <span className="text-xs font-bold text-emerald-400">LOCAL / ON-PREMISE</span>
            </div>
          </div>

          <div className="px-4 py-2.5 rounded-xl bg-slate-950 border border-emerald-500/30 flex items-center gap-3">
            <Radio className="w-5 h-5 text-emerald-400 animate-pulse" />
            <div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">Network Guard</span>
              <span className="text-xs font-bold text-emerald-400 font-mono">External Network Calls: 0</span>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatusCard
          title="On-Premise Status"
          value="100% Isolated"
          subtitle="Zero Telemetry / Air-Gapped"
          icon={Lock}
          color="emerald"
          trend="Secured Local Host"
        />
        <StatusCard
          title="Active Model"
          value={status.activeModel}
          subtitle={`VRAM: ${status.gpuVramUsed}`}
          icon={Cpu}
          color="cyan"
          trend="Quantized Local LLM"
        />
        <StatusCard
          title="Indexed Documents"
          value={`${docs.length} Confidential Files`}
          subtitle={`${status.indexedChunksTotal} Vector Chunks`}
          icon={Database}
          color="blue"
          trend="ChromaDB RAG Engine"
        />
        <StatusCard
          title="Available Local LLMs"
          value={`${status.availableModelsCount} Models`}
          subtitle="Qwen3 4B, 8B, 14B"
          icon={Bot}
          color="amber"
          trend="Open-Weight Multimodal"
        />
      </div>

      {/* Action Shortcuts */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => navigate('/chat')}
          className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-cyan-500/40 hover:bg-slate-800/60 transition-all text-left group shadow-lg"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <MessageSquareText className="w-5 h-5" />
            </div>
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all" />
          </div>
          <h3 className="text-sm font-bold text-slate-100">Launch Confidential AI Chat</h3>
          <p className="text-xs text-slate-400 mt-1">Interact with Qwen3 LLMs on air-gapped internal SOPs.</p>
        </button>

        <button
          onClick={() => navigate('/documents')}
          className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-emerald-500/40 hover:bg-slate-800/60 transition-all text-left group shadow-lg"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <FileText className="w-5 h-5" />
            </div>
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all" />
          </div>
          <h3 className="text-sm font-bold text-slate-100">Upload Technical Documents</h3>
          <p className="text-xs text-slate-400 mt-1">Ingest PDFs, logs, and maintenance manuals into RAG.</p>
        </button>

        <button
          onClick={() => navigate('/agents')}
          className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-blue-500/40 hover:bg-slate-800/60 transition-all text-left group shadow-lg"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="p-3 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Bot className="w-5 h-5" />
            </div>
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
          </div>
          <h3 className="text-sm font-bold text-slate-100">Execute Agent Workflow</h3>
          <p className="text-xs text-slate-400 mt-1">Run automated Inspection Report → Approval Note pipeline.</p>
        </button>
      </div>

      {/* Recent Activity Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Agent Tasks */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">Recent Agent Tasks</h3>
            </div>
            <button
              onClick={() => navigate('/agents')}
              className="text-xs text-cyan-400 hover:underline font-semibold"
            >
              View All Tasks
            </button>
          </div>

          <div className="space-y-3">
            {tasks.map((task) => (
              <div key={task.id} className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between gap-3">
                <div>
                  <h4 className="text-xs font-bold text-slate-200">{task.title}</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Source: <span className="text-cyan-300 font-mono">{task.sourceDocument}</span>
                  </p>
                </div>
                <div className="text-right">
                  <Badge variant={task.status === 'Completed' ? 'emerald' : 'amber'}>
                    {task.status}
                  </Badge>
                  <span className="text-[10px] text-slate-500 block mt-1 font-mono">{task.createdAt}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Generated Deliverables */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FolderArchive className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">Recent Generated Files</h3>
            </div>
            <button
              onClick={() => navigate('/files')}
              className="text-xs text-emerald-400 hover:underline font-semibold"
            >
              View Repository
            </button>
          </div>

          <div className="space-y-3">
            {files.slice(0, 3).map((file) => (
              <div key={file.id} className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded bg-slate-900 border border-slate-700 text-cyan-400">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-200 font-mono">{file.name}</h4>
                    <p className="text-[11px] text-slate-400">{file.category}</p>
                  </div>
                </div>
                <div className="text-right">
                  <Badge variant="cyan" className="font-mono text-[10px]">
                    {file.type}
                  </Badge>
                  <span className="text-[10px] text-slate-500 block mt-1 font-mono">{file.size}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Security Status Footprint */}
      <div className="p-5 rounded-xl bg-slate-950 border border-emerald-500/30 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-100">Security & Confidentiality Verification</h4>
            <p className="text-xs text-slate-400 mt-0.5">
              Local ChromaDB vector index encrypted. Zero outbound HTTP telemetry. Compatible with defense & refinery compliance standards.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="emerald" className="py-1 px-3 text-xs">
            DATA PROCESSING: ON-PREMISE
          </Badge>
          <Badge variant="rose" className="py-1 px-3 text-xs">
            CLOUD API: DISABLED
          </Badge>
        </div>
      </div>
    </div>
  );
};
