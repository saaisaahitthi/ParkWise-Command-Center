import * as React from "react";
import { cn } from "@/lib/utils";

export interface SectionHeaderProps {
  title: string;
  description?: string;
  badge?: string;
  action?: React.ReactNode;
  className?: string;
}

export function SectionHeader({ title, description, badge, action, className }: SectionHeaderProps) {
  return (
    <div className={cn("flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between", className)}>
      <div className="space-y-2">
        <div className="flex flex-wrap items-center gap-3">
          {badge ? <span className="rounded-full bg-slate-900 px-3 py-1 text-xs uppercase tracking-[0.32em] text-slate-400">{badge}</span> : null}
          <h2 className="text-2xl font-semibold text-white">{title}</h2>
        </div>
        {description ? <p className="max-w-2xl text-sm text-slate-400">{description}</p> : null}
      </div>
      {action ? <div>{action}</div> : null}
    </div>
  );
}
