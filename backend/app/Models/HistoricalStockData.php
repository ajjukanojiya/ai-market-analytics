<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class HistoricalStockData extends Model
{
    protected $table = 'historical_stock_data';
    // No created_at or updated_at in this table
    public $timestamps = false;
    protected $guarded = [];
}
