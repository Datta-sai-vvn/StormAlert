import asyncio
import aiohttp
import unittest
import os
from datetime import datetime

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8003") # Test Port
ADMIN_EMAIL = "admin@stormalert.com"
ADMIN_PASSWORD = "admin_password"

class TestDeployment(unittest.TestCase):
    async def asyncSetUp(self):
        self.session = aiohttp.ClientSession()

    async def asyncTearDown(self):
        await self.session.close()

    def run_async(self, coro):
        return asyncio.run(coro)

    def test_01_health_check(self):
        async def run():
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BASE_URL}/healthz") as resp:
                    self.assertEqual(resp.status, 200)
                    data = await resp.json()
                    self.assertEqual(data["status"], "ok")
        self.run_async(run())

    def test_02_metrics_endpoint(self):
        async def run():
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BASE_URL}/metrics") as resp:
                    self.assertEqual(resp.status, 200)
                    data = await resp.json()
                    self.assertIn("ticker", data)
                    self.assertIn("alert_engine", data)
        self.run_async(run())

    def test_03_admin_login_flow(self):
        async def run():
            async with aiohttp.ClientSession() as session:
                # 1. Register (if not exists) or Login
                # Try login first
                login_data = {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
                async with session.post(f"{BASE_URL}/api/auth/login", data=login_data) as resp:
                    if resp.status == 401:
                        # Register
                        reg_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
                        async with session.post(f"{BASE_URL}/api/auth/register", json=reg_data) as reg_resp:
                            if reg_resp.status == 200:
                                print("Registered Admin User")
                            elif reg_resp.status == 400:
                                print("User already exists (but login failed?)")
                        
                        # Retry Login
                        async with session.post(f"{BASE_URL}/api/auth/login", data=login_data) as login_resp:
                            self.assertEqual(login_resp.status, 200)
                            token_data = await login_resp.json()
                            self.assertIn("access_token", token_data)
                            return token_data["access_token"]
                    else:
                        self.assertEqual(resp.status, 200)
                        token_data = await resp.json()
                        self.assertIn("access_token", token_data)
                        return token_data["access_token"]

        token = self.run_async(run())
        self.assertIsNotNone(token)

    def test_04_system_status(self):
        async def run():
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BASE_URL}/api/status/live") as resp:
                    self.assertEqual(resp.status, 200)
                    data = await resp.json()
                    self.assertIn("status", data)
                    # Should be OFFLINE or ONLINE depending on state
                    print(f"System Status: {data['status']}")
        self.run_async(run())

if __name__ == "__main__":
    unittest.main()
