import { ActiveOperation } from "@/types";
import { Card } from "@/components/ui/card";
import clsx from "clsx";

interface ActiveOperationsProps {
  operations: ActiveOperation[];
}

const statusColor: Record<ActiveOperation["status"], string> = {
  running: "bg-emerald-500/20 text-emerald-300",
  settling: "bg-amber-500/20 text-amber-300",
};

export function ActiveOperations({ operations }: ActiveOperationsProps) {
  return (
    <Card title="Operações em andamento" className="h-full">
      <div className="flex items-center justify-between text-xs uppercase tracking-wide text-slate-400">
        <span>Total</span>
        <span className="text-sm font-semibold text-slate-100">{operations.length}</span>
      </div>
      <div className="mt-4 space-y-3">
        {operations.length === 0 && (
          <p className="text-sm text-slate-500">Nenhuma operação ativa no momento.</p>
        )}
        {operations.map((operation) => (
          <div
            key={operation.id}
            className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 shadow-inner"
          >
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-slate-100">{operation.tokenPair}</p>
                <p className="text-xs text-slate-400">{operation.dex}</p>
              </div>
              <span
                className={clsx(
                  "rounded-full px-3 py-1 text-xs font-semibold",
                  statusColor[operation.status]
                )}
              >
                {operation.status === "running" ? "Executando" : "Liquidação"}
              </span>
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-6 text-xs text-slate-400">
              <span>
                Valor: <strong className="text-slate-200">{operation.amount} {operation.amountSymbol}</strong>
              </span>
              <span>
                PnL: <strong className={operation.profit >= 0 ? "text-emerald-400" : "text-rose-400"}>
                  {operation.profit.toFixed(4)} {operation.amountSymbol}
                </strong>
              </span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
