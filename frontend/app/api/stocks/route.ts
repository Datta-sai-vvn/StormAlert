import { NextRequest, NextResponse } from 'next/server';
import { redis } from '@/lib/redis';

// GET: List all watched stocks
export async function GET(request: NextRequest) {
    try {
        // 1. Get tokens from Redis Set
        const tokens = await redis.smembers("watched_tokens");

        // 2. Mock symbol mapping for now (since we store only tokens in Redis)
        // ideally we should store a hash "token_symbols" mapping token -> symbol
        const stocks = tokens.map(token => ({
            symbol: `TOKEN:${token}`, // Placeholder symbol
            instrument_token: parseInt(token),
            name: "Stock"
        }));

        return NextResponse.json(stocks);
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}

// POST: Add a stock to watch
export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { instrument_token } = body;

        if (!instrument_token) {
            return NextResponse.json({ error: "Missing instrument_token" }, { status: 400 });
        }

        // Add to Redis Set
        await redis.sadd("watched_tokens", instrument_token);

        return NextResponse.json({ success: true, instrument_token });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}

// DELETE: Remove a stock
export async function DELETE(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url);
        const token = searchParams.get('token');

        if (!token) {
            return NextResponse.json({ error: "Missing token" }, { status: 400 });
        }

        await redis.srem("watched_tokens", token);
        return NextResponse.json({ success: true });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
