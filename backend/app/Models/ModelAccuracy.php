<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ModelAccuracy extends Model
{
    use HasFactory;

    protected $table = 'model_accuracy';
    
    // Disable default timestamps if they aren't created_at and updated_at
    // We only have created_at in the python script.
    public $timestamps = false;

    protected $fillable = [
        'symbol',
        'evaluation_date',
        'mae',
        'accuracy_percentage',
        'days_evaluated',
    ];
}
