"use client";

import { useMemo } from "react";
import { ActiveOperation, LogEntry, OperationHistoryItem } from "@/types";
import { WalletButton } from "@/components/ui/wallet-button";
import { BotController } from "@/components/dashboard/bot-controller";
import { ActiveOperations } from "@/components/dashboard/active-operations";
import { LogPanel } from "@/components/dashboard/log-panel";
import { HistoryTable } from "@/components/dashboard/history-table";
import { useRealtimeLogs } from "@/lib/use-realtime-logs";

interface DashboardScreenProps {
  activeOperations: ActiveOperation[];
  history: OperationHistoryItem[];
  initialLogs: LogEntry[];
}

export function DashboardScreen({ activeOperations, history, initialLogs }: DashboardScreenProps) {
  const logs = useRealtimeLogs({
    wsUrl: process.env.NEXT_PUBLIC_LOG_STREAM_URL,
    initialLogs,
  });

  const pnlSummary = useMemo(() => {
    const total = activeOperations.reduce((acc, item) => acc + item.profit, 0);
    const positives = activeOperations.filter((item) => item.profit >= 0).length;
    return { total, positives };
  }, [activeOperations]);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-8 px-6 py-10">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-100">Painel do Bot de Arbitragem</h1>
          <p className="text-sm text-slate-400">
            Conecte sua Phantom Wallet e controle o estado do bot em tempo real.
          </p>
        </div>
        <WalletButton />
      </header>

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          <BotController
            defaultAmount={activeOperations[0]?.amount ?? 0.5}
            defaultCurrency={activeOperations[0]?.amountSymbol ?? "SOL"}
            onStart={(amount, currency) => {
              console.info("Bot start requested", { amount, currency });
            }}
            onStop={() => {
              console.info("Bot stop requested");
            }}
          />

          <div className="grid gap-6 md:grid-cols-2">
            <ActiveOperations operations={activeOperations} />
            <div className="rounded-2xl bg-slate-900/60 p-6 shadow-lg ring-1 ring-slate-800">
              <h2 className="text-lg font-semibold text-slate-100">Resumo</h2>
              <dl className="mt-4 grid gap-4 text-sm text-slate-300 sm:grid-cols-2">
                <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-4">
                  <dt className="text-xs uppercase tracking-wide text-slate-500">PnL agregado</dt>
                  <dd className={pnlSummary.total >= 0 ? "mt-2 text-emerald-400" : "mt-2 text-rose-400"}>
                    {pnlSummary.total.toFixed(4)} {activeOperations[0]?.amountSymbol ?? "SOL"}
                  </dd>
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-4">
                  <dt className="text-xs uppercase tracking-wide text-slate-500">Operações positivas</dt>
                  <dd className="mt-2 text-slate-200">{pnlSummary.positives}</dd>
                </div>
              </dl>
            </div>
          </div>

          <HistoryTable history={history} />
        </div>

        <LogPanel logs={logs} />
      </section>
    </main>
  );
}
