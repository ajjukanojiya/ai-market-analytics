import logging
import pandas as pd
from app.db.session import SessionLocal
from app.models.asset import Asset
from app.models.prediction import Prediction
from app.ai.preprocessing import fetch_data_from_db, add_technical_indicators, create_sequences
from app.ai.model import QuantModel

logger = logging.getLogger(__name__)

def generate_live_prediction(symbol="NIFTY 50"):
    """Generates a prediction for the next candle based on the latest data."""
    db = SessionLocal()
    try:
        asset = db.query(Asset).filter(Asset.symbol == symbol).first()
        if not asset:
            return None
            
        df = fetch_data_from_db(asset.id)
        if len(df) < 61:
            logger.warning("Not enough data to generate a prediction (need at least 61 candles).")
            return None
            
        # We need the most recent 60 candles to predict the next one
        # add_technical_indicators will process the whole df, but we only need the latest window
        df = add_technical_indicators(df)
        
        # Load Model
        model = QuantModel()
        model_prefix = "nifty50_5m" if "NIFTY" in symbol else "crudeoil_5m"
        
        # Get the latest 60 rows
        latest_window_df = df.tail(60)
        current_close = float(latest_window_df.iloc[-1]['close'])
        
        if "CRUDE" in symbol:
            current_close = current_close * 83.5
            
        if not model.load(prefix=model_prefix):
            logger.warning(f"No AI model for {symbol}. Using Technical Indicator Fallback.")
            # Fallback: Simple SMA Crossover
            sma10 = latest_window_df.iloc[-1]['SMA_10'] if 'SMA_10' in latest_window_df else latest_window_df.iloc[-1]['close']
            sma20 = latest_window_df.iloc[-1]['SMA_20'] if 'SMA_20' in latest_window_df else latest_window_df.iloc[-1]['close']
            direction = "BUY" if sma10 > sma20 else "SELL"
            confidence = 65.0
            margin_pts = 10 if "NIFTY" in symbol else 15
            expected_close = current_close + (margin_pts if direction == "BUY" else -margin_pts)
        else:
            # We need to scale the data using the SAME scaler that was used for training.
            _, _, _, scaler = create_sequences(df, lookback=60)
            
            features = ['open', 'high', 'low', 'close', 'volume', 'SMA_10', 'SMA_20', 'RSI_14', 'MACD', 'MACD_Signal', 'ROC_5', 'pcr_ratio', 'sentiment_score']
            
            # Check and fill missing features in latest window just in case
            for f in ['pcr_ratio', 'sentiment_score']:
                if f not in latest_window_df.columns:
                    latest_window_df[f] = 1.0 if f == 'pcr_ratio' else 0.0
                    
            data = latest_window_df[features].values
            scaled_data = scaler.transform(data)
            
            # Flatten for XGBoost
            X_live = scaled_data.flatten().reshape(1, -1)
            
            dir_pred, dir_prob, price_pred = model.predict(X_live)
            
            # Original classification confidence
            confidence = dir_prob[0][dir_pred[0]] * 100
            expected_close = float(price_pred[0])
            
            if "CRUDE" in symbol:
                expected_close = expected_close * 83.5
            
            # FIX LOGICAL CONTRADICTIONS:
            # Trust the price model over the trend model.
            if expected_close > current_close:
                direction = "BUY"
            else:
                direction = "SELL"
                
        logger.info(f"Prediction for {symbol}: {direction} with {confidence:.1f}% confidence. Expected Close: ₹{expected_close:.2f}")
        
        from datetime import datetime, timezone
        # Save prediction to DB
        pred = Prediction(
            asset_id=asset.id,
            prediction_timeframe="5m",
            timestamp=datetime.now(timezone.utc), # Ensure UTC timezone-aware
            predicted_trend=direction,
            expected_close=expected_close,
            confidence_score=confidence,
            entry_price=current_close
        )
        db.add(pred)
        db.commit()
        
        return {
            "direction": direction,
            "confidence": confidence,
            "expected_close": expected_close,
            "current_close": current_close
        }
        
    finally:
        db.close()

if __name__ == "__main__":
    generate_live_prediction("NIFTY 50")
    generate_live_prediction("CRUDE OIL (MCX)")
