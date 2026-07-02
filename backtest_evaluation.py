import pymysql
import sys
import logging
from datetime import date
import pandas as pd
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'market_data',
    'charset': 'utf8mb4'
}

def get_db_connection(db_config):
    """Establish a connection to the MySQL database."""
    return pymysql.connect(**db_config)

def create_accuracy_table(cursor):
    """Create the model_accuracy table if it does not exist."""
    query = """
    CREATE TABLE IF NOT EXISTS model_accuracy (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(50),
        evaluation_date DATE,
        mae DECIMAL(15, 4),
        accuracy_percentage DECIMAL(5, 2),
        days_evaluated INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(query)

def evaluate_accuracy(symbol):
    """
    Calculate the Mean Absolute Error (MAE) for the last 30 days of predictions
    and convert it into an Accuracy Percentage.
    """
    connection = get_db_connection(DB_CONFIG)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Ensure the output table exists
            create_accuracy_table(cursor)
            
            # Fetch the last 30 predictions with actual prices for the symbol
            query = """
                SELECT predicted_price, actual_price 
                FROM stock_predictions 
                WHERE symbol = %s AND actual_price IS NOT NULL
                ORDER BY prediction_for_date DESC
                LIMIT 30;
            """
            cursor.execute(query, (symbol,))
            results = cursor.fetchall()
            
            if not results:
                logging.warning(f"No completed predictions found for {symbol}. Cannot evaluate.")
                return
            
            df = pd.DataFrame(results)
            df['predicted_price'] = df['predicted_price'].astype(float)
            df['actual_price'] = df['actual_price'].astype(float)
            
            # Calculate Mean Absolute Error (MAE)
            df['absolute_error'] = np.abs(df['predicted_price'] - df['actual_price'])
            mae = df['absolute_error'].mean()
            
            # Calculate average actual price to determine percentage error
            avg_actual_price = df['actual_price'].mean()
            
            # Calculate Accuracy Percentage
            # E.g., if avg error is 2% of stock price, accuracy is 98%
            if avg_actual_price > 0:
                error_percentage = (mae / avg_actual_price) * 100
                accuracy_percentage = max(0.0, 100 - error_percentage) # Ensure it doesn't go below 0
            else:
                accuracy_percentage = 0.0
                
            days_evaluated = len(df)
            evaluation_date = date.today()
            
            # Insert the calculated accuracy into model_accuracy table
            insert_query = """
                INSERT INTO model_accuracy (symbol, evaluation_date, mae, accuracy_percentage, days_evaluated)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                symbol, 
                evaluation_date, 
                float(mae), 
                float(accuracy_percentage), 
                days_evaluated
            ))
            connection.commit()
            
            logging.info(f"--- Evaluation Results for {symbol} ---")
            logging.info(f"Days Evaluated: {days_evaluated}")
            logging.info(f"Mean Absolute Error (MAE): {mae:.4f}")
            logging.info(f"Accuracy Percentage: {accuracy_percentage:.2f}%")
            logging.info("Saved accuracy metrics to model_accuracy table.")
            
    except Exception as e:
        logging.error(f"Error during accuracy evaluation: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    symbol_to_evaluate = sys.argv[1] if len(sys.argv) > 1 else 'SBIN.NS'
    logging.info(f"Starting accuracy evaluation for {symbol_to_evaluate}...")
    evaluate_accuracy(symbol_to_evaluate)
