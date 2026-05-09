"use client";

import { PageWrapper } from "@/components/layout/PageWrapper";
import { NarrativeCard } from "@/components/cards/NarrativeCard";
import { useArchetype } from "@/hooks/useInterventions";
import { CardSkeleton } from "@/components/ui/SkeletonLoader";

const ARCHETYPE_META: Record<string, { emoji: string; desc: string }> = {
  stress_spender:  { emoji: "😤", desc: "Tends to spend more during emotional stress or fatigue. Evenings and weekends are high-risk windows." },
  impulse_buyer:   { emoji: "🛒", desc: "High variance spending with frequent unplanned purchases. Lacks a cooling-off buffer before buying." },
  planner:         { emoji: "📋", desc: "Consistent and deliberate spending. Tracks categories and rarely exceeds monthly limits." },
  social_spender:  { emoji: "🎉", desc: "Spending is correlated with social activities. Food and Entertainment dominate the budget." },
  anxiety_saver:   { emoji: "🏦", desc: "Under-spends and hoards cash even when savings goals are met. May miss enjoyment opportunities." },
  status_seeker:   { emoji: "✨", desc: "High spend on aspirational categories — fashion, tech, and premium services signal status anxiety." },
};

export default function NarrativePage() {
  const { data: archetype, isLoading: archetypeLoading } = useArchetype();

  const meta = archetype ? ARCHETYPE_META[archetype.archetype] : null;

  return (
    <PageWrapper
      title="AI Narrative"
      subtitle="Your weekly behavioral finance story"
    >
      <div className="grid grid-cols-3 gap-4">
        {/* Narrative */}
        <div className="col-span-2">
          <NarrativeCard />
        </div>

        {/* Archetype panel */}
        <div className="col-span-1 space-y-4">
          <div className="card">
            <p className="label-xs mb-3">Behavioral Archetype</p>
            {archetypeLoading ? (
              <CardSkeleton />
            ) : archetype ? (
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{meta?.emoji ?? "◎"}</span>
                  <div>
                    <p className="text-sm font-semibold text-white capitalize">
                      {archetype.archetype.replace(/_/g, " ")}
                    </p>
                    <p className="text-xs text-muted">
                      {(archetype.confidence * 100).toFixed(0)}% confidence
                    </p>
                  </div>
                </div>
                {meta && (
                  <p className="text-xs text-white/60 leading-relaxed">{meta.desc}</p>
                )}
                <div className="border-t border-border pt-3 space-y-1.5">
                  <p className="label-xs">Key Signals</p>
                  {archetype.key_signals.map((sig, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-muted">
                      <span className="text-teal-500 mt-0.5 shrink-0">→</span>
                      {sig}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-6 text-muted text-sm space-y-2">
                <p>Archetype not yet classified</p>
                <p className="text-xs">Upload transactions to get classified</p>
              </div>
            )}
          </div>

          {/* Archetype legend */}
          <div className="card">
            <p className="label-xs mb-3">All Archetypes</p>
            <div className="space-y-2">
              {Object.entries(ARCHETYPE_META).map(([key, val]) => (
                <div
                  key={key}
                  className={`flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs transition-colors ${
                    archetype?.archetype === key
                      ? "bg-teal-500/10 text-teal-300"
                      : "text-muted hover:text-white"
                  }`}
                >
                  <span>{val.emoji}</span>
                  <span className="capitalize">{key.replace(/_/g, " ")}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </PageWrapper>
  );
}
