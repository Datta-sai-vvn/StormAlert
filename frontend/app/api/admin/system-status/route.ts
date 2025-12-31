import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
    // In Serverless mode, we assume ONLINE if the Ticker Service is running.
    // Ticker Service configuration is static (Env Vars).
    return NextResponse.json({
        status: "ONLINE",
        uptime: new Date().toISOString()
    });
}
