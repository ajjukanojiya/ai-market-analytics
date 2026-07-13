import sys
import os
import yfinance as yf
import pandas as pd
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

# Add parent directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.asset import Asset
from app.models.market_data import MarketData

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

def fetch_historical_data(days=60):
    """
    Fetch the maximum allowed 5-minute data from Yahoo Finance (60 days max)
    for tracked assets and save it to the PostgreSQL database.
    """
    assets_to_fetch = [
        {"db_symbol": "NIFTY 50", "yf_symbol": "^NSEI"},
        {"db_symbol": "CRUDEOIL", "yf_symbol": "CL=F"}
    ]
    
    db: Session = SessionLocal()
    try:
        for asset_info in assets_to_fetch:
            db_sym = asset_info["db_symbol"]
            yf_sym = asset_info["yf_symbol"]
            
            logger.info(f"Fetching {days} days of 5-minute historical data for {db_sym} ({yf_sym})...")
            
            asset = db.query(Asset).filter(Asset.symbol == db_sym).first()
            if not asset:
                logger.error(f"{db_sym} asset not found in DB. Skipping.")
                continue
                
            try:
                ticker = yf.Ticker(yf_sym)
                df = ticker.history(period=f"{days}d", interval="5m")
                
                if df.empty:
                    logger.error(f"No data returned from Yahoo Finance for {yf_sym}.")
                    continue
                    
                df.reset_index(inplace=True)
                df['Datetime'] = pd.to_datetime(df['Datetime'])
                
                logger.info(f"Fetched {len(df)} 5-minute candles for {db_sym}.")
                
                records_added = 0
                for _, row in df.iterrows():
                    timestamp = row['Datetime']
                    
                    if timestamp.tzinfo is None:
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
                            open=float(row['Open']),
                            high=float(row['High']),
                            low=float(row['Low']),
                            close=float(row['Close']),
                            volume=int(row['Volume'])
                        )
                        db.add(candle)
                        records_added += 1
                
                db.commit()
                logger.info(f"Successfully saved {records_added} new candles for {db_sym}.")
                
            except Exception as e:
                logger.error(f"Error fetching data for {db_sym}: {e}")
                db.rollback()
                
    finally:
        db.close()

if __name__ == "__main__":
    fetch_historical_data(60)