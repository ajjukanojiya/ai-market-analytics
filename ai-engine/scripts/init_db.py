import sys
import os

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine, Base, SessionLocal
from app.models.asset import Asset
from app.models.market_data import MarketData
from app.models.prediction import Prediction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully.")
    
    db = SessionLocal()
    try:
        # Check if NIFTY 50 already exists
        nifty = db.query(Asset).filter(Asset.symbol == "NIFTY 50").first()
        if not nifty:
            logger.info("Adding NIFTY 50 to the database...")
            nifty = Asset(
                symbol="NIFTY 50",
                name="Nifty 50 Index",
                asset_type="INDEX",
                exchange="NSE",
                is_active=True
            )
            db.add(nifty)
            db.commit()
            logger.info("NIFTY 50 added.")
        else:
            logger.info("NIFTY 50 already exists in the database.")
    except Exception as e:
        logger.error(f"Error initializing DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
