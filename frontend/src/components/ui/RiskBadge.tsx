import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const riskStyles = cva(
  "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] transition-colors",
  {
    variants: {
      variant: {
        critical: "bg-red-500/15 text-red-300 border border-red-500/20",
        high: "bg-amber-500/15 text-amber-300 border border-amber-500/20",
        medium: "bg-sky-500/15 text-sky-300 border border-sky-500/20",
        low: "bg-emerald-500/15 text-emerald-300 border border-emerald-500/20",
      },
    },
    defaultVariants: {
      variant: "medium",
    },
  }
);

export interface RiskBadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof riskStyles> {}

export function RiskBadge({ className, variant, ...props }: RiskBadgeProps) {
  return <span className={cn(riskStyles({ variant }), className)} {...props} />;
}
