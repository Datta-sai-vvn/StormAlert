# Blue-Green Deployment & Canary Strategy

## 1. Blue-Green Deployment
We maintain two identical production environments: **Blue** (Live) and **Green** (Idle/Staging).

### Workflow
1.  **Deploy to Green**: New version (v2) is deployed to the Green environment.
2.  **Smoke Test**: Run automated E2E tests against Green.
3.  **Switch Traffic**: Update Nginx Load Balancer to point to Green.
4.  **Monitor**: Watch error rates and latency for 15 minutes.
5.  **Rollback (if needed)**: Instantly switch Nginx back to Blue.
6.  **Decommission Blue**: Once Green is stable, Blue becomes the new Staging.

### Nginx Configuration for Switching
```nginx
upstream backend_cluster {
    # Blue (Active)
    # server backend_blue:8000;
    
    # Green (New)
    server backend_green:8000;
}
```

## 2. Canary Releases
For risky changes, we use a weighted routing strategy.

### Nginx Weighted Routing
```nginx
upstream backend_cluster {
    # 95% traffic to Stable
    server backend_stable:8000 weight=95;
    
    # 5% traffic to Canary
    server backend_canary:8000 weight=5;
}
```

## 3. Rollback Triggers
Automatic rollback is triggered if:
*   Error Rate (5xx) > 1%
*   Latency (p95) > 500ms
*   WebSocket Disconnects > 10/min
