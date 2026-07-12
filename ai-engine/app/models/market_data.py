from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, BigInteger, Index
from sqlalchemy.sql import func
from app.db.session import Base

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False) # e.g., '1m', '5m', '15m'
    
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, default=0)
    oi = Column(BigInteger, default=0) # Open Interest (if available)

    # Advanced Features (Milestone 6)
    pcr_ratio = Column(Float, nullable=True, default=1.0) # Put-Call Ratio
    sentiment_score = Column(Float, nullable=True, default=0.0) # -1.0 to 1.0
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Create a composite index for fast querying by asset, timeframe, and timestamp
    __table_args__ = (
        Index('idx_asset_timeframe_timestamp', 'asset_id', 'timeframe', 'timestamp'),
    )
