export interface PricePoint {
    price: number;
    timestamp: number;
}

export interface AlertSettings {
    trailing: {
        enabled: boolean;
        threshold: number;
    };
    rollingWindow: {
        enabled: boolean;
        threshold: number;
        period: number; // minutes
    };
}

export interface Alert {
    type: 'DIP' | 'SPIKE';
    token: number;
    percent: number;
    price: number;
    timestamp: number;
}

export class Algorithms {
    static evaluateTrailing(currentPrice: number, history: PricePoint[], threshold: number): Alert | null {
        if (!history || history.length === 0) return null;

        const maxPrice = Math.max(...history.map(p => p.price));
        // Check for Dip from High (Trailing Stop Loss logic)
        const dropUnsigned = ((maxPrice - currentPrice) / maxPrice) * 100;

        if (dropUnsigned >= threshold) {
            return {
                type: 'DIP',
                token: 0, // Set by caller
                percent: dropUnsigned,
                price: currentPrice,
                timestamp: Date.now()
            };
        }
        return null;
    }

    static evaluateRolling(currentPrice: number, history: PricePoint[], periodMinutes: number, threshold: number): Alert | null {
        if (!history || history.length === 0) return null;

        const now = Date.now();
        const cutoff = now - (periodMinutes * 60 * 1000);

        // Filter history for the window
        const windowData = history.filter(p => p.timestamp >= cutoff);
        if (windowData.length === 0) return null;

        const minPrice = Math.min(...windowData.map(p => p.price));

        // Check for Spike from Low
        const gain = ((currentPrice - minPrice) / minPrice) * 100;

        if (gain >= threshold) {
            return {
                type: 'SPIKE',
                token: 0, // Set by caller
                percent: gain,
                price: currentPrice,
                timestamp: now
            };
        }
        return null;
    }
}
