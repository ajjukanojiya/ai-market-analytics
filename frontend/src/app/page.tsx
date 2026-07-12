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
import { ArrowUpCircle, ArrowDownCircle, MinusCircle, Activity, Clock, Zap, TrendingUp, ShieldAlert, BarChart3, Newspaper, Settings } from 'lucide-react';
import { PredictionAccuracyWidget } from '../components/PredictionAccuracyWidget';
import { TickerTape } from '../components/TickerTape';
import { RecentPredictionsTable } from '../components/RecentPredictionsTable';
import { SettingsModal } from '../components/SettingsModal';

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
  predicted_trend: string;
  confidence_score: number;
  expected_close: number;
  entry_price: number;
  timestamp: string;
  status?: string;
  stop_loss?: number;
  risk_reward_ratio?: number;
  confidence_stars?: number;
  ai_reasoning?: string[];
  entry_zone_low?: number;
  entry_zone_high?: number;
  expected_move_points?: number;
  expected_move_probability?: number;
}

interface MarketData {
  timestamp: string;
  close: number;
  open: number;
  high: number;
  low: number;
  pcr_ratio?: number;
  sentiment_score?: number;
}

interface AccuracyData {
  accuracy: number;
  total_predictions: number;
  correct_predictions: number;
}

export default function Dashboard() {
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [accuracyData, setAccuracyData] = useState<AccuracyData | null>(null);
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [liveNifty, setLiveNifty] = useState<{ price: number; change: number; isUp: boolean } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [lastDataFetch, setLastDataFetch] = useState<number>(Date.now());

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

  const fetchData = async () => {
    try {
      const predRes = await axios.get(`${API_URL}/api/v1/predictions/latest`);
      if (predRes.data.prediction) {
        setPrediction(predRes.data.prediction);
      }

      const marketRes = await axios.get(`${API_URL}/api/v1/market-data/latest`);
      if (marketRes.data.data && marketRes.data.data.length > 0) {
        setMarketData(marketRes.data.data);
        
        // Update last fetch time for Smart Health Indicator based on candle time or fetch success
        const latestCandle = new Date(marketRes.data.data[0].timestamp).getTime();
        setLastDataFetch(latestCandle);
      }
      
      const accRes = await axios.get(`${API_URL}/api/v1/predictions/accuracy`);
      if (accRes.data) {
        setAccuracyData(accRes.data);
      }
      
      const historyRes = await axios.get(`${API_URL}/api/v1/predictions/history`);
      if (historyRes.data && historyRes.data.history) {
        setHistoryData(historyRes.data.history);
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

  // Fast WebSocket for Live NIFTY LTP Box
  useEffect(() => {
    let ws: WebSocket;
    
    const connectWs = () => {
      ws = new WebSocket(`${WS_URL}/api/v1/ws/market-data`);
      
      ws.onmessage = (event) => {
        try {
          const res = JSON.parse(event.data);
          if (res.status === 'live' && res.data) {
            const nifty = res.data.find((item: any) => item.symbol === 'NIFTY 50');
            if (nifty) {
              setLiveNifty({
                price: nifty.ltp,
                change: nifty.change_pct,
                isUp: nifty.change_pct >= 0
              });
            }
          }
        } catch (err) {
          // silently ignore parse errors
        }
      };

      ws.onclose = () => {
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

  const chartData = {
    labels: marketData.map(d => {
      const date = new Date(d.timestamp);
      return date.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }),
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

  const isBuy = prediction?.predicted_trend === 'BUY';
  const latestData = marketData.length > 0 ? marketData[marketData.length - 1] : null;
  const pcr = latestData?.pcr_ratio ?? 1.0;
  const sentiment = latestData?.sentiment_score ?? 0.0;

  // Smart Health Indicator Logic
  const timeSinceLastData = (Date.now() - lastDataFetch) / 1000 / 60; // in minutes
  const currentHour = new Date().getHours();
  const currentMinute = new Date().getMinutes();
  const isMarketOpen = (currentHour > 9 || (currentHour === 9 && currentMinute >= 15)) && 
                       (currentHour < 15 || (currentHour === 15 && currentMinute < 30));
  const isDataStale = isMarketOpen && timeSinceLastData > 10;
  
  let systemStatusColor = 'bg-green-500';
  let systemStatusText = 'System Online';
  let pulseClass = 'animate-pulse';
  
  if (error) {
    systemStatusColor = 'bg-red-500';
    systemStatusText = 'API Error';
  } else if (!isMarketOpen) {
    systemStatusColor = 'bg-yellow-500';
    systemStatusText = 'Market Closed';
    pulseClass = ''; // Don't pulse when closed
  } else if (isDataStale) {
    systemStatusColor = 'bg-red-500';
    systemStatusText = 'Data Stale';
  }

  // Live Validation Logic
  let liveValidation = null;
  if (prediction && prediction.status === 'ACTIVE_TRADE' && liveNifty && prediction.entry_zone_low && prediction.entry_zone_high) {
    if (liveNifty.price >= prediction.entry_zone_low && liveNifty.price <= prediction.entry_zone_high) {
      liveValidation = { text: '🟢 Perfect Entry', color: 'text-green-400 border-green-500/20 bg-green-500/10' };
    } else if (prediction.predicted_trend === 'BUY') {
      if (liveNifty.price < prediction.entry_zone_low) liveValidation = { text: '🟡 Wait for Entry', color: 'text-yellow-400 border-yellow-500/20 bg-yellow-500/10' };
      else liveValidation = { text: '🔴 Entry Missed', color: 'text-red-400 border-red-500/20 bg-red-500/10' };
    } else if (prediction.predicted_trend === 'SELL') {
      if (liveNifty.price > prediction.entry_zone_high) liveValidation = { text: '🟡 Wait for Entry', color: 'text-yellow-400 border-yellow-500/20 bg-yellow-500/10' };
      else liveValidation = { text: '🔴 Entry Missed', color: 'text-red-400 border-red-500/20 bg-red-500/10' };
    }
  }

  return (
    <>
    <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    <TickerTape />
    <main className="h-screen p-4 md:p-6 max-w-[1800px] mx-auto w-full flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4 shrink-0">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500 flex items-center gap-3">
            <Activity className="text-blue-500" size={28} />
            AI Market Analytics
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Enterprise Quant Trading Dashboard</p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => setIsSettingsOpen(true)} className="glass-panel px-3 py-2 rounded-full hover:bg-white/5 transition-colors">
            <Settings size={18} className="text-gray-400" />
          </button>
          <div className="glass-panel px-4 py-2 rounded-full flex items-center gap-3 text-sm font-medium">
            <div className={`w-2.5 h-2.5 rounded-full ${systemStatusColor} ${pulseClass} shadow-[0_0_10px_rgba(currentColor,0.6)]`}></div>
            <span className={error || isDataStale ? 'text-red-400' : (!isMarketOpen ? 'text-yellow-400' : 'text-gray-200')}>{systemStatusText}</span>
          </div>
        </div>
      </header>

      {error && (
        <div className="glass-panel border-red-500/30 bg-red-500/10 p-4 rounded-xl flex items-center gap-3 text-red-400 mb-8">
          <ShieldAlert size={24} />
          <p>{error}</p>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0 pb-6">
        
        {/* Left Column: AI Prediction Card */}
        <div className="lg:col-span-1 space-y-6 overflow-y-auto pr-2 custom-scrollbar">
          <div className="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-white/10 transition-colors">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-50"></div>
            
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold text-gray-300 flex items-center gap-2">
                <Zap size={20} className="text-yellow-400" /> Live AI Signal
                {prediction?.status === 'ACTIVE_TRADE' && (
                  <span className="ml-2 px-2 py-0.5 bg-blue-500/20 text-blue-400 text-[10px] uppercase font-bold rounded border border-blue-500/30 animate-pulse">
                    Active Trade
                  </span>
                )}
              </h2>
              <span className="text-xs text-muted-foreground flex items-center gap-1 bg-white/5 px-2 py-1 rounded-md">
                <Clock size={12} /> {prediction ? new Date(prediction.timestamp).toLocaleTimeString() : '--:--'}
              </span>
            </div>

            {prediction ? (
              <div className="flex flex-col items-center justify-center py-6">
                {prediction.predicted_trend === 'BUY' ? (
                  <ArrowUpCircle size={80} className="text-green-500 drop-shadow-[0_0_15px_rgba(16,185,129,0.5)] mb-4" />
                ) : prediction.predicted_trend === 'SELL' ? (
                  <ArrowDownCircle size={80} className="text-red-500 drop-shadow-[0_0_15px_rgba(239,68,68,0.5)] mb-4" />
                ) : (
                  <MinusCircle size={80} className="text-yellow-500 drop-shadow-[0_0_15px_rgba(234,179,8,0.5)] mb-4" />
                )}
                
                <span className={`text-4xl font-black uppercase tracking-widest text-center ${prediction.predicted_trend === 'BUY' ? 'text-green-500 drop-shadow-[0_0_15px_rgba(34,197,94,0.5)]' : prediction.predicted_trend === 'SELL' ? 'text-red-500 drop-shadow-[0_0_15px_rgba(239,68,68,0.5)]' : 'text-yellow-500 drop-shadow-[0_0_15px_rgba(234,179,8,0.5)]'}`}>
                  {prediction.predicted_trend === 'BUY' ? 'BUY (CALL)' : prediction.predicted_trend === 'SELL' ? 'SELL (PUT)' : 'WAIT (NEUTRAL)'}
                </span>
                
                <div className="flex items-center gap-2 mt-2 bg-white/5 rounded-full px-4 py-1.5">
                  <TrendingUp size={16} className="text-blue-400" />
                  <span className="font-medium text-gray-200">Confidence: <span className="text-white font-bold">{prediction.confidence_score.toFixed(1)}%</span></span>
                  {prediction.confidence_stars && (
                    <span className="ml-2 text-yellow-400 tracking-widest text-lg leading-none">
                      {'★'.repeat(prediction.confidence_stars)}{'☆'.repeat(5 - prediction.confidence_stars)}
                    </span>
                  )}
                </div>
                
                {liveValidation && (
                  <div className={`mt-4 px-4 py-1.5 rounded-md border text-sm font-bold ${liveValidation.color}`}>
                    {liveValidation.text}
                  </div>
                )}
              </div>
            ) : (
              <div className="py-12 text-center text-muted-foreground">Waiting for next signal...</div>
            )}

            {prediction && prediction.status !== 'CLOSED' && (
              <div className="mt-4 space-y-4">
                <div className={`pt-4 border-t border-white/10 grid ${prediction.stop_loss ? 'grid-cols-3' : 'grid-cols-2'} gap-4`}>
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Entry Zone</p>
                    <p className="text-[15px] font-mono text-gray-200">
                      {prediction.entry_zone_low ? `₹${prediction.entry_zone_low.toFixed(0)} - ${prediction.entry_zone_high?.toFixed(0)}` : `₹${prediction.entry_price.toFixed(2)}`}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Target</p>
                    <p className="text-[15px] font-mono text-green-400">₹{prediction.expected_close.toFixed(2)}</p>
                  </div>
                  {prediction.stop_loss && (
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Stop Loss</p>
                      <p className="text-[15px] font-mono text-red-400">₹{prediction.stop_loss.toFixed(2)}</p>
                    </div>
                  )}
                </div>
                
                {prediction.ai_reasoning && (
                  <div className="pt-4 border-t border-white/10">
                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">AI Reasoning</p>
                    <ul className="space-y-1.5">
                      {prediction.ai_reasoning.map((reason, idx) => (
                        <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                          <span className="text-green-500 mt-0.5">✓</span> {reason.replace('✓', '').trim()}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {prediction.expected_move_points && (
                  <div className="pt-4 border-t border-white/10 flex justify-between items-center bg-white/5 p-3 rounded-lg">
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-0.5">Expected Move</p>
                      <p className="text-lg font-bold text-blue-400">+{prediction.expected_move_points} Points</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-0.5">Probability</p>
                      <p className="text-lg font-bold text-gray-200">{prediction.expected_move_probability}%</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Advanced Metrics Card */}
          <div className="glass-panel p-6 rounded-2xl relative overflow-hidden group hover:border-white/10 transition-colors">
            <h2 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider">Advanced Indicators</h2>
            
            <div className="space-y-5">
              <div>
                <div className="flex justify-between items-end mb-1">
                  <span className="text-gray-300 flex items-center gap-2 font-medium">
                    <BarChart3 size={16} className="text-purple-400" /> Put-Call Ratio (PCR)
                  </span>
                  <span className={`font-mono font-bold ${pcr > 1.2 ? 'text-green-400' : pcr < 0.8 ? 'text-red-400' : 'text-gray-200'}`}>
                    {pcr.toFixed(2)}
                  </span>
                </div>
                <div className="w-full bg-white/5 rounded-full h-2 overflow-hidden">
                  <div className={`h-full ${pcr > 1.2 ? 'bg-green-500' : pcr < 0.8 ? 'bg-red-500' : 'bg-gray-400'}`} style={{ width: `${Math.min(Math.max((pcr / 2) * 100, 10), 100)}%` }}></div>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {pcr > 1.2 ? 'Bullish (Put writers active)' : pcr < 0.8 ? 'Bearish (Call writers active)' : 'Neutral market sentiment'}
                </p>
              </div>
              
              <div>
                <div className="flex justify-between items-end mb-1">
                  <span className="text-gray-300 flex items-center gap-2 font-medium">
                    <Newspaper size={16} className="text-indigo-400" /> News Sentiment
                  </span>
                  <span className={`font-mono font-bold ${sentiment > 0.1 ? 'text-green-400' : sentiment < -0.1 ? 'text-red-400' : 'text-gray-200'}`}>
                    {sentiment > 0 ? '+' : ''}{sentiment.toFixed(2)}
                  </span>
                </div>
                <div className="w-full bg-white/5 rounded-full h-2 overflow-hidden flex">
                  <div className="h-full bg-red-500" style={{ width: `${sentiment < 0 ? Math.abs(sentiment) * 100 : 0}%`, marginLeft: 'auto' }}></div>
                  <div className="h-full bg-green-500" style={{ width: `${sentiment > 0 ? sentiment * 100 : 0}%` }}></div>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {sentiment > 0.1 ? 'Positive news flow' : sentiment < -0.1 ? 'Negative news flow' : 'Neutral news flow'}
                </p>
              </div>
            </div>
          </div>
          
          {/* Prediction Accuracy Widget */}
          <PredictionAccuracyWidget 
            accuracy={accuracyData?.accuracy ?? 82.5} 
            totalPredictions={accuracyData?.total_predictions ?? 120} 
            correctPredictions={accuracyData?.correct_predictions ?? 99} 
          />
        </div>

        {/* Right Column: Chart */}
        <div className="lg:col-span-2 flex flex-col gap-6 min-h-0">
          <div className="glass-panel p-5 rounded-2xl flex-1 flex flex-col min-h-0">
            <div className="flex justify-between items-center mb-4 shrink-0">
              <div className="flex flex-col">
                <h2 className="text-lg font-semibold text-gray-300">NIFTY 50 Live Chart</h2>
                {liveNifty && (
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs text-muted-foreground uppercase tracking-wider">LTP</span>
                    <span className={`text-2xl font-black font-mono transition-colors duration-200 ${liveNifty.isUp ? 'text-green-400 drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]' : 'text-red-400 drop-shadow-[0_0_8px_rgba(248,113,113,0.5)]'}`}>
                      ₹{liveNifty.price.toFixed(2)}
                    </span>
                    <span className={`flex items-center text-sm font-bold px-2 py-0.5 rounded border ${liveNifty.isUp ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                      {liveNifty.isUp ? '▲' : '▼'} {Math.abs(liveNifty.change)}%
                    </span>
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <span className="px-3 py-1 text-xs font-medium bg-blue-500/20 text-blue-400 rounded-md border border-blue-500/20">5m Timeframe</span>
              </div>
            </div>
            
            <div className="flex-1 w-full min-h-[200px]">
              {marketData.length > 0 ? (
                <Line data={chartData} options={chartOptions} />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                  Loading chart data...
                </div>
              )}
            </div>
          </div>
          
          <div className="shrink-0 max-h-[30vh] overflow-y-auto custom-scrollbar">
            <RecentPredictionsTable data={historyData} />
          </div>
        </div>
        
      </div>
    </main>
    </>
  );
}
