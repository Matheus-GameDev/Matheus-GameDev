// src/types/index.ts

interface ArbitrageOpportunity {
    sourceMarket: string;
    targetMarket: string;
    profit: number; // Potential profit in base currency
    currencyPair: string; // e.g., "SOL/USDC"
    timestamp: Date; // When the opportunity was found
}

interface Order {
    id: string;
    market: string;
    price: number;
    quantity: number;
    side: 'buy' | 'sell'; // Order side
    status: 'pending' | 'completed' | 'canceled'; // Order status
}

interface ArbitrageBotSettings {
    maxSlippage: number;
    minProfitThreshold: number;
    tradingPairs: string[]; // array of strings like ["SOL/USDC", "USDC/SOL"]
    enabled: boolean; // Flag to enable/disable the bot
}

interface Trade {
    orderId: string;
    market: string;
    executedPrice: number;
    quantity: number;
    tradeTime: Date; // When the trade was executed
}

interface Market {
    name: string; // e.g., "Binance"
    baseCurrency: string; // e.g., "SOL"
    quoteCurrency: string; // e.g., "USDC"
    price: number; // Current price of the asset
    volume: number; // 24h volume
}

export type {
    ArbitrageOpportunity,
    Order,
    ArbitrageBotSettings,
    Trade,
    Market
};