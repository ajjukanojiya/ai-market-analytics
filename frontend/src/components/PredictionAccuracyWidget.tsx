import React from 'react';
import { Target, CheckCircle2, AlertCircle } from 'lucide-react';

interface PredictionAccuracyWidgetProps {
  accuracy: number;
  totalPredictions: number;
  correctPredictions: number;
}

export function PredictionAccuracyWidget({ accuracy, totalPredictions, correctPredictions }: PredictionAccuracyWidgetProps) {
  // Determine color based on accuracy
  const colorClass = accuracy >= 70 ? 'text-green-500' : accuracy >= 50 ? 'text-yellow-500' : 'text-red-500';
  const bgClass = accuracy >= 70 ? 'bg-green-500' : accuracy >= 50 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div className="glass-panel p-6 rounded-2xl relative overflow-hidden group hover:border-white/10 transition-colors mt-6">
      <h2 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider flex items-center gap-2">
        <Target size={16} className="text-blue-400" />
        Model Performance
      </h2>
      
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <span className="text-4xl font-bold text-gray-200">
            {accuracy.toFixed(1)}<span className="text-2xl text-gray-400">%</span>
          </span>
          <span className="text-xs text-muted-foreground mt-1">Historical Accuracy</span>
        </div>

        {/* Circular Progress */}
        <div className="relative w-16 h-16 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
            <path
              className="text-gray-700"
              strokeWidth="3"
              stroke="currentColor"
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path
              className={colorClass}
              strokeDasharray={`${accuracy}, 100`}
              strokeWidth="3"
              strokeLinecap="round"
              stroke="currentColor"
              fill="none"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
          </svg>
        </div>
      </div>

      <div className="mt-5 pt-4 border-t border-white/10 flex justify-between text-sm">
        <div className="flex items-center gap-2 text-gray-300">
          <CheckCircle2 size={16} className="text-green-500" />
          <span>Correct: {correctPredictions}</span>
        </div>
        <div className="flex items-center gap-2 text-gray-300">
          <AlertCircle size={16} className="text-blue-500" />
          <span>Total: {totalPredictions}</span>
        </div>
      </div>
    </div>
  );
}
