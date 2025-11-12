export interface ActiveOperation {
  id: string;
  tokenPair: string;
  dex: string;
  amount: number;
  amountSymbol: "SOL" | "USDC";
  profit: number;
  status: "running" | "settling";
}

export interface OperationHistoryItem {
  id: string;
  tokenPair: string;
  dexRoute: string;
  amount: number;
  amountSymbol: "SOL" | "USDC";
  profit: number;
  executedAt: string;
  status: "success" | "failed";
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: "info" | "warn" | "error";
  message: string;
}
