import sys
import os
import yfinance as yf
import pandas as pd
import logging
from sqlalchemy.orm import Session

# Add parent directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.asset import Asset
from app.models.market_data import MarketData

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_historical_nifty(days=60):
    """
    Fetch the maximum allowed 5-minute data from Yahoo Finance (60 days max)
    for NIFTY 50 and save it to the PostgreSQL database.
    """
    symbol = "^NSEI" # NIFTY 50 symbol on Yahoo Finance
    logger.info(f"Fetching {days} days of 5-minute historical data for {symbol}...")
    
    try:
        # Fetch data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=f"{days}d", interval="5m")
        
        if df.empty:
            logger.error("No data returned from Yahoo Finance.")
            return
            
        df.reset_index(inplace=True)
        # Handle timezone (convert to naive UTC or keep as aware)
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        
        logger.info(f"Fetched {len(df)} 5-minute candles.")
        
        db: Session = SessionLocal()
        try:
            nifty = db.query(Asset).filter(Asset.symbol == "NIFTY 50").first()
            if not nifty:
                logger.error("NIFTY 50 asset not found in DB. Run init_db.py first.")
                return
                
            # Insert into database
            records_added = 0
            for _, row in df.iterrows():
                # Check if it already exists to avoid duplicates
                timestamp = row['Datetime']
                exists = db.query(MarketData).filter(
                    MarketData.asset_id == nifty.id,
                    MarketData.timestamp == timestamp
                ).first()
                
                if not exists:
                    candle = MarketData(
                        asset_id=nifty.id,
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
            logger.info(f"Successfully saved {records_added} new candles to PostgreSQL.")
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_historical_nifty(60)
