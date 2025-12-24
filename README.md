# 🌩️ StormAlert - Real-Time Stock Alert System

**Domain:** dv6280.online
**Status:** Production Deployed (Stable)

## 1. Project Overview
StormAlert is a high-performance, real-time stock alert system designed for the Indian Stock Market (NSE/BSE). It connects to the Zerodha Kite Connect WebSocket to track up to 500 stocks simultaneously. It detects price movements based on user-defined criteria (Trailing % and Rolling Timeframe %) and sends instant notifications via WhatsApp, Telegram, and Email.

### Core Features
- **Real-Time Ticker:** Consumes live ticks via WebSocket.
- **Alert Engine:** O(1) algorithm complexity for evaluating alerts against thousands of rules.
- **Dynamic Dashboard:** Next.js frontend with live WebSocket updates for system status and alerts.
- **Admin Panel:** Secure management of API keys and system configuration.
- **Production Hardening:** Dockerized, Nginx reverse proxy, SSL (Let's Encrypt), and robust error handling.

## 2. Technology Stack

### Backend (`/backend`)
- **Framework:** FastAPI (Python 3.11)
- **Asynchronous:** Fully async architecture using asyncio.
- **Authentication:** JWT (JSON Web Tokens) with Argon2 password hashing.
- **Database Driver:** Motor (Async MongoDB driver).
- **Key Libraries:** `kiteconnect` (Market Data), `pydantic` (Validation), `passlib[argon2]` (Security).

### Frontend (`/frontend`)
- **Framework:** Next.js 14 (App Router, TypeScript).
- **UI Library:** Shadcn/UI + Tailwind CSS.
- **State Management:** React Context + Hooks.
- **Real-Time:** Custom WebSocket hooks for live updates.
- **Charts:** Recharts for sparklines and analytics.

### Database & Infrastructure
- **Primary DB:** MongoDB (Dockerized).
- **Caching/Queue:** Redis (for task queues and fast caching).
- **Web Server:** Nginx (Reverse Proxy, SSL termination, Gzip).
- **Containerization:** Docker & Docker Compose.
- **OS:** Ubuntu Linux (VM).

## 3. Architecture & Data Flow

### Ticker Service (`backend/services/ticker.py`):
- Connects to KiteConnect WebSocket.
- Receives binary ticks.
- Pushes ticks to an asyncio.Queue (decoupled producer).

### Alert Engine (`backend/services/alert_engine.py`):
- Consumes ticks from the queue (consumer).
- Updates internal TokenCache and StockCache (in-memory).
- Evaluates RollingWindowAlgo and TrailingAlgo for every tick.
- Triggers alerts if thresholds are met.

### API Layer (`backend/main.py`):
- Exposes REST endpoints for Auth, Settings, and Dashboard.
- Exposes WebSocket endpoint (`/ws`) for frontend real-time updates.

### Frontend:
- Polls `/api/admin/system-status` for connectivity checks.
- Connects to `/ws` for live alert streaming.

## 4. Key Directory Structure
```text
StormAlert/
├── backend/
│   ├── main.py                 # Entry point, FastAPI app
│   ├── models/                 # Pydantic models (DB schema)
│   ├── routers/                # API routes (auth, stocks, admin)
│   ├── services/
│   │   ├── alert_engine.py     # Core logic for evaluating alerts
│   │   ├── kite_client.py      # Wrapper for Zerodha API
│   │   ├── ticker.py           # WebSocket client for market data
│   │   └── algorithms.py       # Rolling/Trailing math logic
│   ├── Dockerfile              # Backend container config
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── app/                    # Next.js App Router pages
│   ├── components/             # Reusable UI components
│   ├── lib/                    # Utilities (api.ts, utils.ts)
│   ├── Dockerfile              # Frontend container config
│   └── next.config.ts          # Next.js config (standalone output)
├── nginx/
│   ├── nginx.prod.conf         # Production Nginx config (SSL, Proxy)
│   └── Dockerfile              # Nginx container
├── docker-compose.prod.yml     # Production orchestration
└── .env.production             # Environment variables (Secrets)
```

### Required Environment Variables (.env)
- `KITE_API_KEY`: Your Zerodha Kite Connect API Key
- `KITE_API_SECRET`: Your Zerodha Kite Connect API Secret
- `TWILIO_SID`: Your Twilio Account SID (for WhatsApp)
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
- `TWILIO_FROM_NUMBER`: Your Twilio WhatsApp Number (e.g., `whatsapp:+14155238886`)
- `JWT_SECRET`: Secret key for token generation
- `MONGODB_URI`: Connection string for MongoDB

## 5. Deployment

The application is containerized and can be deployed using Docker Compose.

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```
