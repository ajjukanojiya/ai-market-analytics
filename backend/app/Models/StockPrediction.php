<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class StockPrediction extends Model
{
    protected $table = 'stock_predictions';
    // Only created_at exists in the python-generated table, no updated_at
    const UPDATED_AT = null;
    protected $guarded = [];
}
