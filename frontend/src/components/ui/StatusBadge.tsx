import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeStyles = cva(
  "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] transition-colors",
  {
    variants: {
      variant: {
        default: "bg-slate-900 text-slate-200",
        success: "bg-emerald-500/15 text-emerald-300 border border-emerald-500/20",
        warning: "bg-amber-500/15 text-amber-300 border border-amber-500/20",
        danger: "bg-red-500/15 text-red-300 border border-red-500/20",
        info: "bg-blue-500/15 text-blue-300 border border-blue-500/20",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface StatusBadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeStyles> {}

export function StatusBadge({ className, variant, ...props }: StatusBadgeProps) {
  return <span className={cn(badgeStyles({ variant }), className)} {...props} />;
}
