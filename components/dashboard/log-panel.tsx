import { useMemo } from "react";
import { LogEntry } from "@/types";
import { Card } from "@/components/ui/card";
import clsx from "clsx";

interface LogPanelProps {
  logs: LogEntry[];
}

const badgeColor: Record<LogEntry["level"], string> = {
  info: "bg-slate-800 text-slate-200",
  warn: "bg-amber-500/20 text-amber-300",
  error: "bg-rose-500/20 text-rose-300",
};

export function LogPanel({ logs }: LogPanelProps) {
  const sortedLogs = useMemo(() => [...logs].sort((a, b) => b.timestamp.localeCompare(a.timestamp)), [logs]);

  return (
    <Card title="Logs em tempo real" className="h-full">
      <div className="flex flex-col gap-3 overflow-y-auto pr-2" style={{ maxHeight: "28rem" }}>
        {sortedLogs.length === 0 && <p className="text-sm text-slate-500">Nenhum log recebido até o momento.</p>}
        {sortedLogs.map((log) => (
          <article key={log.id} className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-3">
            <header className="flex items-center justify-between text-xs text-slate-500">
              <time className="font-mono text-[11px]">{new Date(log.timestamp).toLocaleTimeString()}</time>
              <span className={clsx("rounded-full px-2 py-0.5 text-[11px] font-semibold", badgeColor[log.level])}>
                {log.level.toUpperCase()}
              </span>
            </header>
            <p className="mt-2 text-sm text-slate-200">{log.message}</p>
          </article>
        ))}
      </div>
    </Card>
  );
}
