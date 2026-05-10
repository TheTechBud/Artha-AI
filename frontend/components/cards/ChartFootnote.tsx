"use client";

import type { ReactNode } from "react";

export function ChartFootnote({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="mt-3 pt-3 border-t border-border/70">
      <p className="text-[10px] uppercase tracking-wide text-muted mb-1.5">{title}</p>
      <div className="text-xs text-white/65 leading-relaxed">{children}</div>
    </div>
  );
}
