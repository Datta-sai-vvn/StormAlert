from kiteconnect import KiteConnect
import os
import random

class KiteClient:
    def __init__(self):
        self.api_key = os.getenv("KITE_API_KEY")
        self.api_secret = os.getenv("KITE_API_SECRET")
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.kite = None
        self.mock_mode = False
        
        self.instruments_cache = []
        
        if self.api_key and self.access_token:
            try:
                self.kite = KiteConnect(api_key=self.api_key)
                self.kite.set_access_token(self.access_token)
                print("KiteConnect Client Initialized")
            except Exception as e:
                print(f"Error initializing KiteConnect: {e}")
                if os.getenv("PRODUCTION_MODE", "false").lower() == "true":
                    raise RuntimeError("KiteConnect failed in Production Mode. Cannot switch to Mock.")
                self.mock_mode = True
        else:
        else:
            print("Warning: KiteConnect credentials missing. System will wait for Admin Token.")
            self.mock_mode = False # Do NOT enable mock mode in production
            self.kite = None

    def fetch_instruments(self):
        print("Fetching instruments...")
        if self.mock_mode:
            # DISABLED
            self.instruments_cache = []
            return

        if not self.kite:
             print("Kite client not initialized.")
             return

        try:
            # Fetch only NSE Equity for now to keep it simple/fast
            self.instruments_cache = self.kite.instruments("NSE")
            print(f"Cached {len(self.instruments_cache)} instruments.")
        except Exception as e:
            print(f"Error fetching instruments: {e}")
            self.instruments_cache = []

    def search_instruments(self, query: str):
        if not query:
            return []
        
        query = query.upper()
        results = []
        # Simple linear search (sufficient for <100k items in memory)
        # Prioritize startsWith, then contains
        for inst in self.instruments_cache:
            if inst["segment"] == "NSE" and inst["instrument_type"] == "EQ": # Filter for equity
                if inst["tradingsymbol"].startswith(query):
                    results.append(inst)
                elif query in inst["name"].upper():
                    results.append(inst)
            
            if len(results) >= 20: # Limit results
                break
        return results

    def get_quote(self, instruments):
        if self.mock_mode:
            return {}

        if not self.kite:
            return {}
        try:
            return self.kite.quote(instruments)
        except Exception as e:
            print(f"Error fetching quote: {e}")
            return {}

    def get_instruments(self):
        return self.instruments_cache

    def set_access_token(self, access_token):
        self.access_token = access_token
        if self.kite:
            self.kite.set_access_token(access_token)
        else:
            try:
                self.kite = KiteConnect(api_key=self.api_key)
                self.kite.set_access_token(access_token)
            except Exception as e:
                print(f"Error initializing KiteConnect in set_access_token: {e}")
        self.mock_mode = False # Disable mock mode if we set a token
        print(f"KiteClient access token updated. Mock Mode: {self.mock_mode}")

kite_client = KiteClient()
