require('dotenv').config();
const KiteTicker = require("kiteconnect").KiteTicker;
const Redis = require("ioredis");

// Initialize Redis Client (Upstash)
// Initialize Redis Client (Upstash)
// Force 'rediss://' (TLS) if it comes as 'redis://' for Upstash
let redisUrl = process.env.UPSTASH_REDIS_URL;
if (redisUrl && redisUrl.startsWith('redis://')) {
    redisUrl = redisUrl.replace('redis://', 'rediss://');
}
const redis = new Redis(redisUrl, {
    family: 0, // Auto-detect IPv4/IPv6 (Safer)
    tls: {
        rejectUnauthorized: false
    },
    maxRetriesPerRequest: null
});

// Initialize Kite Ticker
const ticker = new KiteTicker({
    api_key: process.env.KITE_API_KEY,
    access_token: process.env.KITE_ACCESS_TOKEN
});

// Vercel Webhook URL
const VERCEL_WEBHOOK_URL = process.env.VERCEL_URL
    ? `${process.env.VERCEL_URL}/api/webhooks/ticker`
    : null;

ticker.autoReconnect(true, 10, 5);

ticker.on("connect", () => {
    console.log("Connected to Kite Ticker");
    subscribeToTokens();
});

ticker.on("ticks", async (ticks) => {
    // console.log("Ticks: ", ticks.length); 

    for (const tick of ticks) {
        // 1. Store latest price in Redis (Hot Cache for Frontend) - Expires in 30 mins
        // Key: price:123456
        await redis.setex(
            `price:${tick.instrument_token}`,
            1800,
            JSON.stringify({
                price: tick.last_price,
                timestamp: Date.now(),
                change: tick.change, // Day's change percent
                last_quantity: tick.last_quantity
            })
        );

        // 2. Alert Processing: Trigger Vercel Webhook directly (Serverless style)
        // or Push to Queue if high throughput.
        // For 4-5 users, direct Webhook is fine (and faster).
        // To allow async processing, we can fire-and-forget the fetch.

        if (VERCEL_WEBHOOK_URL) {
            fetch(VERCEL_WEBHOOK_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(tick)
            }).catch(err => console.error("Webhook Error:", err.message));
        }

        // 3. (Optional) For robustness, push to a List for backup processing
        // await redis.lpush("alert_queue", JSON.stringify(tick)); 
    }
});

ticker.on("reconnecting", (reconnect_interval, reconnect_attempt) => {
    console.log("Reconnecting: attempt - ", reconnect_attempt, " interval - ", reconnect_interval);
});

ticker.on("close", () => {
    console.log("Connection Closed");
});

ticker.on("error", (e) => {
    console.log("Ticker Error:", e.message);
});

// Helper to subscribe to tokens from Redis
async function subscribeToTokens() {
    try {
        // Get list of tokens to watch from Redis Set
        const tokens = await redis.smembers("watched_tokens");
        if (tokens.length > 0) {
            const tokenNumbers = tokens.map(Number);
            ticker.subscribe(tokenNumbers);
            ticker.setMode(ticker.modeFull, tokenNumbers);
            console.log(`Subscribed to ${tokens.length} tokens`);
        } else {
            console.log("No tokens to subscribe to.");
        }
    } catch (err) {
        console.error("Subscription Error:", err);
    }
}

// Subscribe to new tokens dynamically? 
// We can check every minute or use Redis PubSub for command channel.
// Simpler: Poll Redis 'watched_tokens' every minute to see if we missed any.
setInterval(subscribeToTokens, 60000); 
