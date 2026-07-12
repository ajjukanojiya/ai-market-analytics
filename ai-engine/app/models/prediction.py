from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app.db.session import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    prediction_timeframe = Column(String(10), nullable=False) # Predict for next '30m'
    
    predicted_trend = Column(String(20), nullable=False) # BUY, SELL, HOLD
    expected_high = Column(Float, nullable=True)
    expected_low = Column(Float, nullable=True)
    expected_close = Column(Float, nullable=True)
    
    entry_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    target_1 = Column(Float, nullable=True)
    target_2 = Column(Float, nullable=True)
    target_3 = Column(Float, nullable=True)
    
    confidence_score = Column(Float, nullable=False) # 0.0 to 1.0
    
    status = Column(String(20), default="SCANNING") # SCANNING, ACTIVE_TRADE, CLOSED_WIN, CLOSED_LOSS
    risk_reward_ratio = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
