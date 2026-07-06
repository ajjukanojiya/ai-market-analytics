import logging
import feedparser
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

class SentimentService:
    def __init__(self):
        self.sia = None
        self._initialize_nltk()
        
    def _initialize_nltk(self):
        try:
            nltk.download('vader_lexicon', quiet=True)
            self.sia = SentimentIntensityAnalyzer()
        except Exception as e:
            logger.error(f"Failed to initialize NLTK VADER: {e}")

    def get_live_sentiment(self, symbol="NIFTY"):
        """
        Fetch latest news from Yahoo Finance RSS and calculate sentiment score.
        Returns a score between -1.0 (Very Negative) to 1.0 (Very Positive).
        """
        if not self.sia:
            return 0.0
            
        try:
            # Yahoo Finance RSS feed for NIFTY 50 (represented by ^NSEI)
            # Or general Indian market news
            rss_url = "https://finance.yahoo.com/news/rssindex"
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                return 0.0
                
            total_compound = 0.0
            count = 0
            
            # Analyze top 10 news headlines
            for entry in feed.entries[:10]:
                text = entry.title + " " + getattr(entry, 'summary', '')
                score = self.sia.polarity_scores(text)
                total_compound += score['compound']
                count += 1
                
            if count == 0:
                return 0.0
                
            avg_sentiment = total_compound / count
            logger.info(f"Live News Sentiment for {symbol}: {avg_sentiment:.2f}")
            return avg_sentiment
            
        except Exception as e:
            logger.error(f"Error fetching News Sentiment: {e}")
            return 0.0

sentiment_service = SentimentService()
