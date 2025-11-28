# Production MongoDB Setup Guide

## 1. ReplicaSet Configuration
For high availability, use a 3-node ReplicaSet (Primary-Secondary-Secondary).

### Docker Compose Setup
```yaml
services:
  mongo1:
    image: mongo:latest
    command: ["mongod", "--replSet", "rs0", "--bind_ip_all"]
  mongo2:
    image: mongo:latest
    command: ["mongod", "--replSet", "rs0", "--bind_ip_all"]
  mongo3:
    image: mongo:latest
    command: ["mongod", "--replSet", "rs0", "--bind_ip_all"]
```

### Initialization
```bash
docker-compose exec mongo1 mongosh --eval "rs.initiate({
 _id: 'rs0',
 members: [
   {_id: 0, host: 'mongo1:27017'},
   {_id: 1, host: 'mongo2:27017'},
   {_id: 2, host: 'mongo3:27017'}
 ]
})"
```

## 2. Security Hardening
*   **Authentication**: Enable Access Control (`--auth`).
*   **Encryption**: Enable TLS/SSL for all connections.
*   **Network**: Bind only to private IP or use Docker internal network.

## 3. Backup Strategy
*   **Daily**: Full Dump via `mongodump` to S3-compatible storage.
*   **Oplog**: Continuous backup for Point-in-Time Recovery (PITR).
*   **Retention**:
    *   Daily: 30 days
    *   Weekly: 3 months
    *   Monthly: 1 year

## 4. Indexing Strategy
Ensure all queries use indexes.
*   `{ "symbol": 1, "user_id": 1 }` (Unique)
*   `{ "timestamp": -1 }` (TTL Index for Logs)
