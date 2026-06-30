import pymysql
import subprocess
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(message)s')

def main():
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'market_data',
        'charset': 'utf8mb4'
    }
    
    import sys
    provided_symbols = sys.argv[1:]
    
    if provided_symbols:
        symbols = provided_symbols
    else:
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT symbol FROM historical_stock_data")
                symbols = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Failed to fetch symbols from DB: {e}")
            return
        finally:
            if 'connection' in locals() and connection.open:
                connection.close()

    if not symbols:
        logging.info("No stocks found in the database.")
        return

    logging.info(f"\n=======================================================")
    logging.info(f" 🔄 Starting Bulk Update for {len(symbols)} stocks")
    logging.info(f" Stocks: {', '.join(symbols)}")
    logging.info(f"=======================================================\n")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = r"C:\Users\hp\AppData\Local\Programs\Python\Python312\python.exe"
    pipeline_script = os.path.join(script_dir, "run_pipeline.py")
    
    for symbol in symbols:
        logging.info(f"\n---> Triggering pipeline for {symbol} <---")
        result = subprocess.run([python_exe, pipeline_script, symbol], cwd=script_dir)
        if result.returncode != 0:
            logging.error(f"❌ Failed to update {symbol}")
        else:
            logging.info(f"✅ Successfully updated {symbol}")

    logging.info("\n🎉 All stocks updated successfully!")

if __name__ == "__main__":
    main()
