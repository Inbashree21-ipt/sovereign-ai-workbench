import React from 'react';

export const Badge = ({ children, variant = 'emerald', className = '' }) => {
  const variantStyles = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    slate: 'bg-slate-800 text-slate-300 border-slate-700'
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-medium rounded-full border ${variantStyles[variant] || variantStyles.slate} ${className}`}>
      {children}
    </span>
  );
};
