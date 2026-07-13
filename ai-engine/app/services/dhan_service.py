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
            self._init_dhan()
            
    def _init_dhan(self):
        try:
            from dhanhq import DhanContext
            context = DhanContext(self.client_id, self.access_token)
            self.dhan = dhanhq(context)
            logger.info("Dhan API client successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Dhan API client: {e}")
            self.dhan = None
            
    def update_credentials(self, client_id: str, access_token: str):
        """Dynamically update credentials and re-initialize client without restarting server."""
        self.client_id = client_id
        self.access_token = access_token
        self._init_dhan()
        # Also update the environment variable temporarily so if celery forks it might see it
        import os
        os.environ["DHAN_CLIENT_ID"] = client_id
        os.environ["DHAN_ACCESS_TOKEN"] = access_token
        
        # Restart or start WebSocket live feed
        self.stop_live_feed()
        self.start_live_feed()
            
    def _on_ws_message(self, ws, message):
        from app.services.ws_manager import manager
        import asyncio
        import time
        # The dhanhq WebSocket returns data. We parse it and broadcast to frontend.
        # It's an async callback if we use `async def`, but `dhanhq` might expect sync.
        # The frontend expects {"status": "live", "timestamp": ms, "data": [{"symbol": "NIFTY 50", "ltp": 24000, "change_pct": 0}]}
        
        if message and "type" in message and message["type"] == "Ticker Data":
            try:
                # Format depends on Dhan API response. For now, assuming standard parsed tick
                # For safety, let's just create a generic broadcast message
                ltp = message.get("LTP", 0.0)
                sec_id = str(message.get("Security_ID", ""))
                symbol = "NIFTY 50" if sec_id == "13" else "BANKNIFTY" if sec_id == "25" else "RELIANCE"
                
                payload = {
                    "status": "live",
                    "timestamp": int(time.time() * 1000),
                    "data": [
                        {
                            "symbol": symbol,
                            "ltp": ltp,
                            "change_pct": 0.0 # Will implement change tracking if needed
                        }
                    ]
                }
                
                # Broadcast asynchronously
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(manager.broadcast(payload))
            except Exception as e:
                logger.error(f"WebSocket parse error: {e}")

    def start_live_feed(self):
        """Start the Dhan Live MarketFeed WebSocket in a background thread."""
        if not self.client_id or not self.access_token:
            return
            
        try:
            from dhanhq import DhanContext
            from dhanhq.marketfeed import MarketFeed
            
            context = DhanContext(self.client_id, self.access_token)
            
            # Subscribe to NIFTY (13), BANKNIFTY (25) and RELIANCE (2885)
            # 0 = IDX (Index), 1 = NSE (Equity)
            instruments = [(0, "13"), (0, "25"), (1, "2885")]
            
            self.feed = MarketFeed(
                context, 
                instruments, 
                on_message=self._on_ws_message
            )
            
            import threading
            self.ws_thread = threading.Thread(target=self.feed.run_forever, daemon=True)
            self.ws_thread.start()
            logger.info("Dhan Live MarketFeed WebSocket started.")
        except Exception as e:
            logger.error(f"Error starting Dhan WebSocket: {e}")

    def stop_live_feed(self):
        """Stop the Dhan WebSocket feed."""
        try:
            if hasattr(self, 'feed') and self.feed:
                self.feed.close_connection()
            logger.info("Dhan Live MarketFeed WebSocket stopped.")
        except Exception as e:
            logger.error(f"Error stopping Dhan WebSocket: {e}")
            
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
