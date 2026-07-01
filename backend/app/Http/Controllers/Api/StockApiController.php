<?php
namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\HistoricalStockData;
use App\Models\StockPrediction;
use App\Models\NewsSentiment;
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

        // Return combined JSON payload
        return response()->json([
            'symbol' => $symbol,
            'historical_data' => $historical,
            'prediction' => $prediction,
            'sentiment' => $sentiment,
        ], 200, [], JSON_PRETTY_PRINT);
    }

    public function syncStock($symbol)
    {
        // Use dynamic Python path and project directory
        $projectRoot = dirname(dirname(dirname(dirname(__DIR__))));
        $parentDir = dirname($projectRoot);
        $scriptPath = $parentDir . "\\run_pipeline.py";
        $pythonPath = "python"; // Use python from PATH
        
        // Execute the python pipeline and capture output
        $command = "cd " . escapeshellarg($parentDir) . " && " . escapeshellarg($pythonPath) . " " . escapeshellarg(basename($scriptPath)) . " " . escapeshellarg($symbol) . " 2>&1";
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
        $projectRoot = dirname(dirname(dirname(dirname(__DIR__))));
        $parentDir = dirname($projectRoot);
        $pythonPath = "python"; // Use python from PATH
        
        $command = "cd " . escapeshellarg($parentDir) . " && " . escapeshellarg($pythonPath) . " update_all_stocks.py 2>&1";
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

        $projectRoot = dirname(dirname(dirname(dirname(__DIR__))));
        $parentDir = dirname($projectRoot);
        $pythonPath = "python"; // Use python from PATH
        
        $symbolsString = implode(' ', $symbols);
        $command = "cd " . escapeshellarg($parentDir) . " && " . escapeshellarg($pythonPath) . " update_all_stocks.py " . escapeshellarg($symbolsString) . " 2>&1";
        $output = shell_exec($command);
        
        return response()->json([
            'message' => 'Selective sync execution finished',
            'output' => $output
        ]);
    }
}
