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
from app.services.dhan_service import dhan_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

def fetch_asset(db, symbol_db, symbol_yf, dhan_args=None):
    asset = db.query(Asset).filter(Asset.symbol == symbol_db).first()
    if not asset:
        logger.error(f"{symbol_db} nahi mila database me! Pehle init_db run karein.")
        return

    records_added = 0
    
    # Try DHAN API first for real-time 0-latency intraday data
    dhan_success = False
    if dhan_args and dhan_service.dhan:
        try:
            logger.info(f"Dhan API se live intraday data fetch kar rahe hain for {symbol_db}...")
            data = dhan_service.get_intraday_data(
                security_id=dhan_args['sec_id'],
                exchange_segment=dhan_args['exch'],
                instrument_type=dhan_args['type'],
                interval=5
            )
            
            if data and len(data.get('start_Time', [])) > 0:
                for idx, ts_str in enumerate(data['start_Time']):
                    # Dhan format: "2024-01-01 09:15:00"
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=IST)
                    
                    exists = db.query(MarketData).filter(
                        MarketData.asset_id == asset.id,
                        MarketData.timestamp == ts
                    ).first()
                    
                    if not exists:
                        candle = MarketData(
                            asset_id=asset.id,
                            timeframe="5m",
                            timestamp=ts,
                            open=float(data['open'][idx]),
                            high=float(data['high'][idx]),
                            low=float(data['low'][idx]),
                            close=float(data['close'][idx]),
                            volume=int(data['volume'][idx]) if 'volume' in data else 0
                        )
                        db.add(candle)
                        records_added += 1
                
                db.commit()
                dhan_success = True
                logger.info(f"Dhan API SUCCESS! {records_added} nayi live rows {symbol_db} ke liye save ho gayi!")
        except Exception as e:
            logger.error(f"Dhan API fetch failed for {symbol_db}: {e}")

    # Fallback to Yahoo Finance if Dhan fails or is unconfigured
    if not dhan_success:
        logger.info(f"Yahoo Finance se pichle 5 din ka 5-min data nikal rahe hain for {symbol_db}...")
        df = yf.download(tickers=symbol_yf, period="5d", interval="5m", progress=False)
        
        if df.empty:
            logger.error(f"Koi data nahi aaya {symbol_db} ke liye!")
            return
            
        df = df.reset_index()
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
                open_p = float(row['Open'].iloc[0] if isinstance(row['Open'], pd.Series) else row['Open'])
                high_p = float(row['High'].iloc[0] if isinstance(row['High'], pd.Series) else row['High'])
                low_p = float(row['Low'].iloc[0] if isinstance(row['Low'], pd.Series) else row['Low'])
                close_p = float(row['Close'].iloc[0] if isinstance(row['Close'], pd.Series) else row['Close'])
                
                # Scale NYMEX Crude Oil USD data to INR MCX format (approximate)
                if "CRUDE" in symbol_db:
                    open_p = round(open_p * 83.5, 2)
                    high_p = round(high_p * 83.5, 2)
                    low_p = round(low_p * 83.5, 2)
                    close_p = round(close_p * 83.5, 2)
                    
                candle = MarketData(
                    asset_id=asset.id,
                    timeframe="5m",
                    timestamp=timestamp,
                    open=open_p,
                    high=high_p,
                    low=low_p,
                    close=close_p,
                    volume=int(row['Volume'].iloc[0] if isinstance(row['Volume'], pd.Series) else row['Volume'])
                )
                db.add(candle)
                records_added += 1
                
        db.commit()
        logger.info(f"Yahoo SUCCESS! {records_added} nayi rows {symbol_db} ke liye save ho gayi!")

def fetch_fast():
    db = SessionLocal()
    try:
        fetch_asset(db, "NIFTY 50", "^NSEI", dhan_args={"sec_id": "13", "exch": "IDX_I", "type": "INDEX"})
        fetch_asset(db, "CRUDE OIL (MCX)", "CL=F", dhan_args={"sec_id": "560977", "exch": "MCX_COMM", "type": "FUTCOM"})
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
