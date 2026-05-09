"use client";

import { PageWrapper } from "@/components/layout/PageWrapper";
import { InterventionCard } from "@/components/cards/InterventionCard";
import { useInterventions, useGenerateIntervention } from "@/hooks/useInterventions";
import { CardSkeleton } from "@/components/ui/SkeletonLoader";

const RISK_TYPES = [
  { value: "velocity_spike",  label: "Velocity Spike" },
  { value: "salary_gap_risk", label: "Salary Gap Risk" },
  { value: "budget_overflow", label: "Budget Overflow" },
  { value: "emotional_spend", label: "Emotional Spend" },
];

export default function InterventionsPage() {
  const { data: items, isLoading } = useInterventions();
  const generate = useGenerateIntervention();

  const GenerateButton = (
    <div className="flex items-center gap-2">
      <select
        id="risk-select"
        className="text-xs bg-panel border border-border text-muted rounded-lg px-2 py-1.5 focus:outline-none focus:border-teal-500/50"
      >
        {RISK_TYPES.map((r) => (
          <option key={r.value} value={r.value}>{r.label}</option>
        ))}
      </select>
      <button
        onClick={() => {
          const sel = document.getElementById("risk-select") as HTMLSelectElement;
          generate.mutate(sel?.value ?? "velocity_spike");
        }}
        disabled={generate.isPending}
        className="px-3 py-1.5 bg-teal-500/10 text-teal-400 border border-teal-500/20 rounded-lg text-sm hover:bg-teal-500/20 transition-colors"
      >
        {generate.isPending ? "Generating…" : "⚡ Generate Intervention"}
      </button>
    </div>
  );

  return (
    <PageWrapper
      title="Interventions"
      subtitle="AI-generated actions to improve your financial health"
      action={GenerateButton}
    >
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : items?.length ? (
        <div className="space-y-4">
          {items.map((item) => (
            <InterventionCard key={item.id} item={item} />
          ))}
        </div>
      ) : (
        <div className="card py-16 text-center space-y-3">
          <p className="text-3xl">⚡</p>
          <p className="text-white font-medium">No active interventions</p>
          <p className="text-sm text-muted max-w-sm mx-auto">
            Generate an AI-powered intervention based on your current risk signals.
          </p>
        </div>
      )}
    </PageWrapper>
  );
}
