import unittest
from collections import deque
from backend.services.algorithms import TrailingAlgo, RollingWindowAlgo

class TestAlgorithms(unittest.TestCase):
    def test_trailing_algo(self):
        algo = TrailingAlgo()
        token = 123
        
        # Initial price
        algo.process_tick(token, 100.0)
        self.assertEqual(algo.state[token]['high'], 100.0)
        self.assertEqual(algo.state[token]['low'], 100.0)
        
        # Price goes up
        algo.process_tick(token, 110.0)
        self.assertEqual(algo.state[token]['high'], 110.0)
        
        # Price dips 10% from high (110 -> 99)
        dip, spike = algo.process_tick(token, 99.0)
        self.assertAlmostEqual(dip, 10.0)
        
        # Price goes down further
        algo.process_tick(token, 90.0)
        self.assertEqual(algo.state[token]['low'], 90.0)
        
        # Price spikes 10% from low (90 -> 99)
        dip, spike = algo.process_tick(token, 99.0)
        self.assertAlmostEqual(spike, 10.0)

    def test_rolling_window_algo(self):
        # 1 minute window for testing
        algo = RollingWindowAlgo(window_minutes=1)
        token = 456
        
        # Add ticks
        algo.process_tick(token, 100.0)
        algo.process_tick(token, 105.0)
        algo.process_tick(token, 95.0)
        
        # Current Window: [100, 105, 95] -> High: 105, Low: 95
        
        # New tick 90.0 -> Dip from 105 is (15/105)*100 = 14.28%
        dip, spike = algo.process_tick(token, 90.0)
        self.assertAlmostEqual(dip, 14.2857, places=2)
        
        # New tick 110.0 -> Spike from 90 (min in window now includes 90) is (20/90)*100 = 22.22%
        # Window: [100, 105, 95, 90, 110] -> Low: 90
        dip, spike = algo.process_tick(token, 110.0)
        self.assertAlmostEqual(spike, 22.22, places=2)

if __name__ == '__main__':
    unittest.main()
