from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("KITE_API_KEY")
api_secret = os.getenv("KITE_API_SECRET")

if not api_key or not api_secret:
    print("Error: API_KEY or API_SECRET missing in .env")
    exit(1)

kite = KiteConnect(api_key=api_key)

print("--- Zerodha Access Token Generator ---")
print(f"API Key: {api_key}")

request_token = input("Enter the Request Token (from the URL): ").strip()

try:
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    print("\nSUCCESS! Here is your Access Token:")
    print("-" * 50)
    print(access_token)
    print("-" * 50)
    print("Copy this token and paste it into your .env file as ACCESS_TOKEN")
except Exception as e:
    print(f"\nError generating session: {e}")
