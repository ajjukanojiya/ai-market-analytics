import logging
from app.db.session import SessionLocal
from app.models.asset import Asset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    db = SessionLocal()
    try:
        # Seed NIFTY 50 if it doesn't exist
        symbol = "NIFTY 50"
        existing_asset = db.query(Asset).filter(Asset.symbol == symbol).first()
        if not existing_asset:
            nifty = Asset(symbol=symbol, exchange="NSE", is_active=True)
            db.add(nifty)
            db.commit()
            logger.info(f"Successfully added {symbol} to tracked assets.")
        else:
            logger.info(f"{symbol} already exists in tracked assets.")
    except Exception as e:
        logger.error(f"Error initializing DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
