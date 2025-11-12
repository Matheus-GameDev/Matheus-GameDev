"use client";

import { useWalletModal } from "@solana/wallet-adapter-react-ui";
import { useWallet } from "@solana/wallet-adapter-react";
import { useCallback } from "react";
import { shortenAddress } from "@/lib/shorten-address";
import clsx from "clsx";

export function WalletButton() {
  const { setVisible } = useWalletModal();
  const { connected, publicKey, disconnect } = useWallet();

  const handleClick = useCallback(() => {
    if (connected) {
      void disconnect();
      return;
    }

    setVisible(true);
  }, [connected, disconnect, setVisible]);

  return (
    <button
      onClick={handleClick}
      className={clsx(
        "rounded-full px-4 py-2 text-sm font-medium transition-colors",
        connected
          ? "bg-slate-800 hover:bg-slate-700"
          : "bg-primary text-primary-foreground hover:bg-violet-500"
      )}
    >
      {connected && publicKey
        ? `Desconectar ${shortenAddress(publicKey.toBase58())}`
        : "Conectar Phantom"}
    </button>
  );
}
