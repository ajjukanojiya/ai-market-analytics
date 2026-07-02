<?php
namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\HistoricalStockData;
use App\Models\StockPrediction;
use App\Models\NewsSentiment;
use App\Models\ModelAccuracy;
use Illuminate\Http\Request;

class StockApiController extends Controller
{
    public function getStockData($symbol)
    {
        // 1. Fetch last 30 days of historical data
        $historical = HistoricalStockData::where('symbol', $symbol)
            ->orderBy('date', 'desc')
            ->limit(30)
            ->get();

        // 2. Fetch tomorrow's prediction (latest one)
        $prediction = StockPrediction::where('symbol', $symbol)
            ->orderBy('created_at', 'desc')
            ->first();

        // 3. Fetch today's sentiment (latest one)
        $sentiment = NewsSentiment::where('symbol', $symbol)
            ->orderBy('created_at', 'desc')
            ->first();

        // 4. Fetch the latest accuracy evaluation
        $accuracy = ModelAccuracy::where('symbol', $symbol)
            ->orderBy('created_at', 'desc')
            ->first();

        // Return combined JSON payload
        return response()->json([
            'symbol' => $symbol,
            'historical_data' => $historical,
            'prediction' => $prediction,
            'sentiment' => $sentiment,
            'accuracy' => $accuracy,
        ], 200, [], JSON_PRETTY_PRINT);
    }

    public function syncStock($symbol)
    {
        $pythonPath = "C:\\Users\\hp\\AppData\\Local\\Programs\\Python\\Python312\\python.exe";
        $scriptPath = "F:\\milstone\\run_pipeline.py";
        
        // Execute the python pipeline and capture output
        $command = escapeshellcmd("$pythonPath $scriptPath $symbol") . " 2>&1";
        $output = shell_exec($command);
        
        return response()->json([
            'symbol' => $symbol,
            'message' => 'Pipeline execution finished',
            'output' => $output
        ]);
    }

    public function syncAllStocks()
    {
        set_time_limit(0); // Prevent 30 second timeout for bulk updates
        $pythonPath = "C:\\Users\\hp\\AppData\\Local\\Programs\\Python\\Python312\\python.exe";
        $scriptPath = "F:\\milstone\\update_all_stocks.py";
        
        $command = escapeshellcmd("$pythonPath $scriptPath") . " 2>&1";
        $output = shell_exec($command);
        
        return response()->json([
            'message' => 'Bulk update execution finished',
            'output' => $output
        ]);
    }

    public function getAllSymbols()
    {
        $symbols = HistoricalStockData::select('symbol')->distinct()->pluck('symbol');
        return response()->json($symbols);
    }

    public function syncSelected(Request $request)
    {
        set_time_limit(0); // Prevent 30 second timeout for selective updates
        $symbols = $request->input('symbols', []);
        if (empty($symbols)) {
            return response()->json(['message' => 'No symbols provided'], 400);
        }

        $pythonPath = "C:\\Users\\hp\\AppData\\Local\\Programs\\Python\\Python312\\python.exe";
        $scriptPath = "F:\\milstone\\update_all_stocks.py";
        
        $symbolsString = implode(' ', $symbols);
        $command = escapeshellcmd("$pythonPath $scriptPath $symbolsString") . " 2>&1";
        $output = shell_exec($command);
        
        return response()->json([
            'message' => 'Selective sync execution finished',
            'output' => $output
        ]);
    }
}
