#!/bin/bash

echo "======================================================="
echo "STORMALERT DEPLOYMENT DIAGNOSTIC TOOL"
echo "======================================================="
echo "Timestamp: $(date)"
echo ""

# 1. Check Docker Containers
echo "--- 1. Container Status ---"
docker compose -f docker-compose.prod.yml ps -a
echo ""

# 2. Check Frontend Environment Variables
echo "--- 2. Frontend Environment Variables ---"
echo "Checking if NEXT_PUBLIC_API_URL is set correctly inside the container..."
docker compose -f docker-compose.prod.yml exec frontend env | grep NEXT_PUBLIC || echo "WARNING: No NEXT_PUBLIC variables found!"
echo ""

# 3. Network Connectivity Checks
echo "--- 3. Internal Network Connectivity ---"

echo "[Test] Nginx -> Backend (Port 8000)"
docker compose -f docker-compose.prod.yml exec nginx curl -I -m 5 http://backend:8000/docs || echo "FAIL: Nginx cannot reach Backend"

echo ""
echo "[Test] Nginx -> Frontend (Port 3000)"
docker compose -f docker-compose.prod.yml exec nginx curl -I -m 5 http://frontend:3000 || echo "FAIL: Nginx cannot reach Frontend"

echo ""
echo "[Test] Frontend -> Backend (Port 8000)"
# Frontend is Node/Alpine, might not have curl, try wget
docker compose -f docker-compose.prod.yml exec frontend wget -q --spider http://backend:8000/docs && echo "SUCCESS: Frontend can reach Backend" || echo "FAIL: Frontend cannot reach Backend"

echo ""

# 4. Check Logs
echo "--- 4. Recent Logs (Backend - Last 50 lines) ---"
docker compose -f docker-compose.prod.yml logs backend --tail 50
echo ""

echo "--- 5. Recent Logs (Frontend - Last 50 lines) ---"
docker compose -f docker-compose.prod.yml logs frontend --tail 50
echo ""

echo "--- 6. Recent Logs (Nginx - Last 50 lines) ---"
docker compose -f docker-compose.prod.yml logs nginx --tail 50
echo ""

echo "======================================================="
echo "DIAGNOSTIC COMPLETE"
echo "Please copy the output above and share it."
echo "======================================================="
