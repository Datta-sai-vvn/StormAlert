import pytest
from collections import deque
from datetime import datetime, timedelta
from backend.services.algorithms import RollingWindowAlgo, RollingWindowState
from backend.services.alert_engine import AlertEngine
from backend.models import SettingsInDB

# --- Rolling Window Algo Tests ---
def test_rolling_window_state_update():
    window = RollingWindowState(window_minutes=1)
    now = datetime.utcnow()
    
    # 1. Add initial price
    min_val, max_val = window.update(100, now)
    assert min_val == 100
    assert max_val == 100
    
    # 2. Add higher price
    min_val, max_val = window.update(110, now + timedelta(seconds=10))
    assert min_val == 100
    assert max_val == 110
    
    # 3. Add lower price
    min_val, max_val = window.update(90, now + timedelta(seconds=20))
    assert min_val == 90
    assert max_val == 110
    
    # 4. Expire the first high price (110)
    # Window is 60s. At T+75s, T+10 (110) should be gone? No, T+10 is at 10s.
    # Let's advance to T+80s. T=0 (100) and T+10 (110) and T+20 (90) are expired.
    # Wait, let's expire just the first one.
    # T=0 (100), T+10 (110), T+20 (90).
    # Advance to T+65. T=0 is expired. T+10 (110) remains.
    min_val, max_val = window.update(95, now + timedelta(seconds=65))
    # Window: [110 (10s), 90 (20s), 95 (65s)]
    assert max_val == 110
    assert min_val == 90
    
    # Advance to T+80. T+10 (110) expired.
    min_val, max_val = window.update(95, now + timedelta(seconds=80))
    # Window: [90 (20s), 95 (65s), 95 (80s)] -> Wait, 20s is also expired (80-20=60).
    # Actually 80-20 = 60. So 20s is just on the edge or expired.
    # Let's say strictly > 60.
    
    # Let's test explicit expiration
    window = RollingWindowState(window_minutes=1)
    window.update(100, now) # T=0
    window.update(120, now + timedelta(seconds=30)) # T=30
    
    # T=70. T=0 expired. Max should be 120.
    min_val, max_val = window.update(110, now + timedelta(seconds=70))
    assert max_val == 120
    
    # T=100. T=30 expired. Max should be 110.
    min_val, max_val = window.update(105, now + timedelta(seconds=100))
    assert max_val == 110

def test_rolling_window_algo_process_tick():
    algo = RollingWindowAlgo(window_minutes=10)
    token = 12345
    
    # Initial
    dip, spike = algo.process_tick(token, 100)
    assert dip == 0.0
    assert spike == 0.0
    
    # Price drops to 90 (10% dip)
    dip, spike = algo.process_tick(token, 90)
    assert dip == 10.0
    assert spike == 0.0
    
    # Price rises to 110 (from low of 90, that's 22% spike)
    # Window High = 100. Window Low = 90.
    # Current = 110.
    # Dip from High (110? No, window high updates to 110).
    # Wait, update happens first.
    # Window: 100, 90, 110. High=110, Low=90.
    # Dip = (110-110)/110 = 0.
    # Spike = (110-90)/90 = 22.22%
    dip, spike = algo.process_tick(token, 110)
    assert dip == 0.0
    assert abs(spike - 22.22) < 0.1

# --- Alert Engine Cache Tests ---
@pytest.mark.asyncio
async def test_alert_engine_caching():
    engine = AlertEngine()
    
    # Mock DB Data
    mock_settings = {
        "user_1": SettingsInDB(user_id="user_1", dip_threshold=1.0, rise_threshold=1.0, timeframe_minutes=10)
    }
    mock_token_map = {
        123: [("user_1", "INFY")]
    }
    
    # Manually inject cache
    engine.user_settings = mock_settings
    engine.token_map = mock_token_map
    engine.rolling_algos["user_1"] = RollingWindowAlgo(window_minutes=10)
    
    # Test process_ticks uses cache
    ticks = [{"instrument_token": 123, "last_price": 100, "timestamp": datetime.utcnow()}]
    
    # We need to mock trigger_alert to verify it's called
    called = False
    async def mock_trigger(*args, **kwargs):
        nonlocal called
        called = True
    
    engine.trigger_alert = mock_trigger
    
    # 1. Initial tick (no alert)
    await engine.process_ticks(ticks)
    assert not called
    
    # 2. Dip tick
    ticks[0]["last_price"] = 98 # 2% dip
    await engine.process_ticks(ticks)
    assert called
