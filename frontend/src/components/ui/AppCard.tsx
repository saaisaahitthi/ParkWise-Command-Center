import * as React from "react";
import { cn } from "@/lib/utils";
import { Card } from "./card";

export interface AppCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  footer?: React.ReactNode;
}

export function AppCard({
  title,
  subtitle,
  actions,
  footer,
  className,
  children,
  ...props
}: AppCardProps) {
  return (
    <Card className={cn("overflow-hidden", className)} {...props}>
      <div className="flex flex-col gap-6 p-6">
        {(title || subtitle || actions) && (
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div className="space-y-2">
              {title ? <h3 className="text-xl font-semibold text-white">{title}</h3> : null}
              {subtitle ? <p className="text-sm text-slate-400">{subtitle}</p> : null}
            </div>
            {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
          </div>
        )}

        <div className="space-y-4">{children}</div>

        {footer ? <div className="border-t border-[var(--color-card-border)] pt-4">{footer}</div> : null}
      </div>
    </Card>
  );
}
