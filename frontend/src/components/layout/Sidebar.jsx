import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  MessageSquareText, 
  FileText, 
  Database, 
  Bot, 
  Cpu, 
  FolderArchive, 
  Settings, 
  ShieldCheck, 
  Lock 
} from 'lucide-react';

export const Sidebar = () => {
  const navItems = [
    { label: 'Dashboard', path: '/', icon: LayoutDashboard },
    { label: 'AI Chat', path: '/chat', icon: MessageSquareText },
    { label: 'Documents', path: '/documents', icon: FileText },
    { label: 'Knowledge Base', path: '/knowledge', icon: Database },
    { label: 'Agent Tasks', path: '/agents', icon: Bot },
    { label: 'Models', path: '/models', icon: Cpu },
    { label: 'Generated Files', path: '/files', icon: FolderArchive },
    { label: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen sticky top-0 z-30 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="p-2.5 rounded-xl bg-gradient-to-tr from-emerald-600 to-cyan-500 text-slate-950 shadow-md shadow-emerald-500/10">
          <ShieldCheck className="w-6 h-6 stroke-[2.5]" />
        </div>
        <div>
          <h1 className="text-base font-bold text-slate-100 tracking-tight leading-none">SOVEREIGN AI</h1>
          <p className="text-[10px] font-semibold text-emerald-400 uppercase tracking-widest mt-1">Air-Gapped Workbench</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
          Main Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Air-Gap Status Box */}
      <div className="p-4 m-3 rounded-xl bg-slate-950/80 border border-emerald-500/20 text-xs">
        <div className="flex items-center gap-2 text-emerald-400 font-semibold mb-1">
          <Lock className="w-3.5 h-3.5" />
          <span>CONFIDENTIAL INDUSTRIAL</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-tight">
          100% On-Premise Execution. Zero External API Calls.
        </p>
        <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400">
          <span>Status:</span>
          <span className="flex items-center gap-1 text-emerald-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-status-pulse"></span>
            AIR-GAPPED
          </span>
        </div>
      </div>
    </aside>
  );
};
