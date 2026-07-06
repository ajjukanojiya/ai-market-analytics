import pandas as pd
import numpy as np
from typing import Tuple
from app.db.session import SessionLocal
from app.models.market_data import MarketData
from sklearn.preprocessing import MinMaxScaler
import logging

logger = logging.getLogger(__name__)

def fetch_data_from_db(asset_id: int) -> pd.DataFrame:
    """Fetch historical data for a specific asset and load it into a Pandas DataFrame."""
    db = SessionLocal()
    try:
        # Fetch data ordered by timestamp
        query = db.query(MarketData).filter(MarketData.asset_id == asset_id).order_by(MarketData.timestamp.asc())
        df = pd.read_sql(query.statement, db.bind)
        return df
    finally:
        db.close()

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate and add technical indicators (RSI, MA, etc.) to the DataFrame."""
    if df.empty:
        return df
        
    # Moving Averages
    df['SMA_10'] = df['close'].rolling(window=10).mean()
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    
    # RSI (Relative Strength Index)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema_12 = df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Price Rate of Change
    df['ROC_5'] = df['close'].pct_change(periods=5)
    
    # Fill NaN values that result from rolling windows
    df = df.fillna(0)
    return df

def create_sequences(df: pd.DataFrame, lookback: int = 60) -> Tuple[np.ndarray, np.ndarray, np.ndarray, MinMaxScaler]:
    """
    Creates sequences of 'lookback' length for training.
    Returns: X (features), y_dir (Direction: 1 for UP, 0 for DOWN), y_price (Next Close), and the fitted scaler.
    """
    features = ['open', 'high', 'low', 'close', 'volume', 'SMA_10', 'SMA_20', 'RSI_14', 'MACD', 'MACD_Signal', 'ROC_5']
    
    if len(df) < lookback + 1:
        logger.warning(f"Not enough data to create sequences of length {lookback}")
        return np.array([]), np.array([]), np.array([]), None
        
    data = df[features].values
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    X, y_dir, y_price = [], [], []
    
    for i in range(lookback, len(scaled_data) - 1):
        # Flatten the lookback window to a 1D array for XGBoost (which needs 2D inputs overall)
        window = scaled_data[i-lookback:i].flatten()
        X.append(window)
        
        # Target Price: Next candle's close
        next_close = data[i + 1, features.index('close')]
        current_close = data[i, features.index('close')]
        y_price.append(next_close)
        
        # Target Direction: 1 if next close > current close else 0
        direction = 1 if next_close > current_close else 0
        y_dir.append(direction)
        
    return np.array(X), np.array(y_dir), np.array(y_price), scaler
