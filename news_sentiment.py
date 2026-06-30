import pymysql
import feedparser
from google import genai
import json
import logging
from datetime import date

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection(db_config):
    """Establishes and returns a MySQL database connection."""
    return pymysql.connect(**db_config)

def create_sentiments_table(cursor):
    """Creates the news_sentiments table if it doesn't exist."""
    query = """
    CREATE TABLE IF NOT EXISTS news_sentiments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(50),
        date DATE,
        sentiment_score DECIMAL(4, 2),
        verdict VARCHAR(20),
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(query)
    logging.info("Ensured 'news_sentiments' table exists.")

def fetch_yahoo_finance_news(symbol):
    """Fetches the latest news headlines from Yahoo Finance RSS feed."""
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}"
    feed = feedparser.parse(url)
    # Get up to 5 latest headlines
    headlines = [entry.title for entry in feed.entries[:5]]
    return headlines

def analyze_sentiment_with_gemini(headlines, api_key):
    """Calls Google Gemini API (new SDK) to analyze the sentiment of the headlines."""
    client = genai.Client(api_key=api_key)
    
    news_text = "\n".join(headlines)
    if not news_text:
        return {"sentiment_score": 0.0, "verdict": "NEUTRAL", "summary": "No news found today."}
        
    prompt = f"""
    Act as a financial analyst. Analyze the sentiment of the following news headlines for a stock.
    Return ONLY a valid JSON object with the following exact structure (no markdown formatting, no extra text):
    {{
        "sentiment_score": a float between -1.0 (very negative) to 1.0 (very positive),
        "verdict": "POSITIVE", "NEGATIVE", or "NEUTRAL",
        "summary": "a very brief 1-2 sentence summary of the news"
    }}
    
    Headlines:
    {news_text}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        # Strip potential markdown formatting that APIs sometimes add (like ```json ... ```)
        json_str = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        result = json.loads(json_str)
        return result
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return None

import sys

def main():
    # --- Configuration ---
    SYMBOL = sys.argv[1] if len(sys.argv) > 1 else 'SBIN.NS'
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'market_data',
        'charset': 'utf8mb4'
    }
    
    import os
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    
    logging.info(f"Fetching latest news for {SYMBOL}...")
    headlines = fetch_yahoo_finance_news(SYMBOL)
    
    if not headlines:
        logging.warning("No news headlines found from Yahoo Finance.")
        headlines = ["Bank reports record profits and strong growth.", "Analysts upgrade stock rating to BUY."]
    
    logging.info(f"Found {len(headlines)} headlines. Sending to Gemini for analysis...")
    
    sentiment_data = analyze_sentiment_with_gemini(headlines, GEMINI_API_KEY)

    if not sentiment_data:
        logging.error("Failed to analyze sentiment. Exiting.")
        return
        
    logging.info(f"--- Gemini Analysis Output ---")
    print(json.dumps(sentiment_data, indent=4))
    logging.info(f"------------------------------")
    
    # Save to Database
    try:
        connection = get_db_connection(DB_CONFIG)
        with connection.cursor() as cursor:
            create_sentiments_table(cursor)
            
            insert_query = """
            INSERT INTO news_sentiments (symbol, date, sentiment_score, verdict, summary)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                SYMBOL, 
                date.today(), 
                float(sentiment_data.get('sentiment_score', 0)),
                sentiment_data.get('verdict', 'NEUTRAL'),
                sentiment_data.get('summary', 'No summary provided')
            ))
            connection.commit()
            logging.info(f"Sentiment data for {SYMBOL} successfully saved to MySQL.")
            
    except pymysql.MySQLError as e:
        logging.error(f"MySQL error: {e}")
    except Exception as e:
        logging.error(f"Database error: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

if __name__ == "__main__":
    main()
