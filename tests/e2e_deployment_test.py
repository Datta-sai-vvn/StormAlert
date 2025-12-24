import asyncio
import aiohttp
import unittest
import os
from datetime import datetime

import uuid

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8003") # Test Port
ADMIN_EMAIL = f"test_user_{uuid.uuid4().hex[:8]}@stormalert.com"
ADMIN_PASSWORD = "test_password_123"

class TestDeployment(unittest.TestCase):
    async def asyncSetUp(self):
        self.session = aiohttp.ClientSession()

    async def asyncTearDown(self):
        await self.session.close()

    def run_async(self, coro):
        return asyncio.run(coro)

    def test_01_health_check(self):
        # /healthz is not exposed in prod Nginx, so we check /api/status/live which implies backend is up
        async def run():
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BASE_URL}/api/status/live") as resp:
                    self.assertEqual(resp.status, 200)
                    data = await resp.json()
                    self.assertIn("status", data)
        self.run_async(run())

    # def test_02_metrics_endpoint(self):
    #     # Not exposed in prod
    #     pass

    def test_03_admin_login_flow(self):
        async def run():
            async with aiohttp.ClientSession() as session:
                # 1. Register
                print(f"Registering {ADMIN_EMAIL}...")
                reg_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
                async with session.post(f"{BASE_URL}/api/auth/register", json=reg_data) as reg_resp:
                    if reg_resp.status != 200:
                        text = await reg_resp.text()
                        print(f"Registration failed: {reg_resp.status} - {text}")
                    self.assertIn(reg_resp.status, [200, 400]) # 400 if exists (unlikely with random)
                
                # 2. Login
                login_data = {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
                async with session.post(f"{BASE_URL}/api/auth/login", data=login_data) as login_resp:
                    self.assertEqual(login_resp.status, 200)
                    token_data = await login_resp.json()
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
                    print(f"System Status: {data['status']}")
        self.run_async(run())

if __name__ == "__main__":
    unittest.main()
