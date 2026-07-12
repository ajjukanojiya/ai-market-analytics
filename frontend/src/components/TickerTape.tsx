import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface TickerData {
  symbol: string;
  price: number;
  change: number;
  isUp: boolean;
}

const STATIC_TICKERS = [
  { symbol: 'TCS', price: 3950.10, change: -0.55, isUp: false },
  { symbol: 'INFY', price: 1640.80, change: 0.89, isUp: true },
  { symbol: 'HDFCBANK', price: 1630.25, change: 0.15, isUp: true },
  { symbol: 'SBIN', price: 845.60, change: 1.10, isUp: true },
  { symbol: 'ITC', price: 425.30, change: -0.30, isUp: false },
];

export function TickerTape() {
  const [liveTickers, setLiveTickers] = useState<TickerData[]>([]);

  useEffect(() => {
    let ws: WebSocket;
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    
    const connectWs = () => {
      ws = new WebSocket(`${WS_URL}/api/v1/ws/market-data`);
      
      ws.onmessage = (event) => {
        try {
          const res = JSON.parse(event.data);
          if (res.status === 'live' && res.data) {
            const formatted = res.data.map((item: any) => ({
              symbol: item.symbol,
              price: item.ltp,
              change: item.change_pct,
              isUp: item.change_pct >= 0
            }));
            
            // Merge with existing live tickers to keep non-updated ones
            setLiveTickers(prev => {
              const updated = [...prev];
              formatted.forEach((newT: any) => {
                const idx = updated.findIndex(t => t.symbol === newT.symbol);
                if (idx >= 0) updated[idx] = newT;
                else updated.push(newT);
              });
              return updated;
            });
          }
        } catch (err) {
          console.error("WS Parse error", err);
        }
      };

      ws.onclose = () => {
        // Reconnect after 1 second
        setTimeout(connectWs, 1000);
      };
    };

    connectWs();
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const displayTickers = liveTickers.length > 0 ? [...liveTickers, ...STATIC_TICKERS] : STATIC_TICKERS;

  return (
    <div className="w-full bg-[#09090b] border-b border-white/5 h-10 overflow-hidden flex items-center shrink-0">
      <div className="whitespace-nowrap animate-marquee flex items-center">
        {/* Double the array to ensure continuous scrolling */}
        {[...displayTickers, ...displayTickers].map((ticker, index) => (
          <div key={index} className="flex items-center mx-6 text-sm font-medium">
            <span className="text-gray-300 mr-2">{ticker.symbol}</span>
            <span className={`mr-2 font-mono transition-colors duration-200 ${ticker.isUp ? 'text-green-300' : 'text-red-300'}`}>₹{ticker.price.toFixed(2)}</span>
            <span className={`flex items-center ${ticker.isUp ? 'text-green-500' : 'text-red-500'}`}>
              {ticker.isUp ? <ArrowUpRight size={14} className="mr-0.5" /> : <ArrowDownRight size={14} className="mr-0.5" />}
              {Math.abs(ticker.change)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
