import React from 'react';

export const StatusCard = ({ title, value, subtitle, icon: Icon, trend, color = 'emerald' }) => {
  const colorBorders = {
    emerald: 'border-emerald-500/20 hover:border-emerald-500/40 glow-emerald',
    cyan: 'border-cyan-500/20 hover:border-cyan-500/40 glow-cyan',
    blue: 'border-blue-500/20 hover:border-blue-500/40',
    amber: 'border-amber-500/20 hover:border-amber-500/40',
  };

  const iconColors = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  };

  return (
    <div className={`bg-slate-900/80 backdrop-blur-md rounded-xl p-5 border ${colorBorders[color] || 'border-slate-800'} transition-all duration-300`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        {Icon && (
          <div className={`p-2.5 rounded-lg border ${iconColors[color] || 'bg-slate-800 text-slate-300'}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      
      <div className="mt-3">
        <h3 className="text-2xl font-bold text-slate-100 tracking-tight">{value}</h3>
        {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
      </div>

      {trend && (
        <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center gap-1.5 text-xs text-emerald-400">
          <span>{trend}</span>
        </div>
      )}
    </div>
  );
};
