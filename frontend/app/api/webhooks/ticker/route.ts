import { NextRequest, NextResponse } from 'next/server';
import { redis } from '@/lib/redis';
import clientPromise from '@/lib/mongodb';
import { Algorithms, PricePoint, AlertSettings } from '@/lib/algorithms';
import { sendNotification } from '@/lib/notifications';

// Prevent this route from being cached
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
    try {
        const tick = await req.json();

        // validate tick
        if (!tick || !tick.instrument_token || !tick.last_price) {
            return NextResponse.json({ error: "Invalid tick data" }, { status: 400 });
        }

        const token = tick.instrument_token;
        const price = tick.last_price;
        const now = Date.now();

        // 1. Get History (Last 1000 points)
        // Redis List: history:123456
        // We push first, then read. 
        // Actually, TickerService might push history or we do it here?
        // TickerService only sets `price:TOKEN`. It pushes to `alert_queue`.
        // Ideally TickerService should maintain history to be fast?
        // Let's assume WE maintain history here since this is the "Brain".

        await redis.lpush(`history:${token}`, JSON.stringify({ price, timestamp: now }));
        await redis.ltrim(`history:${token}`, 0, 999); // Keep last 1000

        const historyRaw = await redis.lrange(`history:${token}`, 0, 999);
        const history: PricePoint[] = historyRaw.map(s => JSON.parse(s));

        // 2. Get Watchers
        const watchers = await redis.smembers(`watchers:${token}`);

        // 3. Evaluate for each watcher
        const mongo = await clientPromise;
        const db = mongo.db(); // uses default DB from URI

        for (const userId of watchers) {
            // Get Settings (Cached in Redis or DB)
            // For MVP: Default settings or fetch from DB
            // const userSettings = await db.collection('settings').findOne({ user_id: userId });

            const settings: AlertSettings = {
                trailing: { enabled: true, threshold: 1.0 }, // 1% default
                rollingWindow: { enabled: true, threshold: 2.0, period: 5 } // 2% in 5 min
            };

            // Evaluate
            const trailingAlert = Algorithms.evaluateTrailing(price, history, settings.trailing.threshold);
            const rollingAlert = Algorithms.evaluateRolling(price, history, settings.rollingWindow.period, settings.rollingWindow.threshold);

            const alerts = [trailingAlert, rollingAlert].filter(a => a !== null);

            for (const alert of alerts) {
                if (!alert) continue;

                // Deduplication: Check if we recently alerted this user for this token/type
                const cooldownKey = `cooldown:${userId}:${token}:${alert.type}`;
                const inCooldown = await redis.get(cooldownKey);

                if (!inCooldown) {
                    // Send & Save
                    await db.collection('alerts').insertOne({ ...alert, user_id: userId, created_at: new Date() });
                    await sendNotification(alert, userId);

                    // Set Cooldown (e.g., 5 minutes)
                    await redis.setex(cooldownKey, 300, '1');
                }
            }
        }

        return NextResponse.json({ success: true });
    } catch (e: any) {
        console.error("Webhook Error", e);
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
