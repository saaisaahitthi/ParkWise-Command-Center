import * as React from "react";
import { cn } from "@/lib/utils";

export interface MapContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
}

export function MapContainer({ title, subtitle, className, children, ...props }: MapContainerProps) {
  return (
    <div className={cn("rounded-[32px] border border-[var(--color-card-border)] bg-[var(--color-card-bg)] shadow-[0_20px_60px_-40px_rgba(0,0,0,0.65)]", className)} {...props}>
      <div className="border-b border-[var(--color-card-border)] px-5 py-4">
        {title ? <h3 className="text-lg font-semibold text-white">{title}</h3> : null}
        {subtitle ? <p className="mt-1 text-sm text-slate-400">{subtitle}</p> : null}
      </div>
      <div className="min-h-[360px] p-5">{children}</div>
    </div>
  );
}
