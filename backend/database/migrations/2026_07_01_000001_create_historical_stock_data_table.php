<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('historical_stock_data', function (Blueprint $table) {
            $table->id();
            $table->string('symbol', 50);
            $table->date('date');
            $table->decimal('open', 15, 4);
            $table->decimal('high', 15, 4);
            $table->decimal('low', 15, 4);
            $table->decimal('close', 15, 4);
            $table->bigInteger('volume');
            $table->timestamps();
            $table->unique(['symbol', 'date']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('historical_stock_data');
    }
};
