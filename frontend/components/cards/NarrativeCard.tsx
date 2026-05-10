"use client";

import { useNarrative, useGenerateNarrative } from "@/hooks/useInterventions";
import { formatDate } from "@/lib/utils";
import { Skeleton } from "@/components/ui/SkeletonLoader";

export function NarrativeCard() {
  const { data, isLoading } = useNarrative();
  const generate = useGenerateNarrative();

  if (isLoading) {
    return (
      <div className="card space-y-3">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-5/6" />
        <Skeleton className="h-3 w-4/6" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="card text-center py-8 space-y-3">
        <p className="text-muted text-sm">No narrative generated yet.</p>
        <button
          onClick={() => generate.mutate()}
          disabled={generate.isPending}
          className="px-4 py-2 bg-teal-500/10 text-teal-400 border border-teal-500/20 rounded-lg text-sm hover:bg-teal-500/20 transition-colors"
        >
          {generate.isPending ? "Generating…" : "Generate Weekly Narrative"}
        </button>
      </div>
    );
  }

  return (
    <div className="card space-y-4 border border-white/[0.06]">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <p className="label-xs">Weekly Narrative</p>
          <p className="text-[11px] text-muted mt-0.5">Your money story — patterns first, judgment never.</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted">{formatDate(data.generated_at)}</span>
          <button
            onClick={() => generate.mutate()}
            disabled={generate.isPending}
            className="text-xs text-teal-400 hover:text-teal-300 transition-colors"
          >
            {generate.isPending ? "Refreshing…" : "↺ Refresh"}
          </button>
        </div>
      </div>

      <blockquote className="border-l-2 border-teal-500/40 pl-4 py-1 space-y-3">
        {data.narrative_text.split("\n\n").map((para, i) => (
          <p key={i} className="text-sm text-white/82 leading-relaxed">
            {para}
          </p>
        ))}
      </blockquote>

      {data.drs_at_generation && (
        <div className="border-t border-border pt-3 flex items-center gap-2 text-xs text-muted">
          <span>Headspace snapshot — DRS when written:</span>
          <span className="font-mono text-white">{data.drs_at_generation.toFixed(0)}</span>
        </div>
      )}
    </div>
  );
}
