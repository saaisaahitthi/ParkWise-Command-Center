import * as React from "react";
import { cn } from "@/lib/utils";
import { Card } from "./card";

export interface MetricCardProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string;
  value: string;
  delta?: string;
  caption?: string;
  accent?: "primary" | "success" | "warning" | "danger";
}

const accentStyles: Record<NonNullable<MetricCardProps["accent"]>, string> = {
  primary: "text-sky-400",
  success: "text-emerald-400",
  warning: "text-amber-400",
  danger: "text-rose-400",
};

export function MetricCard({ label, value, delta, caption, accent = "primary", className, ...props }: MetricCardProps) {
  return (
    <Card className={cn("space-y-3 rounded-[28px] border border-[var(--color-card-border)] p-5", className)} {...props}>
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-400">{label}</p>
        {delta ? <span className={cn("text-sm font-semibold", accentStyles[accent])}>{delta}</span> : null}
      </div>
      <p className="text-3xl font-semibold text-white">{value}</p>
      {caption ? <p className="text-sm text-slate-500">{caption}</p> : null}
    </Card>
  );
}
