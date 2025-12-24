# 🧪 StormAlert Comprehensive Testing Plan

## 1. Objective
To verify the complete functionality of the StormAlert system, ensuring that:
- Backend services (API, Auth, Database) are healthy.
- Real-time components (Ticker, WebSocket, Alert Engine) are functioning correctly.
- The system can detect price movements and trigger alerts as expected.
- The Frontend is reachable and can connect to the backend.

## 2. Testing Strategy

### Phase 1: Infrastructure & Connectivity (Static Checks)
**Goal:** Ensure all services are up and communicating.
- **Tools:** `tests/e2e_deployment_test.py`, `tests/live_sanity_check.py`
- **Scope:**
    - API Health Check (`/healthz`)
    - Database Connection
    - Authentication Flow (Register/Login)
    - WebSocket Connectivity

### Phase 2: Real-Time Logic Verification (Dynamic Checks)
**Goal:** Verify the core value proposition (Alerts) without relying on live market data (which may be closed or unavailable).
- **Method:** Dependency Injection / Mocking.
- **New Test Script:** `tests/verify_alert_logic.py`
- **Steps:**
    1. Initialize `AlertEngine` in isolation.
    2. Create a mock User and Settings (e.g., Dip Threshold: 1%).
    3. Inject a sequence of "Tick" data directly into the engine (simulating a price drop).
    4. Assert that an `ALERT_NEW` event is generated and would be broadcasted.
    5. Verify the algorithm correctly calculates % change.

### Phase 3: Frontend & Integration
**Goal:** Verify the user experience.
- **Method:** Browser Simulation / Manual Verification steps.
- **Checks:**
    - Dashboard loads without errors.
    - "System Offline" vs "Online" status reflects backend state.
    - WebSocket connects and receives "Heartbeat" or "Tick" messages.

## 3. Execution Plan

### Step 1: Run Existing Sanity Checks
```bash
python -m unittest tests/e2e_deployment_test.py
python tests/live_sanity_check.py
```

### Step 2: Create and Run Logic Verification
Create `tests/verify_alert_logic.py` to test the math and alert triggering mechanism deterministically.

### Step 3: Deployment Verification (If applicable)
If testing against `dv6280.online`:
- Run `live_sanity_check.py` pointing to the production URL.
- Use `browser_subagent` (if available) to capture a screenshot of the dashboard.

## 4. Success Criteria
- [ ] All E2E tests pass (Auth, API).
- [ ] WebSocket connection is established successfully.
- [ ] `verify_alert_logic.py` confirms that a 1% drop triggers a DIP alert.
- [ ] No critical errors in backend logs.
