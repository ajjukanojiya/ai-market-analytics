from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from dhanhq import DhanContext, dhanhq

load_dotenv()

client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")

context = DhanContext(client_id, access_token)
dhan = dhanhq(context)

print("✅ Connected")

today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

response = dhan.intraday_minute_data(
    security_id="2885",
    exchange_segment=dhanhq.NSE,
    instrument_type="EQUITY",
    from_date=yesterday,
    to_date=today,
    interval=5
)

print(response)