import React, { useState, useEffect } from 'react';
import {
  Cpu,
  ShieldCheck,
  Activity,
  Code,
  Eye,
  FileText,
  HardDrive
} from 'lucide-react';

import { Badge } from '../components/common/Badge';
import { getModels } from '../services/api';


export const ModelsPage = () => {

  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);


  // --------------------------------------------------
  // Load Real Ollama Models
  // --------------------------------------------------

  useEffect(() => {
    loadModels();
  }, []);


  const loadModels = async () => {

    try {

      setLoading(true);

      const data = await getModels();

      setModels(data);

    } catch (error) {

      console.error('Failed to load models:', error);

    } finally {

      setLoading(false);

    }
  };


  // --------------------------------------------------
  // Find Primary Local Model
  // --------------------------------------------------

  const primaryModel =
    models.find((model) =>
      model.name.toLowerCase().includes('qwen2.5-coder')
    ) || models[0];


  // --------------------------------------------------
  // Model Information
  // --------------------------------------------------

  const getModelInfo = (modelName) => {

    const name = modelName.toLowerCase();

    if (name.includes('qwen2.5-coder')) {

      return {
        task: 'Coding',
        description:
          'Local coding model for programming and automation tasks.',
        icon: <Code className="w-4 h-4" />,
        variant: 'cyan'
      };

    }

    if (name.includes('gemma3')) {

      return {
        task: 'Vision / Multimodal',
        description:
          'Local multimodal model for image and visual analysis.',
        icon: <Eye className="w-4 h-4" />,
        variant: 'amber'
      };

    }

    if (name.includes('llama3.2')) {

      return {
        task: 'General / Documents',
        description:
          'Local general-purpose model for text and document tasks.',
        icon: <FileText className="w-4 h-4" />,
        variant: 'emerald'
      };

    }

    return {
      task: 'General',
      description:
        'Local open-weight model available through Ollama.',
      icon: <Cpu className="w-4 h-4" />,
      variant: 'slate'
    };
  };


  // --------------------------------------------------
  // Format Model Size
  // --------------------------------------------------

  const formatSize = (bytes) => {

    if (!bytes) {
      return 'Unknown';
    }

    if (bytes < 1024 * 1024 * 1024) {

      return `${(bytes / (1024 * 1024)).toFixed(0)} MB`;

    }

    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  };


  return (

    <div className="p-6 space-y-6">


      {/* --------------------------------------------------
          Header
      -------------------------------------------------- */}

      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-5">

          <div>

            <div className="flex items-center gap-2">

              <Cpu className="w-6 h-6 text-cyan-400" />

              <h2 className="text-xl font-bold text-slate-100">
                Local Open-Weight Model Registry
              </h2>

            </div>

            <p className="text-xs text-slate-400 mt-1 max-w-xl">
              Models currently installed in the local Ollama runtime.
              No cloud API keys are required.
            </p>

          </div>


          {/* Primary Model */}

          <div className="bg-slate-950 border border-slate-800 rounded-xl px-5 py-3 min-w-[250px]">

            <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">
              Router Primary Model
            </div>

            <div className="flex items-center gap-2 mt-1">

              <div className="w-2 h-2 rounded-full bg-emerald-400" />

              <span className="text-sm font-bold text-slate-100">

                {loading
                  ? 'Loading...'
                  : primaryModel
                    ? primaryModel.name
                    : 'No model available'}

              </span>

            </div>

            <div className="text-[10px] text-emerald-400 mt-1">
              LOCAL / OLLAMA
            </div>

          </div>

        </div>

      </div>


      {/* --------------------------------------------------
          Local Status
      -------------------------------------------------- */}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">

          <div className="flex items-center gap-2">

            <ShieldCheck className="w-4 h-4 text-emerald-400" />

            <span className="text-xs font-semibold text-slate-300">
              Runtime
            </span>

          </div>

          <p className="text-sm font-bold text-emerald-400 mt-2">
            Ollama Local
          </p>

        </div>


        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">

          <div className="flex items-center gap-2">

            <HardDrive className="w-4 h-4 text-cyan-400" />

            <span className="text-xs font-semibold text-slate-300">
              Installed Models
            </span>

          </div>

          <p className="text-sm font-bold text-cyan-400 mt-2">
            {loading ? '...' : models.length}
          </p>

        </div>


        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">

          <div className="flex items-center gap-2">

            <ShieldCheck className="w-4 h-4 text-emerald-400" />

            <span className="text-xs font-semibold text-slate-300">
              API Dependency
            </span>

          </div>

          <p className="text-sm font-bold text-emerald-400 mt-2">
            None
          </p>

        </div>

      </div>


      {/* --------------------------------------------------
          Router Visualization
      -------------------------------------------------- */}

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">

        <div className="flex items-center justify-between border-b border-slate-800 pb-3">

          <div className="flex items-center gap-2">

            <Activity className="w-5 h-5 text-emerald-400" />

            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Local Model Router Dispatcher
            </h3>

          </div>

          <Badge variant="emerald">
            AUTOMATIC DYNAMIC ROUTING
          </Badge>

        </div>


        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">


          {/* Coding */}

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">

            <div className="flex items-center gap-2 text-cyan-400 font-semibold text-xs">

              <Code className="w-4 h-4" />

              <span>Coding Task</span>

            </div>

            <div className="flex items-center gap-2 text-xs text-slate-300 pt-1">

              <span className="font-bold text-slate-100">
                qwen2.5-coder:3b
              </span>

            </div>

            <p className="text-[11px] text-slate-400">
              Used by the local router for coding and programming tasks.
            </p>

          </div>


          {/* Documents */}

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">

            <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">

              <FileText className="w-4 h-4" />

              <span>General / Document Task</span>

            </div>

            <div className="flex items-center gap-2 text-xs text-slate-300 pt-1">

              <span className="font-bold text-slate-100">
                llama3.2:3b
              </span>

            </div>

            <p className="text-[11px] text-slate-400">
              Used for general text and document-oriented requests.
            </p>

          </div>


          {/* Vision */}

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">

            <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs">

              <Eye className="w-4 h-4" />

              <span>Multimodal / Image Task</span>

            </div>

            <div className="flex items-center gap-2 text-xs text-slate-300 pt-1">

              <span className="font-bold text-slate-100">
                gemma3:4b
              </span>

            </div>

            <p className="text-[11px] text-slate-400">
              Used by the local vision endpoint for image analysis.
            </p>

          </div>

        </div>

      </div>


      {/* --------------------------------------------------
          Real Ollama Models
      -------------------------------------------------- */}

      <div>

        <div className="flex items-center gap-2 mb-4">

          <HardDrive className="w-5 h-5 text-cyan-400" />

          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
            Installed Local Models
          </h3>

        </div>


        {loading ? (

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center">

            <p className="text-sm text-slate-400">
              Loading Ollama models...
            </p>

          </div>

        ) : models.length === 0 ? (

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center">

            <p className="text-sm text-rose-400">
              No local Ollama models found.
            </p>

          </div>

        ) : (

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            {models.map((model) => {

              const info = getModelInfo(model.name);

              return (

                <div
                  key={model.name}
                  className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between space-y-5"
                >

                  <div>

                    <div className="flex items-start justify-between gap-3">

                      <div>

                        <h3 className="text-lg font-bold text-slate-100">
                          {model.name}
                        </h3>

                        <p className="text-xs text-slate-400 mt-1">
                          Ollama Local Model
                        </p>

                      </div>

                      <Badge variant="emerald">
                        Installed
                      </Badge>

                    </div>


                    <div className="mt-4 p-3 rounded-xl bg-slate-950 border border-slate-800">

                      <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">

                        {info.icon}

                        <span>
                          {info.task}
                        </span>

                      </div>

                      <p className="text-[11px] text-slate-400 mt-2">
                        {info.description}
                      </p>

                    </div>


                    <div className="mt-4 pt-3 border-t border-slate-800 space-y-2 text-xs font-mono">

                      <div className="flex justify-between">

                        <span className="text-slate-400">
                          Model Size:
                        </span>

                        <span className="text-cyan-400 font-bold">
                          {formatSize(model.size)}
                        </span>

                      </div>


                      <div className="flex justify-between">

                        <span className="text-slate-400">
                          Runtime:
                        </span>

                        <span className="text-slate-200">
                          Ollama
                        </span>

                      </div>


                      <div className="flex justify-between">

                        <span className="text-slate-400">
                          Location:
                        </span>

                        <span className="text-emerald-400">
                          Local
                        </span>

                      </div>

                    </div>

                  </div>


                  <div className="pt-4 border-t border-slate-800 flex items-center gap-2 text-[10px] text-emerald-400 font-semibold">

                    <ShieldCheck className="w-3 h-3" />

                    <span>
                      LOCAL OLLAMA MODEL
                    </span>

                  </div>

                </div>

              );

            })}

          </div>

        )}

      </div>

    </div>

  );
};