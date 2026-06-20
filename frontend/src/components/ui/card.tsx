import * as React from "react";
import { cn } from "@/lib/utils";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Card({ className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-[28px] border border-[var(--color-card-border)] bg-[var(--color-card-bg)] shadow-[0_20px_60px_-40px_rgba(0,0,0,0.65)] backdrop-blur-xl",
        className
      )}
      {...props}
    />
  );
}
