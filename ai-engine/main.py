from dotenv import load_dotenv
import os

from dhanhq import DhanContext, dhanhq

load_dotenv()

client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")

print("Connecting to Dhan...")

dhan_context = DhanContext(
    client_id=client_id,
    access_token=access_token
)

dhan = dhanhq(dhan_context)

print("✅ Dhan Connected")

print("Downloading Security Master...")

response = dhan.fetch_security_list(
    mode="compact",
    filename="data/security_id_list.csv"
)

print(response)