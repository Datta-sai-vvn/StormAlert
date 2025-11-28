import asyncio
import time
import random
import os
from datetime import datetime
from backend.services.alert_engine import AlertEngine
from backend.models import SettingsInDB, AlgoMode

# Mock DB
class MockDB:
    def __getitem__(self, item):
        return self

    def find(self, *args, **kwargs):
        return self
    
    async def to_list(self, *args, **kwargs):
        return []

    async def insert_many(self, *args, **kwargs):
        pass

# Patch DB
import backend.database
backend.database.db = MockDB()

async def run_stress_test():
    print("="*50)
    print("🔥 STARTING STRESS TEST: 500 Stocks, 1000 Ticks/sec")
    print("="*50)

    engine = AlertEngine()
    engine.alert_buffer = [] # Manually init buffer
    engine.queue = asyncio.Queue() # Manually init queue
    
    # 1. Setup Mock Cache
    # 500 Stocks
    engine.token_map = {i: [(f"user_{i%10}", f"STOCK_{i}")] for i in range(1, 501)}
    
    # 10 Users with different settings
    engine.user_settings = {
        f"user_{i}": SettingsInDB(
            user_id=f"user_{i}",
            dip_threshold=1.0,
            rise_threshold=1.0,
            algo_mode=AlgoMode.BOTH
        ) for i in range(10)
    }
    
    print(f"Loaded {len(engine.token_map)} stocks and {len(engine.user_settings)} users.")

    # 2. Generate Load
    start_time = time.time()
    total_ticks = 0
    
    for batch in range(10): # Run for 10 batches
        ticks = []
        for _ in range(1000): # 1000 ticks per batch
            token = random.randint(1, 500)
            ticks.append({
                "instrument_token": token,
                "last_price": 100.0 + random.uniform(-5, 5),
                "change": random.uniform(-2, 2),
                "timestamp": datetime.now()
            })
        
        batch_start = time.time()
        await engine.process_ticks(ticks)
        batch_duration = time.time() - batch_start
        
        total_ticks += len(ticks)
        print(f"Batch {batch+1}: Processed {len(ticks)} ticks in {batch_duration*1000:.2f}ms")
        
        # Simulate 1 sec interval (if processing is fast)
        if batch_duration < 1.0:
            await asyncio.sleep(0.1) 

    total_duration = time.time() - start_time
    print("="*50)
    print(f"✅ STRESS TEST COMPLETE")
    print(f"Total Ticks: {total_ticks}")
    print(f"Total Time: {total_duration:.2f}s")
    print(f"Avg Throughput: {total_ticks/total_duration:.2f} ticks/sec")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_stress_test())
