# Service Level Agreement (SLA) & Policy

## 1. Reliability Targets (SLOs)

| Component | Metric | Target (SLO) | Error Budget (Monthly) |
| :--- | :--- | :--- | :--- |
| **API Availability** | Uptime | 99.9% | ~43 minutes |
| **Alert Engine** | Processing Uptime | 99.95% | ~21 minutes |
| **WebSocket** | Connection Success | 99.5% | ~3.6 hours |
| **Notifications** | Delivery Latency | < 5s (p95) | N/A |
| **Token System** | Offline Duration | < 5 mins | N/A |

## 2. Incident Response Policy
*   **P1 (Critical)**: System Down, No Alerts, Data Loss.
    *   *Response Time*: < 15 mins.
    *   *Resolution*: < 2 hours.
*   **P2 (High)**: High Latency, Partial Notification Failure.
    *   *Response Time*: < 1 hour.
    *   *Resolution*: < 8 hours.
*   **P3 (Medium)**: UI Glitches, Non-Critical Bugs.
    *   *Response Time*: < 24 hours.

## 3. Maintenance Windows
*   Scheduled maintenance will occur on **Sundays 02:00 UTC**.
*   Users will be notified 24 hours in advance via Email/In-App.
