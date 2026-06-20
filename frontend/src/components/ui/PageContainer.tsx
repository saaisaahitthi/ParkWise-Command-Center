import * as React from "react";
import { cn } from "@/lib/utils";

export interface PageContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  heading?: string;
  description?: string;
}

export function PageContainer({ heading, description, className, children, ...props }: PageContainerProps) {
  return (
    <div className={cn("space-y-8 px-4 py-6 sm:px-6 lg:px-8", className)} {...props}>
      {heading || description ? (
        <div className="space-y-2">
          {heading ? <h1 className="text-3xl font-semibold text-white">{heading}</h1> : null}
          {description ? <p className="max-w-3xl text-sm text-slate-400">{description}</p> : null}
        </div>
      ) : null}
      {children}
    </div>
  );
}
