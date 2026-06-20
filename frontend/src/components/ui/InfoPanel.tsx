import * as React from "react";
import { cn } from "@/lib/utils";
import { Card } from "./card";

export interface InfoPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  details: string;
  icon?: React.ReactNode;
}

export function InfoPanel({ title, details, icon, className, ...props }: InfoPanelProps) {
  return (
    <Card className={cn("rounded-[28px] border border-[var(--color-card-border)] p-6", className)} {...props}>
      <div className="flex items-start gap-4">
        {icon ? <div className="mt-1 text-sky-400">{icon}</div> : null}
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">{title}</p>
          <p className="mt-3 text-sm leading-6 text-slate-300">{details}</p>
        </div>
      </div>
    </Card>
  );
}
