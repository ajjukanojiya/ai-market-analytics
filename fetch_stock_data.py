import yfinance as yf
import pandas as pd
import psycopg2
import psycopg2.extras
import logging
import time

# Set up logging for better visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_and_clean_data(symbol: str, period: str = "5y") -> pd.DataFrame:
    """
    Fetches historical stock data from Yahoo Finance and cleans it.
    """
    logging.info(f"Fetching data for {symbol} for the last {period}...")
    for attempt in range(3):
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            
            if df.empty:
                logging.warning(f"No data found for symbol {symbol}.")
                return pd.DataFrame()

            # Reset index to make 'Date' a column instead of an index
            df.reset_index(inplace=True)
            
            # Clean data: Rename columns to match database schema (lowercase)
            df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }, inplace=True)
            
            # Ensure date is in proper YYYY-MM-DD format suitable for PostgreSQL DATE type
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            # Handle missing values (forward fill, then backward fill)
            df.ffill(inplace=True)
            df.bfill(inplace=True)
            
            # Add the stock symbol column
            df['symbol'] = symbol
            
            # Select and order required columns
            df = df[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']]
            
            logging.info(f"Successfully fetched and cleaned {len(df)} records for {symbol}.")
            return df

        except Exception as e:
            logging.error(f"Attempt {attempt + 1}/3 failed for {symbol}: {e}")
            if attempt < 2:
                time.sleep(10)
                continue
            logging.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

    logging.error(f"All retry attempts failed for {symbol}.")
    return pd.DataFrame()

def upsert_to_postgresql(df: pd.DataFrame, db_config: dict):
    """
    Connects to PostgreSQL, creates the table if it doesn't exist, and upserts data.
    """
    if df.empty:
        logging.info("DataFrame is empty. Nothing to insert.")
        return

    # Note: We use a composite primary key (symbol, date) so that the table 
    # can store data for multiple different stocks without conflict.
    create_table_query = """
    CREATE TABLE IF NOT EXISTS historical_stock_data (
        symbol VARCHAR(50),
        date DATE,
        open DECIMAL(15, 4),
        high DECIMAL(15, 4),
        low DECIMAL(15, 4),
        close DECIMAL(15, 4),
        volume BIGINT,
        PRIMARY KEY (symbol, date)
    );
    """
    
    # Upsert query using PostgreSQL ON CONFLICT DO UPDATE
    upsert_query = """
    INSERT INTO historical_stock_data (symbol, date, open, high, low, close, volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (symbol, date) DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume;
    """

    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(**db_config)
        with connection.cursor() as cursor:
            # Create table if it doesn't exist
            logging.info("Checking/creating table 'historical_stock_data'...")
            cursor.execute(create_table_query)
            
            # Prepare data tuples for bulk execution
            data_tuples = list(df.itertuples(index=False, name=None))
            
            # Execute the upsert query in bulk
            logging.info("Upserting data into PostgreSQL...")
            cursor.executemany(upsert_query, data_tuples)
            
            # Commit the transaction
            connection.commit()
            logging.info(f"Successfully upserted {len(data_tuples)} records.")

    except psycopg2.Error as e:
        logging.error(f"PostgreSQL error: {e}")
    except Exception as e:
        logging.error(f"Error during database operation: {e}")
    finally:
        # Ensure the connection is always closed
        if 'connection' in locals() and connection:
            connection.close()
            logging.info("PostgreSQL connection closed.")

if __name__ == "__main__":
    # --- Configuration ---
    import sys
    # Target stock symbol (Yahoo Finance format)
    SYMBOL = sys.argv[1] if len(sys.argv) > 1 else 'SBIN.NS'
    
    # PostgreSQL Database Configuration
    # IMPORTANT: Update these credentials and ensure the database exists.
    # You can create the database manually via: CREATE DATABASE market_data;
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'postgres',         # Default PostgreSQL username
        'password': 'postgres',             # Update with your PostgreSQL password if set
        'database': 'market_data',  # Ensure you create this DB first
        'port': '5432'              # Default PostgreSQL port
    }

    # Step 1: Fetch and clean the historical data
    stock_df = fetch_and_clean_data(SYMBOL, period="5y")

    # Step 2: Upsert the data into the local PostgreSQL database
    upsert_to_postgresql(stock_df, DB_CONFIG)
