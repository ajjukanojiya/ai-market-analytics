import logging
import pandas as pd
from app.db.session import SessionLocal
from app.models.asset import Asset
from app.models.prediction import Prediction
from app.ai.preprocessing import fetch_data_from_db, add_technical_indicators, create_sequences
from app.ai.model import QuantModel

logger = logging.getLogger(__name__)

def generate_live_prediction():
    """Generates a prediction for the next candle based on the latest data."""
    db = SessionLocal()
    try:
        nifty = db.query(Asset).filter(Asset.symbol == "NIFTY 50").first()
        if not nifty:
            return None
            
        df = fetch_data_from_db(nifty.id)
        if len(df) < 61:
            logger.warning("Not enough data to generate a prediction (need at least 61 candles).")
            return None
            
        # We need the most recent 60 candles to predict the next one
        # add_technical_indicators will process the whole df, but we only need the latest window
        df = add_technical_indicators(df)
        
        # Load Model
        model = QuantModel()
        if not model.load(prefix="nifty50_5m"):
            logger.error("Could not load AI model. Has it been trained?")
            return None
            
        # Get the latest 60 rows
        latest_window_df = df.tail(60)
        
        # We need to scale the data using the SAME scaler that was used for training.
        # For a production system, you'd save the scaler using joblib (like the model) and load it here.
        # For now, since we re-fetch data, we can re-fit on the whole df (not perfect, but works for PoC).
        _, _, _, scaler = create_sequences(df, lookback=60)
        
        features = ['open', 'high', 'low', 'close', 'volume', 'SMA_10', 'SMA_20', 'RSI_14', 'MACD', 'MACD_Signal', 'ROC_5']
        data = latest_window_df[features].values
        scaled_data = scaler.transform(data)
        
        # Flatten for XGBoost
        X_live = scaled_data.flatten().reshape(1, -1)
        
        dir_pred, dir_prob, price_pred = model.predict(X_live)
        
        direction = "BUY" if dir_pred[0] == 1 else "SELL"
        confidence = dir_prob[0][dir_pred[0]] * 100
        expected_close = float(price_pred[0])
        
        # Get the current close to compare
        current_close = float(latest_window_df.iloc[-1]['close'])
        
        logger.info(f"AI Prediction for next candle: {direction} with {confidence:.1f}% confidence. Expected Close: ₹{expected_close:.2f}")
        
        # Save prediction to DB
        pred = Prediction(
            asset_id=nifty.id,
            prediction_timeframe="5m",
            timestamp=pd.Timestamp.now(), # Approximate time of prediction
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
    generate_live_prediction()
