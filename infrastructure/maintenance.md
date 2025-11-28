# Maintenance & Operations Guide

## 1. Automated Backups
The `docker-compose.yml` includes a `mongo-backup` service that runs daily at 2:00 AM.
Backups are stored in `./backups`.

### Manual Backup
```bash
docker-compose exec mongodb mongodump --out /data/db/backup-$(date +%F)
docker cp stormalert_mongodb:/data/db/backup-$(date +%F) ./backups/
```

### Restore
```bash
docker cp ./backups/backup-2023-10-27 stormalert_mongodb:/data/db/
docker-compose exec mongodb mongorestore /data/db/backup-2023-10-27
```

## 2. Log Cleanup
To prevent logs from filling up disk space, run this script weekly via cron on the host:

**cleanup_logs.sh**
```bash
#!/bin/bash
# Delete logs older than 30 days
find ./logs -name "*.log" -type f -mtime +30 -delete
# Prune unused docker images
docker image prune -a -f --filter "until=168h"
```

## 3. SSL Renewal
Certbot is configured to check for renewal every 12 hours.
To force renewal:
```bash
docker-compose run --rm certbot renew --force-renewal
docker-compose restart nginx
```

## 4. Updates
To update the application:
```bash
git pull origin main
docker-compose up -d --build
```
