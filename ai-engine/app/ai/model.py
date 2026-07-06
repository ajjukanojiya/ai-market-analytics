import xgboost as xgb
from typing import Tuple
import joblib
import os
import logging

logger = logging.getLogger(__name__)

# Ensure models directory exists
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

class QuantModel:
    def __init__(self):
        # We use two models: Classifier for Direction (BUY/SELL), Regressor for exact Price.
        self.dir_model = xgb.XGBClassifier(
            n_estimators=100, 
            learning_rate=0.05, 
            max_depth=5,
            objective='binary:logistic'
        )
        
        self.price_model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            objective='reg:squarederror'
        )
        
    def train(self, X_train, y_dir_train, y_price_train):
        """Train both the direction and price models."""
        logger.info("Training Direction Model (Classifier)...")
        self.dir_model.fit(X_train, y_dir_train)
        
        logger.info("Training Price Model (Regressor)...")
        self.price_model.fit(X_train, y_price_train)
        
        logger.info("Training complete.")
        
    def predict(self, X):
        """Predict direction and next close price."""
        dir_pred = self.dir_model.predict(X)
        dir_prob = self.dir_model.predict_proba(X)
        price_pred = self.price_model.predict(X)
        return dir_pred, dir_prob, price_pred

    def save(self, prefix="nifty50"):
        """Save the trained models to disk."""
        joblib.dump(self.dir_model, os.path.join(MODEL_DIR, f"{prefix}_dir_model.joblib"))
        joblib.dump(self.price_model, os.path.join(MODEL_DIR, f"{prefix}_price_model.joblib"))
        logger.info(f"Models saved successfully to {MODEL_DIR}")

    def load(self, prefix="nifty50"):
        """Load trained models from disk."""
        dir_path = os.path.join(MODEL_DIR, f"{prefix}_dir_model.joblib")
        price_path = os.path.join(MODEL_DIR, f"{prefix}_price_model.joblib")
        
        if os.path.exists(dir_path) and os.path.exists(price_path):
            self.dir_model = joblib.load(dir_path)
            self.price_model = joblib.load(price_path)
            logger.info("Models loaded successfully.")
            return True
        else:
            logger.warning("Saved models not found.")
            return False
