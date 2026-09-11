import React from 'react';
import {
  CheckCircle2,
  Clock,
  Terminal,
  FileText,
  ArrowRight,
  ShieldCheck,
  Download
} from 'lucide-react';

import { Badge } from '../common/Badge';

export const AgentWorkflow = ({ task }) => {

  const stages = [
    {
      name: 'Plan',
      desc: 'Agent decomposes goal into tool calls'
    },
    {
      name: 'Retrieve',
      desc: 'Queries local RAG vector embeddings'
    },
    {
      name: 'Analyze',
      desc: 'Processes technical parameters & SOPs'
    },
    {
      name: 'Execute',
      desc: 'Generates structured compliance draft'
    },
    {
      name: 'Verify',
      desc: 'Validates against regulatory rules'
    },
    {
      name: 'Deliver',
      desc: 'Exports air-gapped output file'
    }
  ];


  if (!task) {
    return null;
  }


  const currentStageIndex =
    typeof task.stageIndex === 'number'
      ? task.stageIndex
      : 0;


  const handleDownload = () => {

    if (!task.outputFile) {

      alert('No deliverable file is available.');

      return;

    }


    const filename = encodeURIComponent(
      task.outputFile
    );


    window.open(
      `http://127.0.0.1:8000/deliverables/download/${filename}`,
      '_blank'
    );

  };


  return (

    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">


      {/* =====================================================
          WORKFLOW HEADER
      ===================================================== */}

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">

        <div>

          <div className="flex items-center gap-2">

            <h3 className="text-lg font-bold text-slate-100">
              {task.title}
            </h3>

            <Badge
              variant={
                task.status === 'Completed'
                  ? 'emerald'
                  : 'cyan'
              }
            >
              {task.status}
            </Badge>

          </div>


          <p className="text-xs text-slate-400 mt-1">

            Source Input:

            <span className="text-cyan-300 font-mono ml-1">
              {task.sourceDocument || 'None'}
            </span>

            <span className="mx-1">
              |
            </span>

            Target Output:

            <span className="text-emerald-400 font-mono ml-1">
              {task.outputFormat || 'AI Generated'}
            </span>

          </p>

        </div>


        {/* Progress */}

        <div className="flex items-center gap-3">

          <div className="text-right">

            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
              Progress
            </span>

            <span className="text-lg font-bold text-cyan-400 font-mono">
              {task.progress ?? 0}%
            </span>

          </div>


          <div className="w-24 bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">

            <div
              className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-full rounded-full transition-all duration-500"
              style={{
                width: `${task.progress ?? 0}%`
              }}
            />

          </div>

        </div>

      </div>


      {/* =====================================================
          STAGE PIPELINE
      ===================================================== */}

      <div className="space-y-2">

        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Agentic Execution Pipeline
        </h4>


        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">

          {stages.map((stage, idx) => {

            const isCompleted =
              idx <= currentStageIndex;

            const isCurrent =
              idx === currentStageIndex &&
              task.status !== 'Completed';


            return (

              <div
                key={stage.name}
                className={`p-3 rounded-lg border flex flex-col justify-between transition-all ${
                  isCurrent
                    ? 'bg-cyan-500/10 border-cyan-500/50 shadow-md shadow-cyan-500/10'
                    : isCompleted
                    ? 'bg-slate-950 border-emerald-500/30'
                    : 'bg-slate-950/40 border-slate-800 text-slate-500'
                }`}
              >

                <div className="flex items-center justify-between mb-1">

                  <span className="text-xs font-bold font-mono">
                    {idx + 1}. {stage.name}
                  </span>


                  {isCompleted ? (

                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />

                  ) : isCurrent ? (

                    <Clock className="w-4 h-4 text-cyan-400 animate-spin shrink-0" />

                  ) : (

                    <div className="w-3 h-3 rounded-full border border-slate-700" />

                  )}

                </div>


                <p className="text-[10px] text-slate-400 leading-tight">
                  {stage.desc}
                </p>

              </div>

            );

          })}

        </div>

      </div>


      {/* =====================================================
          TOOL CALL LOG
      ===================================================== */}

      <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 font-mono text-xs space-y-3">

        <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">

          <div className="flex items-center gap-2 text-cyan-400 font-semibold">

            <Terminal className="w-4 h-4" />

            <span>
              Local Tool Execution Log (
              {task.toolCalls?.length || 0}
              {' '}calls)
            </span>

          </div>


          <span className="text-[10px] text-slate-500">
            Sandbox Isolation: Active
          </span>

        </div>


        <div className="space-y-2 max-h-48 overflow-y-auto pr-1">

          {task.toolCalls &&
          task.toolCalls.length > 0 ? (

            task.toolCalls.map((call, idx) => (

              <div
                key={idx}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-[11px] bg-slate-900/60 p-2 rounded border border-slate-800/60"
              >

                <div className="flex items-center gap-2">

                  <span className="text-slate-500">
                    {call.timestamp}
                  </span>

                  <span className="text-cyan-300 font-bold">
                    [{call.name}]
                  </span>

                  <span className="text-slate-300">
                    {call.result}
                  </span>

                </div>


                <Badge
                  variant={
                    call.status === 'Success'
                      ? 'emerald'
                      : 'cyan'
                  }
                  className="text-[10px] py-0"
                >
                  {call.status}
                </Badge>

              </div>

            ))

          ) : (

            <p className="text-slate-500 text-[11px]">
              No tool calls recorded.
            </p>

          )}

        </div>

      </div>


      {/* =====================================================
          OUTPUT DELIVERABLE
      ===================================================== */}

      <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex flex-col sm:flex-row items-center justify-between gap-3">

        <div className="flex items-center gap-3">

          <div className="p-2 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">

            <FileText className="w-5 h-5" />

          </div>


          <div>

            <h5 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
              Generated Deliverable File
            </h5>


            <p className="text-sm font-bold text-emerald-400 font-mono mt-0.5">

              {task.outputFile || 'No file generated'}

            </p>

          </div>

        </div>


        {/* Download */}

        <button
          onClick={handleDownload}
          disabled={!task.outputFile}
          className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-700 disabled:text-slate-500 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-colors shadow-md shadow-emerald-500/20 disabled:cursor-not-allowed"
        >

          <Download className="w-3.5 h-3.5" />

          <span>
            Download Confidential Output
          </span>

          <ArrowRight className="w-3.5 h-3.5" />

        </button>

      </div>


      {/* =====================================================
          LOCAL SECURITY NOTICE
      ===================================================== */}

      <div className="flex items-center gap-2 text-[10px] text-emerald-400 font-semibold">

        <ShieldCheck className="w-3.5 h-3.5" />

        <span>
          PROCESSING COMPLETED USING LOCAL SOVEREIGN AI BACKEND
        </span>

      </div>

    </div>

  );

};