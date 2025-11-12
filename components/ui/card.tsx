import clsx from "clsx";
import { PropsWithChildren } from "react";

interface CardProps extends PropsWithChildren {
  title?: string;
  className?: string;
  headerAction?: React.ReactNode;
}

export function Card({ title, className, headerAction, children }: CardProps) {
  return (
    <section className={clsx("rounded-2xl bg-slate-900/60 p-6 shadow-lg ring-1 ring-slate-800", className)}>
      {(title || headerAction) && (
        <header className="mb-4 flex items-center justify-between gap-4">
          {title && <h2 className="text-lg font-semibold text-slate-100">{title}</h2>}
          {headerAction}
        </header>
      )}
      <div className="space-y-4 text-sm text-slate-300">{children}</div>
    </section>
  );
}
