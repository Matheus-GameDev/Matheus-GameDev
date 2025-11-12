import { Card } from "@/components/ui/card";
import { OperationHistoryItem } from "@/types";
import clsx from "clsx";

interface HistoryTableProps {
  history: OperationHistoryItem[];
}

export function HistoryTable({ history }: HistoryTableProps) {
  return (
    <Card title="Histórico de operações" className="h-full">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-3 py-2">Data</th>
              <th className="px-3 py-2">Par</th>
              <th className="px-3 py-2">Rota</th>
              <th className="px-3 py-2">Valor</th>
              <th className="px-3 py-2">PnL</th>
              <th className="px-3 py-2">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80">
            {history.length === 0 && (
              <tr>
                <td colSpan={6} className="px-3 py-4 text-center text-slate-500">
                  Nenhuma operação registrada ainda.
                </td>
              </tr>
            )}
            {history.map((item) => (
              <tr key={item.id} className="hover:bg-slate-900/60">
                <td className="px-3 py-2 text-xs text-slate-400">
                  {new Date(item.executedAt).toLocaleString()}
                </td>
                <td className="px-3 py-2 font-medium text-slate-200">{item.tokenPair}</td>
                <td className="px-3 py-2 text-slate-300">{item.dexRoute}</td>
                <td className="px-3 py-2 text-slate-300">
                  {item.amount.toFixed(3)} {item.amountSymbol}
                </td>
                <td
                  className={clsx(
                    "px-3 py-2 font-semibold",
                    item.profit >= 0 ? "text-emerald-400" : "text-rose-400"
                  )}
                >
                  {item.profit.toFixed(4)} {item.amountSymbol}
                </td>
                <td className="px-3 py-2 text-slate-300">
                  <span
                    className={clsx(
                      "rounded-full px-3 py-1 text-xs font-semibold",
                      item.status === "success"
                        ? "bg-emerald-500/20 text-emerald-300"
                        : "bg-rose-500/20 text-rose-300"
                    )}
                  >
                    {item.status === "success" ? "Sucesso" : "Falha"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
