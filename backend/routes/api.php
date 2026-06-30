<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\StockApiController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

// Our custom API endpoint for the Dashboard
Route::get('/stocks/symbols', [StockApiController::class, 'getAllSymbols']);
Route::get('/stocks/{symbol}', [StockApiController::class, 'getStockData']);
Route::post('/stocks/sync/{symbol}', [StockApiController::class, 'syncStock']);
Route::post('/stocks/sync-all', [StockApiController::class, 'syncAllStocks']);
Route::post('/stocks/sync-selected', [StockApiController::class, 'syncSelected']);
