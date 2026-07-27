import sys
import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import logging

# Add parent directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.asset import Asset
from app.models.market_data import MarketData
from app.ai.predictor import generate_live_prediction

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

def fetch_asset(db, symbol_db, symbol_yf):
    asset = db.query(Asset).filter(Asset.symbol == symbol_db).first()
    if not asset:
        logger.error(f"{symbol_db} nahi mila database me! Pehle init_db run karein.")
        return

    logger.info(f"Yahoo Finance se pichle 5 din ka 5-min data nikal rahe hain for {symbol_db}...")
    
    df = yf.download(tickers=symbol_yf, period="5d", interval="5m", progress=False)
    
    if df.empty:
        logger.error(f"Koi data nahi aaya {symbol_db} ke liye!")
        return
        
    df = df.reset_index()
    records_added = 0
    for _, row in df.iterrows():
        timestamp = row['Datetime'] if 'Datetime' in row else row.iloc[0]
        
        if isinstance(timestamp, pd.Series):
            timestamp = timestamp.iloc[0]
            
        if getattr(timestamp, 'tzinfo', None) is None:
            timestamp = timestamp.replace(tzinfo=IST)
            
        exists = db.query(MarketData).filter(
            MarketData.asset_id == asset.id,
            MarketData.timestamp == timestamp
        ).first()
        
        if not exists:
            candle = MarketData(
                asset_id=asset.id,
                timeframe="5m",
                timestamp=timestamp,
                open=float(row['Open'].iloc[0] if isinstance(row['Open'], pd.Series) else row['Open']),
                high=float(row['High'].iloc[0] if isinstance(row['High'], pd.Series) else row['High']),
                low=float(row['Low'].iloc[0] if isinstance(row['Low'], pd.Series) else row['Low']),
                close=float(row['Close'].iloc[0] if isinstance(row['Close'], pd.Series) else row['Close']),
                volume=int(row['Volume'].iloc[0] if isinstance(row['Volume'], pd.Series) else row['Volume'])
            )
            db.add(candle)
            records_added += 1
            
    db.commit()
    logger.info(f"SUCCESS! {records_added} nayi rows {symbol_db} ke liye save ho gayi!")

def fetch_fast():
    db = SessionLocal()
    try:
        fetch_asset(db, "NIFTY 50", "^NSEI")
        fetch_asset(db, "CRUDE OIL (MCX)", "CL=F")
    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
        
    try:
        # After updating market data, generate the latest AI prediction
        logger.info("Generating live AI prediction for NIFTY 50...")
        generate_live_prediction("NIFTY 50")
        logger.info("Generating live AI prediction for CRUDE OIL (MCX)...")
        generate_live_prediction("CRUDE OIL (MCX)")
    except Exception as e:
        logger.error(f"Prediction Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fetch_fast()
