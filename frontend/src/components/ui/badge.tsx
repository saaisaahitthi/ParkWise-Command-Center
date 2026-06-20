import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-navy-100 text-navy-800",
        critical: "bg-red-50 text-red-700 border border-red-200",
        high: "bg-amber-50 text-amber-700 border border-amber-200",
        medium: "bg-blue-50 text-blue-700 border border-blue-200",
        low: "bg-green-50 text-green-700 border border-green-200",
        beta: "bg-purple-50 text-purple-700 border border-purple-200",
        outline: "border border-slate-300 text-slate-600",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
