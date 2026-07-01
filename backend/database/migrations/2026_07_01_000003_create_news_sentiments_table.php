<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('news_sentiments', function (Blueprint $table) {
            $table->id();
            $table->string('symbol', 50);
            $table->date('date');
            $table->decimal('sentiment_score', 5, 2);
            $table->string('verdict', 20);
            $table->text('summary');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('news_sentiments');
    }
};
