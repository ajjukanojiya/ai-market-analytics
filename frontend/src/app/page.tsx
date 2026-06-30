"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { TrendingUp, TrendingDown, Activity, BrainCircuit, Search, AlertCircle, RefreshCw, CheckSquare, X } from "lucide-react";

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

interface StockData {
  symbol: string;
  historical_data: any[];
  prediction: any;
  sentiment: any;
}

export default function Dashboard() {
  const [data, setData] = useState<StockData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isSyncingAll, setIsSyncingAll] = useState(false);
  const [syncMessage, setSyncMessage] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [currentSymbol, setCurrentSymbol] = useState("SBIN.NS");
  const [error, setError] = useState<string | null>(null);

  // Selective Sync State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [availableSymbols, setAvailableSymbols] = useState<string[]>([]);
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([]);
  const [isLoadingSymbols, setIsLoadingSymbols] = useState(false);

  const fetchData = async (symbolToFetch: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `http://localhost:8000/api/stocks/${symbolToFetch}`
      );
      
      if (!response.data || !response.data.historical_data || response.data.historical_data.length === 0) {
          setError(`No database records found for ${symbolToFetch}.`);
          setData(null);
      } else {
          setData(response.data);
      }
    } catch (err) {
      console.error("Error fetching data:", err);
      setError("Error connecting to the backend API. Ensure Laravel is running.");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(currentSymbol);
  }, [currentSymbol]);

  const handleSearch = (e: React.FormEvent) => {
      e.preventDefault();
      if(searchQuery.trim() !== "") {
          setCurrentSymbol(searchQuery.toUpperCase());
      }
  }

  const handleSync = async () => {
    setIsSyncing(true);
    try {
        await axios.post(`http://localhost:8000/api/stocks/sync/${currentSymbol}`);
        await fetchData(currentSymbol);
    } catch (err) {
        console.error("Sync error:", err);
        alert("Error running the AI Pipeline.");
    } finally {
        setIsSyncing(false);
    }
  }

  const handleSyncAll = async () => {
    setSyncMessage("Bulk Update in Progress (All Stocks)...");
    setIsSyncingAll(true);
    try {
        await axios.post(`http://localhost:8000/api/stocks/sync-all`);
        await fetchData(currentSymbol); // Refresh current view
        alert("🎉 All stocks have been successfully updated!");
    } catch (err) {
        console.error("Sync All error:", err);
        alert("Error running the Bulk Update.");
    } finally {
        setIsSyncingAll(false);
    }
  }

  const openSelectiveSyncModal = async () => {
      setIsModalOpen(true);
      setIsLoadingSymbols(true);
      try {
          const response = await axios.get(`http://localhost:8000/api/stocks/symbols`);
          setAvailableSymbols(response.data);
          setSelectedSymbols(response.data); // select all by default
      } catch (error) {
          console.error("Failed to fetch symbols", error);
      } finally {
          setIsLoadingSymbols(false);
      }
  }

  const toggleSymbolSelection = (symbol: string) => {
      if (selectedSymbols.includes(symbol)) {
          setSelectedSymbols(selectedSymbols.filter(s => s !== symbol));
      } else {
          setSelectedSymbols([...selectedSymbols, symbol]);
      }
  }

  const handleSyncSelected = async () => {
      if (selectedSymbols.length === 0) {
          alert("Please select at least one stock to sync.");
          return;
      }
      
      setIsModalOpen(false);
      setSyncMessage(`Selective Sync in Progress (${selectedSymbols.length} stocks)...`);
      setIsSyncingAll(true);
      try {
          await axios.post(`http://localhost:8000/api/stocks/sync-selected`, {
              symbols: selectedSymbols
          });
          await fetchData(currentSymbol); 
          alert("🎉 Selected stocks have been successfully updated!");
      } catch (err) {
          console.error("Sync Selected error:", err);
          alert("Error running the Selective Update.");
      } finally {
          setIsSyncingAll(false);
      }
  }

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 p-6 md:p-12 font-sans selection:bg-indigo-500/30">
      
      {/* Selective Sync Modal */}
      {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
              <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-md shadow-2xl relative">
                  <button onClick={() => setIsModalOpen(false)} className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors">
                      <X size={24} />
                  </button>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-2">
                      <CheckSquare className="text-indigo-400" /> Selective Sync
                  </h2>
                  <p className="text-slate-400 text-sm mb-6">Choose which stocks you want to update with the latest market data and AI predictions.</p>
                  
                  {isLoadingSymbols ? (
                      <div className="flex justify-center py-8">
                          <RefreshCw className="animate-spin text-indigo-500" />
                      </div>
                  ) : (
                      <div className="flex flex-col gap-3 max-h-[300px] overflow-y-auto mb-6 pr-2 custom-scrollbar">
                          {availableSymbols.map(symbol => (
                              <label key={symbol} className="flex items-center gap-3 p-3 bg-slate-800 rounded-xl cursor-pointer hover:bg-slate-700 transition-colors border border-transparent hover:border-slate-600">
                                  <input 
                                      type="checkbox" 
                                      checked={selectedSymbols.includes(symbol)}
                                      onChange={() => toggleSymbolSelection(symbol)}
                                      className="w-5 h-5 rounded border-slate-600 text-indigo-500 focus:ring-indigo-500 focus:ring-offset-slate-800 bg-slate-900"
                                  />
                                  <span className="font-bold text-white">{symbol}</span>
                              </label>
                          ))}
                          {availableSymbols.length === 0 && (
                              <p className="text-slate-500 text-center py-4">No stocks found in database.</p>
                          )}
                      </div>
                  )}

                  <div className="flex gap-3">
                      <button 
                          onClick={() => setIsModalOpen(false)}
                          className="flex-1 bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 px-4 rounded-xl transition-colors"
                      >
                          Cancel
                      </button>
                      <button 
                          onClick={handleSyncSelected}
                          disabled={selectedSymbols.length === 0 || isLoadingSymbols}
                          className="flex-[2] bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold py-3 px-4 rounded-xl transition-colors shadow-lg shadow-indigo-500/20"
                      >
                          Update {selectedSymbols.length} Stocks
                      </button>
                  </div>
              </div>
          </div>
      )}

      {/* Header & Search Bar */}
      <div className="flex flex-col xl:flex-row justify-between items-start xl:items-center mb-10 border-b border-slate-800 pb-6 gap-6">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <div className="p-2 bg-indigo-500/20 rounded-xl">
              <BrainCircuit className="text-indigo-400" size={32} />
            </div>
            AI Market Analytics
          </h1>
          <p className="text-slate-400 mt-2 text-sm uppercase tracking-widest font-semibold ml-1 flex items-center gap-2">
            Real-time predictive insights
            <span className="bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded text-xs font-bold">MULTIVARIATE LSTM</span>
          </p>
        </div>
        
        <div className="flex flex-col md:flex-row w-full xl:w-auto gap-4">
            {/* Sync Selected Button */}
            <button 
                onClick={openSelectiveSyncModal}
                disabled={isSyncingAll || isSyncing}
                className="bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-white px-4 py-3 rounded-xl transition-colors flex items-center justify-center border border-slate-700 hover:border-slate-600 gap-2 font-semibold whitespace-nowrap"
            >
                <CheckSquare size={18} className="text-indigo-400" />
                Sync Selected
            </button>

            {/* Sync All Button */}
            <button 
                onClick={handleSyncAll}
                disabled={isSyncingAll || isSyncing}
                className="bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-white px-4 py-3 rounded-xl transition-colors flex items-center justify-center border border-slate-700 hover:border-slate-600 gap-2 font-semibold whitespace-nowrap"
            >
                <RefreshCw size={18} className={isSyncingAll ? "animate-spin text-indigo-400" : "text-indigo-400"} />
                {isSyncingAll ? "Updating..." : "Sync All"}
            </button>

            {/* Dynamic Search Box */}
            <form onSubmit={handleSearch} className="relative w-full md:w-80 flex">
                <input 
                    type="text" 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search Stock (e.g. TCS.NS)"
                    className="w-full bg-slate-900 border border-slate-700 text-white px-4 py-3 rounded-l-xl focus:outline-none focus:border-indigo-500 transition-colors"
                />
                <button type="submit" className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-3 rounded-r-xl transition-colors flex items-center justify-center border border-indigo-600 hover:border-indigo-500">
                    <Search size={20} />
                </button>
            </form>
        </div>
      </div>

      {isSyncingAll && (
        <div className="mb-8 p-4 bg-indigo-500/10 border border-indigo-500/30 rounded-xl flex items-center gap-4 animate-pulse">
            <RefreshCw className="animate-spin text-indigo-400" />
            <div>
                <h3 className="font-bold text-white">{syncMessage}</h3>
                <p className="text-sm text-slate-400">Fetching new data and training High-Accuracy Multivariate LSTMs for your stocks. This may take a few minutes depending on how many stocks you track.</p>
            </div>
        </div>
      )}

      {loading && !isSyncing && (
        <div className="flex h-[60vh] items-center justify-center bg-[#0f172a] text-white">
          <div className="flex flex-col items-center gap-4">
              <BrainCircuit className="text-indigo-500 animate-pulse" size={48} />
              <div className="text-xl font-bold text-slate-300 tracking-wider">Loading AI Market Data...</div>
          </div>
        </div>
      )}

      {isSyncing && (
        <div className="flex flex-col h-[60vh] items-center justify-center bg-[#0f172a] text-white text-center">
            <div className="relative w-24 h-24 mb-6">
                <div className="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                <BrainCircuit className="absolute inset-0 m-auto text-indigo-400" size={32} />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2 animate-pulse">Running High-Accuracy AI Pipeline...</h2>
            <p className="text-slate-400">Calculating RSI, training Multivariate LSTM model, and reading Gemini news for {currentSymbol}.</p>
            <p className="text-sm text-indigo-400 mt-4">This usually takes 15-20 seconds. Please wait.</p>
        </div>
      )}

      {!loading && !isSyncing && error && (
        <div className="flex flex-col h-[60vh] items-center justify-center bg-[#0f172a] text-white text-center">
            <AlertCircle className="text-rose-500 mb-4" size={64} />
            <h2 className="text-2xl font-bold text-white mb-2">Data Unavailable</h2>
            <p className="text-lg text-slate-400 max-w-lg mb-8">{error}</p>
            <button 
                onClick={handleSync}
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 px-8 rounded-full shadow-lg shadow-indigo-500/30 transition-all flex items-center gap-2"
            >
                🚀 Initialize AI Analysis for {currentSymbol}
            </button>
        </div>
      )}

      {!loading && !isSyncing && !error && data && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <DashboardContent data={data} />
        </div>
      )}
    </div>
  );
}

function DashboardContent({ data }: { data: StockData }) {
    // Prepare Chart Data
    const sortedHistory = [...data.historical_data].reverse();
    const labels = sortedHistory.map((item) => item.date);
    const prices = sortedHistory.map((item) => parseFloat(item.close));

    const chartData = {
        labels,
        datasets: [
        {
            label: `${data.symbol} Close Price (₹)`,
            data: prices,
            borderColor: "rgba(99, 102, 241, 1)", 
            backgroundColor: "rgba(99, 102, 241, 0.1)",
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 6,
            fill: true,
            tension: 0.4,
        },
        ],
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
        y: {
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            ticks: { color: "#9ca3af" }, 
        },
        x: {
            grid: { display: false },
            ticks: { color: "#9ca3af", maxTicksLimit: 10 },
        },
        },
        plugins: {
        legend: { display: false },
        tooltip: { mode: "index", intersect: false },
        },
    };

    const lastActualPrice = prices[prices.length - 1];
    const predictedPrice = parseFloat(data.prediction?.predicted_price || "0");
    const isUp = predictedPrice > lastActualPrice;
    const sentimentVerdict = data.sentiment?.verdict || "NEUTRAL";
    const sentimentScore = parseFloat(data.sentiment?.sentiment_score || "0");

    let recommendation = "HOLD";
    let recColor = "text-yellow-500";
    let recBg = "bg-yellow-500/10";
    let recBorder = "border-yellow-500/30";

    if (isUp && sentimentVerdict === "POSITIVE") {
        recommendation = "STRONG BUY";
        recColor = "text-emerald-400";
        recBg = "bg-emerald-400/10";
        recBorder = "border-emerald-500/30";
    } else if (!isUp && sentimentVerdict === "NEGATIVE") {
        recommendation = "STRONG SELL";
        recColor = "text-rose-500";
        recBg = "bg-rose-500/10";
        recBorder = "border-rose-500/30";
    } else if (isUp) {
        recommendation = "BUY";
        recColor = "text-green-400";
        recBg = "bg-green-400/10";
        recBorder = "border-green-500/30";
    } else if (!isUp) {
        recommendation = "SELL";
        recColor = "text-red-400";
        recBg = "bg-red-400/10";
        recBorder = "border-red-500/30";
    }

    return (
        <>
            <div className="lg:col-span-2 bg-slate-900/60 rounded-3xl border border-slate-800 p-6 md:p-8 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl"></div>
                
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 relative z-10">
                <h2 className="text-xl font-bold text-white flex items-center gap-3">
                    <Activity className="text-indigo-400" size={24} />
                    30-Day Historical Trend
                </h2>
                <div className="mt-4 sm:mt-0 px-4 py-2 bg-slate-800 rounded-lg text-sm text-slate-400 border border-slate-700">
                    Last Close: <span className="text-white font-mono font-bold ml-1">₹{lastActualPrice.toFixed(2)}</span>
                </div>
                </div>
                
                <div className="h-[450px] w-full relative z-10">
                {/* @ts-ignore */}
                <Line data={chartData} options={chartOptions as any} />
                </div>
            </div>

            <div className="flex flex-col gap-6">
                
                <div className="bg-slate-900/60 rounded-3xl border border-slate-800 p-8 shadow-2xl relative overflow-hidden group hover:border-indigo-500/50 transition-colors duration-500">
                <div className="absolute -top-10 -right-10 w-40 h-40 bg-indigo-500/10 rounded-full blur-3xl group-hover:bg-indigo-500/20 transition-all duration-700"></div>
                
                <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-1">Tomorrow's Prediction</h2>
                <div className="text-xs text-slate-500 font-mono mb-6">{data.prediction?.prediction_for_date}</div>
                
                <div className="flex items-end gap-3">
                    <div className="text-5xl font-black text-white tracking-tighter">
                    ₹{predictedPrice.toFixed(2)}
                    </div>
                    <div className={`flex items-center gap-1 font-bold mb-1 ${isUp ? 'text-emerald-400' : 'text-rose-500'}`}>
                    {isUp ? <TrendingUp size={28} strokeWidth={3} /> : <TrendingDown size={28} strokeWidth={3} />}
                    </div>
                </div>
                
                <div className="mt-4 pt-4 border-t border-slate-800 flex justify-between text-xs font-medium">
                    <span className="text-slate-500">LSTM Confidence</span>
                    <span className="text-emerald-400 font-bold">Ultra High (Multivariate)</span>
                </div>
                </div>

                <div className="bg-slate-900/60 rounded-3xl border border-slate-800 p-8 shadow-2xl">
                <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-6">Gemini Sentiment</h2>
                
                <div className="flex items-center justify-between mb-3">
                    <span className="text-3xl font-black text-white">{sentimentScore}</span>
                    <span className={`px-4 py-1.5 rounded-lg text-xs font-bold tracking-wider ${sentimentVerdict === 'POSITIVE' ? 'bg-emerald-500/20 text-emerald-400' : sentimentVerdict === 'NEGATIVE' ? 'bg-rose-500/20 text-rose-400' : 'bg-slate-700/50 text-slate-300'}`}>
                    {sentimentVerdict}
                    </span>
                </div>
                
                <div className="w-full bg-slate-800 rounded-full h-1.5 mb-6 overflow-hidden">
                    <div 
                    className={`h-1.5 rounded-full ${sentimentVerdict === 'POSITIVE' ? 'bg-emerald-500' : sentimentVerdict === 'NEGATIVE' ? 'bg-rose-500' : 'bg-slate-500'}`} 
                    style={{ width: `${Math.max(10, Math.abs(sentimentScore * 100))}%` }}
                    ></div>
                </div>
                
                <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
                    <p className="text-sm text-slate-300 leading-relaxed">"{data.sentiment?.summary || "No recent news found."}"</p>
                </div>
                </div>

                <div className={`rounded-3xl border ${recBorder} p-8 shadow-2xl flex flex-col items-center justify-center text-center ${recBg} backdrop-blur-md`}>
                    <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Final AI Signal</h2>
                    <div className={`text-4xl font-black tracking-tight ${recColor}`}>
                    {recommendation}
                    </div>
                    <p className="text-xs text-slate-400/80 mt-4 max-w-[200px]">Combined Multivariate LSTM price prediction and NLP sentiment analysis.</p>
                </div>
            </div>
        </>
    )
}
