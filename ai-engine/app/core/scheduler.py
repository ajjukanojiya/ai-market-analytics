import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = BackgroundScheduler()

def fetch_market_data_job():
    """
    This job will run every 5 minutes to fetch live data from Dhan API
    and save it to the MySQL database.
    """
    logger.info("Executing background job: Fetching live market data...")
    # TODO: Integration with Dhan API fetching logic here
    pass

def train_ai_model_job():
    """
    This job will run at the end of the day or every hour to retrain 
    or fine-tune the AI models with new data.
    """
    logger.info("Executing background job: Retraining AI models...")
    # TODO: Model training logic here
    pass

def start_scheduler():
    # Schedule fetching data every 5 minutes during market hours
    # E.g., Mon-Fri between 09:15 and 15:30
    scheduler.add_job(
        fetch_market_data_job, 
        trigger=CronTrigger(minute="*/5", hour="9-15", day_of_week="mon-fri"),
        id="fetch_data_5m",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Background Scheduler Started.")

def stop_scheduler():
    scheduler.shutdown()
    logger.info("Background Scheduler Stopped.")
