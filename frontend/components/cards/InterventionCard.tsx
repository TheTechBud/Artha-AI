"use client";

import { useDismissIntervention } from "@/hooks/useInterventions";
import { urgencyBg, formatINR, relativeTime } from "@/lib/utils";
import type { Intervention } from "@/types";

interface InterventionCardProps {
  item: Intervention;
}

export function InterventionCard({ item }: InterventionCardProps) {
  const dismiss = useDismissIntervention();

  return (
    <div className="card space-y-3 animate-fade-in">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`badge ${urgencyBg(item.urgency)}`}>
            {item.urgency.toUpperCase()}
          </span>
          {item.savings_potential > 0 && (
            <span className="badge bg-teal-500/10 text-teal-400 border border-teal-500/20">
              Save {formatINR(item.savings_potential)}/mo
            </span>
          )}
        </div>
        <span className="text-xs text-muted shrink-0">{relativeTime(item.generated_at)}</span>
      </div>

      <h3 className="text-sm font-semibold text-white leading-snug">{item.title}</h3>

      <div className="space-y-2">
        <div className="bg-white/3 rounded-lg px-3 py-2.5 border border-border">
          <p className="text-xs text-muted mb-0.5 font-medium uppercase tracking-wide">Action</p>
          <p className="text-sm text-white/90 leading-relaxed">{item.action}</p>
        </div>
        <div className="bg-white/3 rounded-lg px-3 py-2.5 border border-border">
          <p className="text-xs text-muted mb-0.5 font-medium uppercase tracking-wide">Why</p>
          <p className="text-sm text-white/70 leading-relaxed">{item.reason}</p>
        </div>
      </div>

      <div className="flex gap-2 pt-1">
        <button
          onClick={() => dismiss.mutate(item.id)}
          disabled={dismiss.isPending}
          className="text-xs text-muted hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-white/5"
        >
          {dismiss.isPending ? "Dismissing…" : "Dismiss"}
        </button>
      </div>
    </div>
  );
}
