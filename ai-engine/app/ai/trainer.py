import logging
from app.ai.preprocessing import fetch_data_from_db, add_technical_indicators, create_sequences
from app.ai.model import QuantModel
from app.db.session import SessionLocal
from app.models.asset import Asset
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_nifty_model():
    db = SessionLocal()
    try:
        nifty = db.query(Asset).filter(Asset.symbol == "NIFTY 50").first()
        if not nifty:
            logger.error("NIFTY 50 not found in database.")
            return
            
        logger.info("Fetching historical data from DB...")
        df = fetch_data_from_db(nifty.id)
        
        if len(df) < 100:
            logger.error(f"Not enough historical data (only {len(df)} rows). Need at least 100 rows to train.")
            return
            
        logger.info("Calculating Technical Indicators...")
        df = add_technical_indicators(df)
        
        logger.info("Creating Sequences for XGBoost Training (Lookback: 60)...")
        X, y_dir, y_price, scaler = create_sequences(df, lookback=60)
        
        if len(X) == 0:
            logger.error("Could not create sequences. Not enough data.")
            return
            
        # Split into training and testing
        X_train, X_test, y_dir_train, y_dir_test = train_test_split(X, y_dir, test_size=0.2, shuffle=False)
        _, _, y_price_train, y_price_test = train_test_split(X, y_price, test_size=0.2, shuffle=False)
        
        logger.info(f"Training on {len(X_train)} samples...")
        
        # Initialize and Train Model
        model = QuantModel()
        model.train(X_train, y_dir_train, y_price_train)
        
        # Save model
        model.save(prefix="nifty50_5m")
        
        # Basic Evaluation
        dir_preds, _, price_preds = model.predict(X_test)
        
        from sklearn.metrics import accuracy_score, mean_absolute_error
        acc = accuracy_score(y_dir_test, dir_preds)
        mae = mean_absolute_error(y_price_test, price_preds)
        
        logger.info("====================================")
        logger.info(f"Model Accuracy on Test Data: {acc * 100:.2f}%")
        logger.info(f"Price MAE on Test Data: ₹{mae:.2f}")
        logger.info("====================================")
        
    finally:
        db.close()

if __name__ == "__main__":
    train_nifty_model()
