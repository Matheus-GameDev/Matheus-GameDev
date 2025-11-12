import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { WalletProviders } from "@/components/providers/wallet-providers";

export const metadata: Metadata = {
  title: "Solana Arbitrage Bot Control",
  description: "Painel de controle do bot de arbitragem com integração Phantom Wallet",
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className="bg-slate-950 text-slate-100 min-h-screen">
        <WalletProviders>{children}</WalletProviders>
      </body>
    </html>
  );
}
