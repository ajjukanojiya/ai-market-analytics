import React from 'react';
import { Activity, LayoutDashboard, LineChart, BrainCircuit, Settings, LogOut } from 'lucide-react';

export function Sidebar() {
  return (
    <aside className="hidden md:flex flex-col w-20 xl:w-64 h-screen sticky top-0 bg-[#09090b]/80 backdrop-blur-xl border-r border-white/5 pt-6 pb-4 transition-all duration-300 z-50">
      
      {/* Logo Area */}
      <div className="flex items-center justify-center xl:justify-start xl:px-6 mb-10">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-[0_0_15px_rgba(59,130,246,0.5)]">
          <Activity size={24} className="text-white" />
        </div>
        <span className="hidden xl:block ml-3 font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">
          QuantAI
        </span>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 px-4 space-y-3">
        <a href="#" className="flex items-center justify-center xl:justify-start xl:px-4 py-3 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 group transition-all">
          <LayoutDashboard size={22} className="group-hover:scale-110 transition-transform" />
          <span className="hidden xl:block ml-3 font-medium">Dashboard</span>
        </a>
      </nav>

    </aside>
  );
}
