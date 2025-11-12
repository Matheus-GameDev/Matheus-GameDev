"use client";

import { useEffect, useState } from "react";
import { LogEntry } from "@/types";

interface UseRealtimeLogsOptions {
  wsUrl?: string;
  initialLogs?: LogEntry[];
  mockIntervalMs?: number;
}

function createMockLog(): LogEntry {
  const id = typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : Math.random().toString(36);
  return {
    id,
    timestamp: new Date().toISOString(),
    level: Math.random() > 0.85 ? "warn" : "info",
    message: "Mensagem simulada de log do bot",
  };
}

export function useRealtimeLogs({ wsUrl, initialLogs = [], mockIntervalMs = 5000 }: UseRealtimeLogsOptions) {
  const [logs, setLogs] = useState<LogEntry[]>(initialLogs);

  useEffect(() => {
    if (typeof window === "undefined") return;

    if (wsUrl) {
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data) as LogEntry | LogEntry[];
          setLogs((prev) => [
            ...prev,
            ...(Array.isArray(payload) ? payload : [payload]),
          ]);
        } catch (error) {
          console.error("Falha ao interpretar mensagem do websocket", error);
        }
      };

      ws.onerror = (error) => {
        console.warn("Erro no websocket", error);
      };

      return () => {
        ws.close();
      };
    }

    const intervalId = window.setInterval(() => {
      setLogs((prev) => [...prev, createMockLog()]);
    }, mockIntervalMs);

    return () => window.clearInterval(intervalId);
  }, [mockIntervalMs, wsUrl]);

  return logs;
}
