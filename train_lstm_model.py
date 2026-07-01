import pandas as pd
import numpy as np
import psycopg2
import psycopg2.extras
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
import logging
import os
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_data_from_postgresql(db_config: dict, symbol: str) -> pd.DataFrame:
    logging.info(f"Fetching Multivariate data (Close, Volume) for {symbol}...")
    query = f"SELECT date, close, volume FROM historical_stock_data WHERE symbol = '{symbol}' ORDER BY date ASC"
    
    try:
        connection = psycopg2.connect(**db_config)
        df = pd.read_sql(query, connection)
        logging.info(f"Successfully fetched {len(df)} records.")
        return df
    except Exception as e:
        logging.error(f"Error fetching data from database: {e}")
        return pd.DataFrame()
    finally:
        if 'connection' in locals() and connection:
            connection.close()

def calculate_rsi(data, window=14):
    logging.info("Calculating RSI (Relative Strength Index)...")
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))
    data['rsi'] = data['rsi'].fillna(50) # Neutral RSI for first 14 days
    return data

def create_dataset(dataset: np.ndarray, time_step: int = 60):
    X, y = [], []
    for i in range(len(dataset) - time_step):
        X.append(dataset[i:(i + time_step), :]) # ALL Features (Close, Volume, RSI)
        y.append(dataset[i + time_step, 0])     # Predict Target (Close is at index 0)
    return np.array(X), np.array(y)

def main():
    SYMBOL = sys.argv[1] if len(sys.argv) > 1 else 'SBIN.NS'
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'postgres',
        'password': 'postgres',
        'database': 'market_data',
        'port': '5432'
    }
    TIME_STEP = 60
    EPOCHS = 20
    BATCH_SIZE = 32
    MODEL_FILENAME = f'{SYMBOL}_lstm_model.keras'

    # 1. Fetch data
    df = fetch_data_from_postgresql(DB_CONFIG, SYMBOL)
    if df.empty:
        logging.error("No data available to train the model. Exiting.")
        return

    # 2. Add Technical Indicators (RSI)
    df = calculate_rsi(df)
    
    # We now have 3 Features: Close, Volume, RSI
    features = df[['close', 'volume', 'rsi']].values

    # 3. Preprocess data using MinMaxScaler
    logging.info("Scaling 3D Multivariate data (0 to 1)...")
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(features)
    
    import joblib
    joblib.dump(scaler, f'{SYMBOL}_scaler.pkl')
    logging.info(f"Scaler saved as {SYMBOL}_scaler.pkl")

    # 4. Create sliding window dataset
    logging.info(f"Creating sliding window dataset with time_step={TIME_STEP}...")
    X, y = create_dataset(scaled_data, TIME_STEP)

    logging.info(f"Shape of X: {X.shape}, Shape of y: {y.shape}")

    # Split data into training and testing sets (80% train, 20% test)
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # 5. Build High-Accuracy Multivariate LSTM Network
    logging.info("Building Multivariate LSTM model architecture...")
    model = Sequential([
        Input(shape=(TIME_STEP, 3)), # 3 Features now!
        LSTM(units=50, return_sequences=True),
        Dropout(0.2),
        LSTM(units=50, return_sequences=False),
        Dropout(0.2),
        Dense(units=25),
        Dense(units=1) # Predicts 1 value (scaled close price)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.summary()

    # 6. Train the model
    logging.info(f"Training Multivariate Model for {EPOCHS} epochs...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        verbose=1
    )

    # 7. Save the trained model
    model.save(MODEL_FILENAME)
    logging.info(f"Model successfully saved as {MODEL_FILENAME} in {os.getcwd()}")

    # 8. Save the training loss graph
    logging.info("Generating training loss graph...")
    plt.figure(figsize=(10, 6))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title(f'LSTM Model Loss for {SYMBOL} (Multivariate)')
    plt.xlabel('Epoch')
    plt.ylabel('Loss (MSE)')
    plt.legend()
    
    plot_filename = f'{SYMBOL}_training_loss_graph.png'
    plt.savefig(plot_filename)
    logging.info(f"Training loss graph saved as '{plot_filename}'")
    plt.close()

if __name__ == "__main__":
    main()
