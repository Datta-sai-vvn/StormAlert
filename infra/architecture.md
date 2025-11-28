# Cloud Architecture & Infrastructure Design

**Date**: 2025-11-27
**Status**: APPROVED

## 1. Cloud Provider Selection
**Selected Option**: **Option A — DigitalOcean Droplets (with Docker Swarm/Compose)**

**Reasoning**:
*   **Cost-Efficiency**: Predictable pricing model ideal for the current scale.
*   **Simplicity**: Easier to manage Docker Compose/Swarm setups compared to full K8s (EKS) for this team size.
*   **Scalability**: Vertical scaling (Droplet resize) and Horizontal scaling (Adding nodes) are straightforward.

## 2. Infrastructure Components

### A. Compute Layer (Droplets)
*   **Load Balancer Node**: 1x Basic Droplet (2 vCPU, 4GB RAM) running Nginx.
*   **App Cluster**: 2x General Purpose Droplets (4 vCPU, 8GB RAM) running Docker Swarm/Compose.
    *   *Backend Replicas*: 3 instances distributed across nodes.
    *   *Frontend*: 2 instances.
    *   *Workers*: 2 instances for Notifications/Alerts.

### B. Data Layer
*   **Database**: Managed MongoDB (DigitalOcean Managed DB) or Self-Hosted ReplicaSet on dedicated Droplets.
    *   *Decision*: **Self-Hosted on Dedicated Droplet** (for cost control initially) with automated backups.
*   **Caching/Queue**: Redis (Self-Hosted Docker container).

### C. Networking
*   **VPC**: Private networking enabled between all Droplets.
*   **Firewall**:
    *   Inbound: 80/443 (LB only), 22 (Bastion only).
    *   Outbound: All allowed.

## 3. Deployment Architecture
```mermaid
graph TD
    User[User Traffic] --> LB[Nginx Load Balancer (SSL)]
    LB -->|Round Robin| BE1[Backend Instance 1]
    LB -->|Round Robin| BE2[Backend Instance 2]
    LB -->|Round Robin| BE3[Backend Instance 3]
    LB --> FE[Frontend Next.js]
    
    BE1 & BE2 & BE3 --> DB[(MongoDB ReplicaSet)]
    BE1 & BE2 & BE3 --> Redis[(Redis Queue)]
    
    Worker[Notification Worker] --> Redis
    Worker --> Ext[External APIs (SendGrid/Twilio)]
```

## 4. Scaling Strategy
*   **Horizontal**: Add more Backend containers via `docker-compose up --scale backend=N`.
*   **Vertical**: Resize Droplets if memory pressure increases.
*   **Database**: Enable Read Replicas if read throughput > 1000 ops/sec.
