import { NextRequest, NextResponse } from 'next/server';
import clientPromise from '@/lib/mongodb';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
    try {
        const client = await clientPromise;
        const db = client.db();

        // Parse Query Params (Limit, etc)
        const { searchParams } = new URL(req.url);
        const limit = parseInt(searchParams.get('limit') || '20');

        const alerts = await db.collection("alerts")
            .find({})
            .sort({ created_at: -1 }) // Newest first
            .limit(limit)
            .toArray();

        return NextResponse.json(alerts);
    } catch (e: any) {
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
