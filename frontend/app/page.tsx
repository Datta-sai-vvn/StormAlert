import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-slate-900 to-slate-800 text-white">
      <main className="flex flex-col items-center justify-center px-4 text-center">
        <h1 className="text-6xl font-bold tracking-tighter sm:text-7xl">
          <span className="text-blue-500">Storm</span>Alert
        </h1>
        <p className="mt-4 max-w-[600px] text-lg text-slate-300 md:text-xl">
          Real-time stock price alerts delivered straight to your preferred channels.
          Never miss a market movement again.
        </p>
        
        <div className="mt-8 flex flex-col gap-4 sm:flex-row">
          <Link
            href="/dashboard"
            className="rounded-lg bg-blue-600 px-8 py-3 text-lg font-semibold text-white transition-colors hover:bg-blue-700"
          >
            Go to Dashboard
          </Link>
          <Link
            href="/login"
            className="rounded-lg border border-slate-600 bg-slate-800 px-8 py-3 text-lg font-semibold text-white transition-colors hover:bg-slate-700"
          >
            Login
          </Link>
        </div>

        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-3">
          <div className="rounded-xl bg-slate-800/50 p-6 backdrop-blur-sm">
            <h3 className="mb-2 text-xl font-bold text-blue-400">Real-time Tracking</h3>
            <p className="text-slate-400">Monitor up to 500 stocks with live updates from Zerodha Kite.</p>
          </div>
          <div className="rounded-xl bg-slate-800/50 p-6 backdrop-blur-sm">
            <h3 className="mb-2 text-xl font-bold text-green-400">Smart Alerts</h3>
            <p className="text-slate-400">Set trailing stop-loss and rolling timeframe percentage alerts.</p>
          </div>
          <div className="rounded-xl bg-slate-800/50 p-6 backdrop-blur-sm">
            <h3 className="mb-2 text-xl font-bold text-purple-400">Multi-channel</h3>
            <p className="text-slate-400">Get notified instantly via WhatsApp, Telegram, and Email.</p>
          </div>
        </div>
      </main>
    </div>
  );
}
