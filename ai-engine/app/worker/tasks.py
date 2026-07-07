from app.worker.celery_app import celery_app
from app.services.dhan_service import dhan_service
from app.db.session import SessionLocal
from app.models.asset import Asset
from app.models.market_data import MarketData
import logging
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

# NIFTY 50 segment and instrument mapping for Dhan API
NIFTY_SECURITY_ID = "13"
NIFTY_EXCHANGE = "IDX_I" # Index segment
NIFTY_INSTRUMENT = "INDEX"

@celery_app.task(acks_late=True, name="fetch_nifty_live_data")
def fetch_nifty_live_data():
    """
    Fetches 5-min candle data for NIFTY 50 and saves to PostgreSQL.
    Intended to be run periodically via Celery Beat (e.g. every 5 mins).
    """
    logger.info("Starting task: fetch_nifty_live_data")
    db = SessionLocal()
    try:
        # 1. Ensure NIFTY 50 is tracked
        nifty = db.query(Asset).filter(Asset.symbol == "NIFTY 50").first()
        if not nifty:
            logger.error("NIFTY 50 not found in database. Run init_db.py first.")
            return "Failed: NIFTY 50 asset not found"

        # 2. Fetch data from Dhan API
        data = dhan_service.get_intraday_data(
            security_id=NIFTY_SECURITY_ID,
            exchange_segment=NIFTY_EXCHANGE,
            instrument_type=NIFTY_INSTRUMENT,
            interval=5
        )

        if not data:
            logger.warning("No data received from Dhan API.")
            return "No data"

        # 3. Parse and save to DB
        # The data format usually contains 'start_Time', 'open', 'high', 'low', 'close', 'volume'
        # Dhan returns lists of these values.
        try:
            # Dhan API returns 'timestamp' for the epoch times
            times = data.get("timestamp", data.get("start_Time", []))
            opens = data.get("open", [])
            highs = data.get("high", [])
            lows = data.get("low", [])
            closes = data.get("close", [])
            volumes = data.get("volume", [])
            
            records_added = 0
            
            from app.services.options_service import options_service
            from app.services.sentiment_service import sentiment_service
            from datetime import timezone, timedelta
            
            IST = timezone(timedelta(hours=5, minutes=30))
            
            for i in range(len(times)):
                # Convert timestamp from Dhan (which is usually a string or epoch)
                raw_timestamp = times[i]
                timestamp = dhan_service.dhan.convert_to_date_time(raw_timestamp)
                
                # Make it timezone aware (IST) so SQLAlchemy handles it properly
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=IST)
                
                # Check if this candle already exists in our DB to avoid duplicates
                existing = db.query(MarketData).filter(
                    MarketData.asset_id == nifty.id,
                    MarketData.timeframe == "5m",
                    MarketData.timestamp == timestamp
                ).first()
                
                if not existing:
                    # Fetch Advanced Features (Milestone 6)
                    # We only fetch this once per missing candle (usually just the latest one)
                    pcr_ratio = options_service.get_live_pcr("NIFTY 50")
                    sentiment_score = sentiment_service.get_live_sentiment("NIFTY")
                    
                    new_candle = MarketData(
                        asset_id=nifty.id,
                        timestamp=timestamp,
                        timeframe="5m",
                        open=opens[i],
                        high=highs[i],
                        low=lows[i],
                        close=closes[i],
                        volume=volumes[i] if volumes else 0,
                        oi=0,
                        pcr_ratio=pcr_ratio,
                        sentiment_score=sentiment_score
                    )
                    db.add(new_candle)
                    records_added += 1
            
            db.commit()
            logger.info(f"Successfully saved {records_added} new 5-minute candles for NIFTY 50.")
            
            # 4. Trigger AI Prediction
            if records_added > 0:
                from app.ai.predictor import generate_live_prediction
                logger.info("Triggering AI prediction model...")
                generate_live_prediction()
                
            return f"Saved {records_added} candles"
            
        except Exception as e:
            logger.error(f"Error parsing Dhan data: {e}")
            db.rollback()
            return f"Error: {e}"

    finally:
        db.close()
