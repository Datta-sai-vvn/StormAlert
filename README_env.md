# Environment Variables Guide

## System Configuration
*   `PRODUCTION_MODE`: Set to `true` to enable strict security checks and disable mock data.
*   `JWT_SECRET`: A long, random string used to sign JSON Web Tokens. **Critical for security.**
*   `ALLOWED_ORIGINS`: Comma-separated list of allowed domains for CORS (e.g., `https://yourdomain.com`).

## Database
*   `DATABASE_URL`: Connection string for MongoDB. In Docker Compose, use `mongodb://mongodb:27017/stormalert`.
*   `DB_NAME`: Name of the database (default: `stormalert`).

## Zerodha Kite Connect
*   `KITE_API_KEY`: Your Kite Connect API Key.
*   `KITE_API_SECRET`: Your Kite Connect API Secret.
*   **Note**: These are required for the system to start in Production Mode.

## Notifications
*   `SMTP_*`: Settings for sending emails via SMTP (e.g., Gmail, AWS SES).
*   `TWILIO_*`: Credentials for sending WhatsApp messages via Twilio.
*   `TELEGRAM_BOT_TOKEN`: Token for your Telegram Bot.
