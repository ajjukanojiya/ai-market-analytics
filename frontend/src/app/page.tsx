"use client";

import { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { ArrowUpCircle, ArrowDownCircle, Activity, Clock, Zap, TrendingUp, ShieldAlert } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface Prediction {
  predicted_direction: string;
  confidence_score: number;
  expected_close: number;
  entry_price: number;
  timestamp: string;
}

interface MarketData {
  timestamp: string;
  close: number;
  open: number;
  high: number;
  low: number;
}

export default function Dashboard() {
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const predRes = await axios.get('http://localhost:8000/api/v1/predictions/latest');
      if (predRes.data.prediction) {
        setPrediction(predRes.data.prediction);
      }

      const marketRes = await axios.get('http://localhost:8000/api/v1/market-data/latest');
      if (marketRes.data.data) {
        setMarketData(marketRes.data.data);
      }
      
      setError(null);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError("Failed to connect to AI Engine. Is the FastAPI server running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const chartData = {
    labels: marketData.map(d => new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'NIFTY 50 (5m Close)',
        data: marketData.map(d => d.close),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { mode: 'index' as const, intersect: false, backgroundColor: '#18181b', titleColor: '#a1a1aa', bodyColor: '#fafafa', borderColor: '#27272a', borderWidth: 1 }
    },
    scales: {
      x: { grid: { display: false, color: '#27272a' }, ticks: { color: '#a1a1aa' } },
      y: { grid: { color: '#27272a' }, ticks: { color: '#a1a1aa' } }
    },
    interaction: { mode: 'nearest' as const, axis: 'x' as const, intersect: false }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-primary animate-pulse-slow">
          <Zap size={48} className="animate-bounce" />
          <p className="text-xl font-medium tracking-widest uppercase">Initializing AI Engine...</p>
        </div>
      </div>
    );
  }

  const isBuy = prediction?.predicted_direction === 'BUY';

  return (
    <main className="min-h-screen p-6 md:p-10 max-w-7xl mx-auto">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500 flex items-center gap-3">
            <Activity className="text-blue-500" size={32} />
            AI Market Analytics
          </h1>
          <p className="text-muted-foreground mt-1">Enterprise Quant Trading Dashboard</p>
        </div>
        <div className="glass-panel px-4 py-2 rounded-full flex items-center gap-3 text-sm font-medium">
          <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.6)]"></div>
          System Online
        </div>
      </header>

      {error && (
        <div className="glass-panel border-red-500/30 bg-red-500/10 p-4 rounded-xl flex items-center gap-3 text-red-400 mb-8">
          <ShieldAlert size={24} />
          <p>{error}</p>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: AI Prediction Card */}
        <div className="lg:col-span-1 space-y-8">
          <div className="glass-panel p-6 rounded-2xl relative overflow-hidden group hover:border-white/10 transition-colors">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-50"></div>
            
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold text-gray-300 flex items-center gap-2">
                <Zap size={20} className="text-yellow-400" /> Live AI Signal
              </h2>
              <span className="text-xs text-muted-foreground flex items-center gap-1 bg-white/5 px-2 py-1 rounded-md">
                <Clock size={12} /> {prediction ? new Date(prediction.timestamp).toLocaleTimeString() : '--:--'}
              </span>
            </div>

            {prediction ? (
              <div className="flex flex-col items-center justify-center py-6">
                {isBuy ? (
                  <ArrowUpCircle size={80} className="text-green-500 drop-shadow-[0_0_15px_rgba(16,185,129,0.5)] mb-4" />
                ) : (
                  <ArrowDownCircle size={80} className="text-red-500 drop-shadow-[0_0_15px_rgba(239,68,68,0.5)] mb-4" />
                )}
                
                <h3 className={`text-5xl font-extrabold tracking-tight mb-2 ${isBuy ? 'text-glow-green text-green-400' : 'text-glow-red text-red-400'}`}>
                  {prediction.predicted_direction}
                </h3>
                
                <div className="flex items-center gap-2 mt-2 bg-white/5 rounded-full px-4 py-1.5">
                  <TrendingUp size={16} className="text-blue-400" />
                  <span className="font-medium text-gray-200">Confidence: <span className="text-white font-bold">{prediction.confidence_score.toFixed(1)}%</span></span>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-muted-foreground">Waiting for next signal...</div>
            )}

            {prediction && (
              <div className="mt-6 pt-6 border-t border-white/10 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Entry Price</p>
                  <p className="text-xl font-mono text-gray-200">₹{prediction.entry_price.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Expected Close</p>
                  <p className="text-xl font-mono text-gray-200">₹{prediction.expected_close.toFixed(2)}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Chart */}
        <div className="lg:col-span-2">
          <div className="glass-panel p-6 rounded-2xl h-full min-h-[400px] flex flex-col">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold text-gray-300">NIFTY 50 Live Chart</h2>
              <div className="flex gap-2">
                <span className="px-3 py-1 text-xs font-medium bg-blue-500/20 text-blue-400 rounded-md border border-blue-500/20">5m Timeframe</span>
              </div>
            </div>
            
            <div className="flex-1 w-full h-full min-h-[300px]">
              {marketData.length > 0 ? (
                <Line data={chartData} options={chartOptions} />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                  Loading chart data...
                </div>
              )}
            </div>
          </div>
        </div>
        
      </div>
    </main>
  );
}
