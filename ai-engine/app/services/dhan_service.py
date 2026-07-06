import logging
from datetime import date
from dhanhq import dhanhq
from app.core.config import settings

logger = logging.getLogger(__name__)

class DhanService:
    def __init__(self):
        self.client_id = settings.DHAN_CLIENT_ID
        self.access_token = settings.DHAN_ACCESS_TOKEN
        
        if not self.client_id or not self.access_token:
            logger.warning("Dhan API credentials are not set!")
            self.dhan = None
        else:
            from dhanhq import DhanContext
            context = DhanContext(self.client_id, self.access_token)
            self.dhan = dhanhq(context)
            
    def get_intraday_data(self, security_id: str, exchange_segment: str, instrument_type: str, interval: int = 5):
        """
        Fetch intraday minute data for a given security.
        Interval can be 1, 5, 15, 25, 60.
        """
        if not self.dhan:
            logger.error("Dhan API not initialized.")
            return None
            
        today = date.today().strftime("%Y-%m-%d")
        try:
            logger.info(f"Fetching {interval}-minute intraday data for {security_id} on {today}")
            response = self.dhan.intraday_minute_data(
                security_id=security_id,
                exchange_segment=exchange_segment,
                instrument_type=instrument_type,
                from_date=today,
                to_date=today,
                interval=interval
            )
            
            if response.get("status") == "success":
                return response.get("data")
            else:
                logger.error(f"Error fetching data from Dhan: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Exception while fetching Dhan data: {e}")
            return None

# Singleton instance
dhan_service = DhanService()
