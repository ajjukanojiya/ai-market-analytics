"use client";

import React, { useState } from 'react';
import { ArrowUpRight, ArrowDownRight, CheckCircle2, XCircle, Filter, TrendingUp, MinusCircle } from 'lucide-react';

interface PredictionHistoryItem {
  date: string;
  time: string;
  symbol: string;
  signal: string;
  confidence: number;
  status: string;
  margin: number;
  entry_price?: number;
  expected_close?: number;
}

export function RecentPredictionsTable({ data = [] }: { data?: PredictionHistoryItem[] }) {
  const [filter, setFilter] = useState('All');

  // Helper to format date beautifully
  const formatDateTime = (dateStr: string, timeStr: string) => {
    const itemDate = new Date(dateStr);
    const today = new Date('2026-07-08'); // Reference date
    const diffTime = today.getTime() - itemDate.getTime();
    const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24)); 
    
    let dayLabel = dateStr;
    if (diffDays === 0) dayLabel = `Today (${dateStr})`;
    else if (diffDays === 1) dayLabel = `Yesterday (${dateStr})`;

    return (
      <div className="flex flex-col">
        <span className="text-sm text-gray-200 font-medium">{dayLabel}</span>
        <span className="text-xs text-muted-foreground">{timeStr}</span>
      </div>
    );
  };

  const filteredData = data.filter(item => {
    if (filter === 'Today') return item.date === '2026-07-08';
    if (filter === 'Yesterday') return item.date === '2026-07-07';
    return true;
  });

  // Calculate stats based on filtered data
  const totalSignals = filteredData.length;
  const wins = filteredData.filter(d => d.status === 'WIN').length;
  const losses = filteredData.filter(d => d.status === 'LOSS').length;
  const netMargin = filteredData.reduce((acc, curr) => acc + curr.margin, 0);

  return (
    <div className="glass-panel p-6 rounded-2xl w-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-300 flex items-center gap-2">
          <TrendingUp size={20} className="text-blue-400"/> Signal History
        </h2>
        
        <div className="flex items-center gap-3">
          <div className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 flex items-center gap-2 hover:bg-white/10 transition-colors">
            <Filter size={14} className="text-blue-400" />
            <select 
              className="bg-transparent text-xs text-gray-300 font-medium outline-none cursor-pointer appearance-none pr-2"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="All" className="bg-[#18181b]">All Time</option>
              <option value="Today" className="bg-[#18181b]">Today</option>
              <option value="Yesterday" className="bg-[#18181b]">Yesterday</option>
            </select>
          </div>
        </div>
      </div>

      {/* Summary Stats Bar */}
      <div className="grid grid-cols-4 gap-4 mb-6 bg-white/5 border border-white/10 rounded-xl p-4">
        <div className="flex flex-col">
          <span className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Total Signals</span>
          <span className="text-xl font-bold text-gray-200">{totalSignals}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Winning Signals</span>
          <span className="text-xl font-bold text-green-400">{wins}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Losing Signals</span>
          <span className="text-xl font-bold text-red-400">{losses}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Net Margin (Pts)</span>
          <span className={`text-xl font-bold ${netMargin >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {netMargin >= 0 ? '+' : ''}{netMargin.toFixed(1)}
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/10 text-xs uppercase tracking-wider text-muted-foreground">
              <th className="pb-3 px-4 font-medium">Date & Time</th>
              <th className="pb-3 px-4 font-medium">Symbol</th>
              <th className="pb-3 px-4 font-medium">AI Signal</th>
              <th className="pb-3 px-4 font-medium">Margin (Pts)</th>
              <th className="pb-3 px-4 font-medium">Confidence</th>
              <th className="pb-3 px-4 font-medium text-right">Result</th>
            </tr>
          </thead>
          <tbody>
            {filteredData.length > 0 ? filteredData.map((row, idx) => (
              <tr key={idx} className="border-b border-white/5 hover:bg-white/[0.04] transition-colors group cursor-default">
                <td className="py-3 px-4">
                  {formatDateTime(row.date, row.time)}
                </td>
                <td className="py-3 px-4 font-mono text-sm text-gray-200">{row.symbol}</td>
                <td className="py-3 px-4">
                  {row.signal === 'NEUTRAL' ? (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                      WAIT (NEUTRAL)
                    </span>
                  ) : (
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold ${row.signal === 'BUY' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                      {row.signal === 'BUY' ? <ArrowUpRight size={14} className="mr-1" /> : <ArrowDownRight size={14} className="mr-1" />}
                      {row.signal === 'BUY' ? 'BUY (CALL)' : 'SELL (PUT)'}
                    </span>
                  )}
                </td>
                <td className="py-3 px-4">
                  <div className="flex flex-col gap-1 items-start">
                    <span className={`font-mono text-sm px-2 py-1 rounded-md ${row.margin > 0 ? 'bg-green-500/10 text-green-400 border border-green-500/10' : 'bg-red-500/10 text-red-400 border border-red-500/10'}`}>
                      {row.margin > 0 ? '+' : ''}{row.margin}
                    </span>
                    {row.entry_price && row.expected_close && (
                      <span className="text-[10px] text-muted-foreground mt-1 opacity-70 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                        Entry: ₹{row.entry_price.toFixed(2)} → Target: ₹{row.expected_close.toFixed(2)}
                      </span>
                    )}
                  </div>
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <div className={`h-full ${row.confidence > 80 ? 'bg-green-500' : 'bg-yellow-500'}`} style={{ width: `${row.confidence}%` }}></div>
                    </div>
                    <span className="text-xs font-mono text-gray-300">{row.confidence}%</span>
                  </div>
                </td>
                <td className="py-3 px-4 text-right">
                  {row.status === 'WIN' ? (
                    <span className="inline-flex items-center text-green-500 text-sm font-medium">
                      <CheckCircle2 size={16} className="mr-1" /> Win
                    </span>
                  ) : row.status === 'LOSS' ? (
                    <span className="inline-flex items-center text-red-500 text-sm font-medium">
                      <XCircle size={16} className="mr-1" /> Loss
                    </span>
                  ) : (
                    <span className="inline-flex items-center text-yellow-500 text-sm font-medium">
                      <MinusCircle size={16} className="mr-1" /> Wait
                    </span>
                  )}
                </td>
              </tr>
            )) : (
              <tr>
                <td colSpan={6} className="py-8 text-center text-muted-foreground text-sm">
                  No signals found for the selected period.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
