from collections import deque
from typing import Dict, Optional, Tuple
from datetime import datetime
from backend.models import AlgoMode

class TrailingAlgo:
    def __init__(self):
        # Stores state for each token: {token_id: {'high': float, 'low': float}}
        self.state: Dict[int, Dict[str, float]] = {}

    def process_tick(self, token: int, price: float) -> Tuple[Optional[str], Optional[float]]:
        """
        Returns (alert_type, change_percent) if alert triggered, else (None, None)
        """
        if token not in self.state:
            self.state[token] = {'high': price, 'low': price}
            return None, None

        data = self.state[token]
        
        # Update High/Low
        if price > data['high']:
            data['high'] = price
        if price < data['low']:
            data['low'] = price

        # Check for Dip from High
        dip_percent = ((data['high'] - price) / data['high']) * 100
        
        # Check for Spike from Low
        spike_percent = ((price - data['low']) / data['low']) * 100

        return dip_percent, spike_percent

class RollingWindowState:
    def __init__(self, window_minutes: int):
        self.window_seconds = window_minutes * 60
        self.data = deque() # Stores (timestamp, price)
        self.min_deque = deque() # Stores (timestamp, price) for min tracking
        self.max_deque = deque() # Stores (timestamp, price) for max tracking

    def update(self, price: float, timestamp: datetime) -> Tuple[float, float]:
        # 1. Remove expired items from data
        while self.data and (timestamp - self.data[0][0]).total_seconds() > self.window_seconds:
            self.data.popleft()
        
        # 2. Remove expired items from min/max deques
        while self.min_deque and (timestamp - self.min_deque[0][0]).total_seconds() > self.window_seconds:
            self.min_deque.popleft()
        while self.max_deque and (timestamp - self.max_deque[0][0]).total_seconds() > self.window_seconds:
            self.max_deque.popleft()

        # 3. Maintain Monotonic Properties
        # Min Deque: Increasing order (front is min)
        while self.min_deque and self.min_deque[-1][1] >= price:
            self.min_deque.pop()
        self.min_deque.append((timestamp, price))

        # Max Deque: Decreasing order (front is max)
        while self.max_deque and self.max_deque[-1][1] <= price:
            self.max_deque.pop()
        self.max_deque.append((timestamp, price))

        # 4. Add to data
        self.data.append((timestamp, price))

        # 5. Return current Min/Max
        return self.min_deque[0][1], self.max_deque[0][1]

class RollingWindowAlgo:
    def __init__(self, window_minutes: int = 10):
        self.window_minutes = window_minutes
        # Stores state: {token_id: RollingWindowState}
        self.state: Dict[int, RollingWindowState] = {}

    def process_tick(self, token: int, price: float) -> Tuple[Optional[float], Optional[float]]:
        now = datetime.utcnow()
        
        if token not in self.state:
            self.state[token] = RollingWindowState(self.window_minutes)

        window_state = self.state[token]
        window_low, window_high = window_state.update(price, now)

        if window_high == 0: return 0.0, 0.0

        dip_percent = ((window_high - price) / window_high) * 100
        spike_percent = ((price - window_low) / window_low) * 100

        return dip_percent, spike_percent
