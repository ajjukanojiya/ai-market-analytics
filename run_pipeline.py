import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <SYMBOL>")
        print("Example: python run_pipeline.py RELIANCE.NS")
        sys.exit(1)
        
    symbol = sys.argv[1].upper()
    logging.info(f"\n=======================================================")
    logging.info(f" 🚀 Starting AI Analytics Pipeline for {symbol}")
    logging.info(f"=======================================================\n")
    
    scripts = [
        "fetch_stock_data.py",
        "train_lstm_model.py",
        "predict_daily.py",
        "news_sentiment.py"
    ]
    
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for script in scripts:
        logging.info(f"⏳ Running {script}...")
        # Use absolute path to Python 3.12 to avoid Python 3.14 missing libraries error
        python_exe = r"C:\Users\hp\AppData\Local\Programs\Python\Python312\python.exe"
        result = subprocess.run([python_exe, script, symbol], cwd=script_dir)
        
        if result.returncode != 0:
            logging.error(f"\n❌ Error encountered in {script}. Stopping pipeline.")
            sys.exit(1)
        else:
            logging.info(f"✅ {script} completed.\n")
            
    logging.info(f"🎉 Pipeline Complete! You can now search for {symbol} in your Dashboard.")

if __name__ == "__main__":
    main()
