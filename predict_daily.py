import pandas as pd
import numpy as np
import pymysql
import joblib
from tensorflow.keras.models import load_model
import logging
from datetime import timedelta, date
import os
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection(db_config):
    return pymysql.connect(**db_config)

def create_predictions_table(cursor):
    query = """
    CREATE TABLE IF NOT EXISTS stock_predictions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(50),
        prediction_for_date DATE,
        predicted_price DECIMAL(15, 4),
        actual_price DECIMAL(15, 4) NULL,
        confidence_score DECIMAL(5, 2) NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(query)

    # Ensure the column exists if the table was created before
    alter_query = """
    ALTER TABLE stock_predictions 
    ADD COLUMN confidence_score DECIMAL(5, 2) NULL;
    """
    try:
        cursor.execute(alter_query)
    except Exception as e:
        # Ignore error if column already exists or syntax not supported in older MySQL
        pass

def main():
    SYMBOL = sys.argv[1] if len(sys.argv) > 1 else 'SBIN.NS'
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'market_data',
        'charset': 'utf8mb4'
    }
    MODEL_FILENAME = f'{SYMBOL}_lstm_model.keras'
    SCALER_FILENAME = f'{SYMBOL}_scaler.pkl'
    TIME_STEP = 60

    if not os.path.exists(MODEL_FILENAME) or not os.path.exists(SCALER_FILENAME):
        logging.error("Model or Scaler file not found. Please run training script first.")
        return
        
    logging.info(f"Loading Multivariate model from {MODEL_FILENAME}...")
    model = load_model(MODEL_FILENAME)
    scaler = joblib.load(SCALER_FILENAME)

    try:
        connection = get_db_connection(DB_CONFIG)
        
        # Fetch last 100 days (to allow RSI to warm up, and get 60 days of valid input)
        query = f"SELECT date, close, volume FROM historical_stock_data WHERE symbol = '{SYMBOL}' ORDER BY date DESC LIMIT 100"
        df = pd.read_sql(query, connection)
        
        if len(df) < TIME_STEP + 14:
            logging.error(f"Not enough data to calculate RSI and make a prediction.")
            return
            
        # Reverse to ascending order
        df = df.iloc[::-1].reset_index(drop=True)
        
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        df['rsi'] = df['rsi'].fillna(50)
        
        last_date = df['date'].iloc[-1]
        next_day = (pd.to_datetime(last_date) + timedelta(days=1)).date()
        
        # Prepare Multivariate Data
        features = df[['close', 'volume', 'rsi']].values
        
        # Scale using pre-fitted scaler
        scaled_data = scaler.transform(features)
        
        # Extract last 60 days for prediction
        last_60_days_scaled = scaled_data[-TIME_STEP:]
        
        # Reshape to [samples, time steps, features] -> [1, 60, 3]
        X_test = last_60_days_scaled.reshape(1, TIME_STEP, 3)
        
        # Predict
        predicted_scaled = model.predict(X_test)
        
        # Inverse transform (Wait, scaler was fitted on 3 features. We must pass 3 features to inverse_transform)
        # We only care about the first feature (Close price)
        dummy_array = np.zeros((1, 3))
        dummy_array[0, 0] = predicted_scaled[0][0] # Put scaled prediction in 'close' column
        predicted_price = scaler.inverse_transform(dummy_array)[0][0]
        
        # --- Calculate Confidence Score (Hybrid Approach) ---
        last_close = float(df['close'].iloc[-1])
        predicted_move_pct = abs((predicted_price - last_close) / last_close) * 100
        current_rsi = float(df['rsi'].iloc[-1])
        
        # Base confidence starts at 60%
        confidence = 60.0
        
        # 1. RSI Factor: Normal RSI (40-60) is trend-following (more confident). 
        # Extreme RSI (<30 or >70) might indicate reversal, slightly lower confidence if predicting continuation.
        if 40 <= current_rsi <= 60:
            confidence += 15
        elif 30 < current_rsi < 40 or 60 < current_rsi < 70:
            confidence += 5
        else:
            confidence -= 10 # Extreme RSI, lower confidence
            
        # 2. Movement Factor: If predicted move is between 0.5% and 2%, it's a realistic daily move.
        if 0.5 <= predicted_move_pct <= 2.0:
            confidence += 15
        elif predicted_move_pct > 3.0:
            confidence -= 15 # Too large move, suspicious for daily
        else:
            confidence += 5
            
        # Cap confidence between 10% and 95%
        confidence = max(10.0, min(95.0, confidence))
        # ----------------------------------------------------
        
        logging.info(f"--- MULTIVARIATE PREDICTION RESULT ---")
        logging.info(f"Symbol: {SYMBOL}")
        logging.info(f"Predicting for date: {next_day}")
        logging.info(f"Predicted Close Price: ₹{predicted_price:.2f}")
        logging.info(f"Confidence Score: {confidence:.2f}% (RSI: {current_rsi:.2f}, Pred Move: {predicted_move_pct:.2f}%)")
        
        with connection.cursor() as cursor:
            create_predictions_table(cursor)
            insert_query = """
            INSERT INTO stock_predictions (symbol, prediction_for_date, predicted_price, confidence_score)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (SYMBOL, next_day, float(predicted_price), float(confidence)))
            connection.commit()
            logging.info(f"Successfully saved prediction for {next_day}.")
            
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

if __name__ == "__main__":
    main()
