import unittest
import os
import asyncio
from unittest.mock import patch
from backend.services.ticker import TickerService
from backend.services.kite_client import KiteClient

class TestProductionMockBlock(unittest.TestCase):
    def setUp(self):
        # Force Production Mode
        os.environ["PRODUCTION_MODE"] = "true"
        # Ensure no credentials
        if "KITE_API_KEY" in os.environ: del os.environ["KITE_API_KEY"]
        if "ACCESS_TOKEN" in os.environ: del os.environ["ACCESS_TOKEN"]

    def tearDown(self):
        if "PRODUCTION_MODE" in os.environ: del os.environ["PRODUCTION_MODE"]

    def test_ticker_mock_block(self):
        service = TickerService()
        with self.assertRaises(RuntimeError) as cm:
            asyncio.run(service.start_mock_ticker())
        self.assertIn("Mock Ticker is NOT allowed in Production", str(cm.exception))

    def test_kite_client_mock_block(self):
        with self.assertRaises(RuntimeError) as cm:
            KiteClient()
        self.assertIn("KiteConnect failed in Production Mode", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
