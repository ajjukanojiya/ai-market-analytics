<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class NewsSentiment extends Model
{
    protected $table = 'news_sentiments';
    // Only created_at exists in the python-generated table, no updated_at
    const UPDATED_AT = null;
    protected $guarded = [];
}
