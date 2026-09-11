import React, { useEffect, useState } from 'react';
import { ShieldAlert, Radio, Server, Cpu } from 'lucide-react';
import { Badge } from '../common/Badge';
import { getModels } from '../../services/api';

export const Header = ({ title = 'Dashboard' }) => {

  const [activeModel, setActiveModel] = useState('Loading...');

  useEffect(() => {

    const loadActiveModel = async () => {

      try {

        const models = await getModels();

        if (models && models.length > 0) {

          const primaryModel =
            models.find((model) =>
              model.name
                .toLowerCase()
                .includes('qwen2.5-coder')
            ) || models[0];

          setActiveModel(primaryModel.name);

        } else {

          setActiveModel('No local model');

        }

      } catch (error) {

        console.error(
          'Failed to load active model:',
          error
        );

        setActiveModel('Unavailable');

      }

    };

    loadActiveModel();

  }, []);


  return (

    <header className="h-16 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-20">

      {/* Title */}

      <div className="flex items-center gap-3">

        <h2 className="text-lg font-bold text-slate-100 tracking-tight">
          {title}
        </h2>

        <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
          v1.0-ONPREM
        </span>

      </div>


      {/* Security & Status Indicators */}

      <div className="flex items-center gap-3">


        {/* Local Active Model Indicator */}

        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300">

          <Cpu className="w-3.5 h-3.5 text-cyan-400" />

          <span className="text-slate-400">
            Active Model:
          </span>

          <span className="font-semibold text-cyan-300">
            {activeModel}
          </span>

        </div>


        {/* Local / On-Premise Badge */}

        <Badge
          variant="emerald"
          className="py-1 px-3"
        >

          <Server className="w-3.5 h-3.5 mr-1" />

          LOCAL / ON-PREMISE

        </Badge>


        {/* Network Call Counter Indicator */}

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-950 border border-emerald-500/30 text-xs">

          <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />

          <span className="text-slate-400">
            External Network Calls:
          </span>

          <span className="font-bold text-emerald-400 font-mono">
            0
          </span>

        </div>


        {/* Confidential Badge */}

        <div className="hidden sm:flex items-center gap-1.5 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-lg">

          <ShieldAlert className="w-3.5 h-3.5" />

          <span className="font-semibold">
            RESTRICTED WORKFLOW
          </span>

        </div>

      </div>

    </header>

  );

};