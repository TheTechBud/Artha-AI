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
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <p className="label-xs">Weekly Narrative</p>
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

      <div className="prose prose-sm prose-invert max-w-none">
        {data.narrative_text.split("\n\n").map((para, i) => (
          <p key={i} className="text-sm text-white/80 leading-relaxed mb-3 last:mb-0">
            {para}
          </p>
        ))}
      </div>

      {data.drs_at_generation && (
        <div className="border-t border-border pt-3 flex items-center gap-2 text-xs text-muted">
          <span>DRS at generation:</span>
          <span className="font-mono text-white">{data.drs_at_generation.toFixed(0)}</span>
        </div>
      )}
    </div>
  );
}
