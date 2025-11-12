"use client";

import { useState } from "react";
import { useWallet } from "@solana/wallet-adapter-react";
import { Card } from "@/components/ui/card";
import clsx from "clsx";

interface BotControllerProps {
  defaultAmount?: number;
  defaultCurrency?: "SOL" | "USDC";
  onStart?: (amount: number, currency: "SOL" | "USDC") => void;
  onStop?: () => void;
}

export function BotController({
  defaultAmount = 0.5,
  defaultCurrency = "SOL",
  onStart,
  onStop,
}: BotControllerProps) {
  const { publicKey, connected } = useWallet();
  const [amount, setAmount] = useState<number>(defaultAmount);
  const [currency, setCurrency] = useState<"SOL" | "USDC">(defaultCurrency);
  const [isActive, setIsActive] = useState(false);

  const handleStart = () => {
    if (!connected) return;
    setIsActive(true);
    onStart?.(amount, currency);
  };

  const handleStop = () => {
    setIsActive(false);
    onStop?.();
  };

  return (
    <Card
      title="Controle do Bot"
      headerAction={
        <span
          className={clsx(
            "flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold",
            isActive ? "bg-emerald-500/20 text-emerald-300" : "bg-slate-800 text-slate-300"
          )}
        >
          <span className={clsx("h-2 w-2 rounded-full", isActive ? "bg-emerald-400" : "bg-slate-500")} />
          {isActive ? "Bot ativo" : "Bot inativo"}
        </span>
      }
    >
      <div className="space-y-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Carteira conectada</p>
          <p className="font-mono text-sm text-slate-200">
            {connected && publicKey ? publicKey.toBase58() : "Nenhuma carteira conectada"}
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="space-y-2">
            <span className="block text-xs uppercase tracking-wide text-slate-400">Valor por operação</span>
            <input
              type="number"
              min={0}
              step="0.01"
              value={amount}
              onChange={(event) => {
                const value = Number(event.target.value);
                setAmount(Number.isNaN(value) ? 0 : value);
              }}
              className="w-full rounded-xl border border-slate-800 bg-slate-950/60 px-4 py-2 text-sm text-slate-100 shadow-inner outline-none transition focus:border-primary"
            />
          </label>
          <label className="space-y-2">
            <span className="block text-xs uppercase tracking-wide text-slate-400">Moeda</span>
            <select
              value={currency}
              onChange={(event) => setCurrency(event.target.value as "SOL" | "USDC")}
              className="w-full rounded-xl border border-slate-800 bg-slate-950/60 px-4 py-2 text-sm text-slate-100 shadow-inner outline-none transition focus:border-primary"
            >
              <option value="SOL">SOL</option>
              <option value="USDC">USDC</option>
            </select>
          </label>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <button
            onClick={handleStart}
            disabled={!connected || isActive}
            className="flex-1 rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground shadow-lg transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:bg-slate-800 disabled:text-slate-500"
          >
            Ligar Bot
          </button>
          <button
            onClick={handleStop}
            disabled={!isActive}
            className="flex-1 rounded-xl border border-rose-500/40 bg-slate-900 px-4 py-3 text-sm font-semibold text-rose-300 shadow-lg transition hover:border-rose-400 hover:text-rose-200 disabled:cursor-not-allowed disabled:border-slate-800 disabled:text-slate-500"
          >
            Desligar Bot
          </button>
        </div>
      </div>
    </Card>
  );
}
