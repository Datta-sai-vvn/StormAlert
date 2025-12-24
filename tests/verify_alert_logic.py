import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from backend.services.alert_engine import AlertEngine
from backend.models import SettingsInDB, AlgoMode, AlertType

class TestAlertLogic(unittest.TestCase):
    def setUp(self):
        self.engine = AlertEngine()
        # Mock DB and Notification Service
        self.engine.user_settings = {}
        self.engine.token_map = {}
        self.engine.alert_buffer = []
        self.engine.last_alert_time = {}
        # Mock connection manager
        self.engine.connection_manager = AsyncMock()
        
    def test_dip_alert(self):
        # Setup
        user_id = "user123"
        token = 123456
        symbol = "INFY"
        
        settings = SettingsInDB(
            user_id=user_id,
            algo_mode=AlgoMode.TRAILING,
            dip_threshold=1.0, # 1% drop
            rise_threshold=1.0,
            cooldown_minutes=0
        )
        
        self.engine.user_settings[user_id] = settings
        self.engine.token_map[token] = [(user_id, symbol)]
        
        # Execution
        async def run():
            # 1. Initial High Price
            await self.engine.process_ticks([{"instrument_token": token, "last_price": 100.0}])
            
            # 2. Drop by 1.5% (Price 98.5)
            await self.engine.process_ticks([{"instrument_token": token, "last_price": 98.5}])
            
        asyncio.run(run())
        
        # Assertion
        self.assertEqual(len(self.engine.alert_buffer), 1)
        alert = self.engine.alert_buffer[0]
        self.assertEqual(alert["alert_type"], AlertType.DIP)
        self.assertAlmostEqual(alert["change_percent"], 1.5)
        print("✅ DIP Alert Logic Verified")

    def test_spike_alert(self):
        # Setup
        user_id = "user123"
        token = 123456
        symbol = "INFY"
        
        settings = SettingsInDB(
            user_id=user_id,
            algo_mode=AlgoMode.TRAILING,
            dip_threshold=1.0, 
            rise_threshold=1.0, # 1% rise
            cooldown_minutes=0
        )
        
        self.engine.user_settings[user_id] = settings
        self.engine.token_map[token] = [(user_id, symbol)]
        
        # Execution
        async def run():
            # 1. Initial Low Price
            await self.engine.process_ticks([{"instrument_token": token, "last_price": 100.0}])
            
            # 2. Rise by 1.5% (Price 101.5)
            await self.engine.process_ticks([{"instrument_token": token, "last_price": 101.5}])
            
        asyncio.run(run())
        
        # Assertion
        self.assertEqual(len(self.engine.alert_buffer), 1)
        alert = self.engine.alert_buffer[0]
        self.assertEqual(alert["alert_type"], AlertType.SPIKE)
        self.assertAlmostEqual(alert["change_percent"], 1.5)
        print("✅ SPIKE Alert Logic Verified")

if __name__ == "__main__":
    unittest.main()
