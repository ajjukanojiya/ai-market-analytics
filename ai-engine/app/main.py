from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.market_data import MarketData
from app.models.prediction import Prediction
from app.models.asset import Asset
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration for Frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow Next.js frontend to access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

IST = timezone(timedelta(hours=5, minutes=30))

@app.get("/")
def root():
    return {"message": "Welcome to AI Market Analytics Engine API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get(f"{settings.API_V1_STR}/market-data/latest")
def get_latest_market_data(db: Session = Depends(get_db)):
    """Fetch the latest 50 candles for the frontend chart."""
    nifty = db.query(Asset).filter(Asset.symbol == "NIFTY 50").first()
    if not nifty:
        return {"error": "NIFTY 50 not found"}
        
    data = db.query(MarketData).filter(MarketData.asset_id == nifty.id).order_by(MarketData.timestamp.desc()).limit(50).all()
    result = []
    for d in reversed(data):
        item = d.__dict__.copy()
        item.pop('_sa_instance_state', None)
        
        # Ensure timezone is IST so frontend displays it correctly
        if isinstance(item.get('timestamp'), datetime) and item['timestamp'].tzinfo is None:
            item['timestamp'] = item['timestamp'].replace(tzinfo=IST)
            
        result.append(item)
    return {"data": result}

@app.get(f"{settings.API_V1_STR}/predictions/latest")
def get_latest_prediction(db: Session = Depends(get_db)):
    """Fetch the most recent AI prediction."""
    nifty = db.query(Asset).filter(Asset.symbol == "NIFTY 50").first()
    if not nifty:
        return {"error": "NIFTY 50 not found"}
        
    pred = db.query(Prediction).filter(Prediction.asset_id == nifty.id).order_by(Prediction.timestamp.desc()).first()
    if not pred:
        return {"error": "No predictions available yet."}
        
    pred_dict = pred.__dict__
    pred_dict.pop('_sa_instance_state', None)
    
    # Ensure timezone is IST so frontend displays it correctly
    if isinstance(pred_dict.get('timestamp'), datetime) and pred_dict['timestamp'].tzinfo is None:
        pred_dict['timestamp'] = pred_dict['timestamp'].replace(tzinfo=IST)
        
    return {"prediction": pred_dict}
