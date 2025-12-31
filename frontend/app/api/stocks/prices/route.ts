import { NextRequest, NextResponse } from 'next/server';
import { redis } from '@/lib/redis';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
    try {
        // 1. Get List of Watched Tokens
        const tokens = await redis.smembers("watched_tokens");

        if (tokens.length === 0) {
            return NextResponse.json({});
        }

        // 2. Fetch Prices in Bulk (MGET)
        // Keys are "price:TOKEN"
        const keys = tokens.map(t => `price:${t}`);
        const values = await redis.mget(...keys);

        // 3. Map to Object
        const result: Record<string, any> = {};

        tokens.forEach((token, index) => {
            const val = values[index];
            if (val) {
                result[token] = JSON.parse(val);
            }
        });

        return NextResponse.json(result);
    } catch (e: any) {
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
