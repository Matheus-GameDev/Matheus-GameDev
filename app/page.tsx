import { DashboardScreen } from "@/components/dashboard/dashboard-screen";
import { ActiveOperation, LogEntry, OperationHistoryItem } from "@/types";

const mockActiveOperations: ActiveOperation[] = [
  {
    id: "op-1",
    tokenPair: "SOL/USDC",
    dex: "Orca → Raydium",
    amount: 1.2,
    amountSymbol: "SOL",
    profit: 0.0123,
    status: "running",
  },
  {
    id: "op-2",
    tokenPair: "BONK/USDC",
    dex: "Jupiter",
    amount: 35000,
    amountSymbol: "USDC",
    profit: -2.4,
    status: "settling",
  },
];

const mockHistory: OperationHistoryItem[] = [
  {
    id: "hist-1",
    tokenPair: "SOL/USDC",
    dexRoute: "Orca → Raydium",
    amount: 0.8,
    amountSymbol: "SOL",
    profit: 0.0098,
    executedAt: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
    status: "success",
  },
  {
    id: "hist-2",
    tokenPair: "MSOL/SOL",
    dexRoute: "Jupiter",
    amount: 5,
    amountSymbol: "SOL",
    profit: -0.001,
    executedAt: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    status: "failed",
  },
  {
    id: "hist-3",
    tokenPair: "USDC/USDT",
    dexRoute: "Meteora",
    amount: 1200,
    amountSymbol: "USDC",
    profit: 3.45,
    executedAt: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
    status: "success",
  },
];

const mockLogs: LogEntry[] = [
  {
    id: "log-1",
    timestamp: new Date().toISOString(),
    level: "info",
    message: "Monitorando pares SOL/USDC e BONK/USDC",
  },
  {
    id: "log-2",
    timestamp: new Date(Date.now() - 1000 * 30).toISOString(),
    level: "info",
    message: "Spread identificado em Orca → Raydium",
  },
];

export default function Page() {
  return (
    <DashboardScreen
      activeOperations={mockActiveOperations}
      history={mockHistory}
      initialLogs={mockLogs}
    />
  );
}
