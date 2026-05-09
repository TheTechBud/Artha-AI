"use client";

import { useRisks } from "@/hooks/useInterventions";

export function RiskAlertBanner() {
  const { data, isLoading } = useRisks();

  if (isLoading || !data) return null;
  const aggregate = data.aggregate ?? 0;
  if (aggregate < 0.45) return null;

  const isHigh = aggregate >= 0.7;
  const topSignal = data.signals
    ?.filter((s) => s.risk_score > 0)
    .sort((a, b) => b.risk_score - a.risk_score)[0];

  return (
    <div
      className={`flex items-start gap-3 rounded-xl px-4 py-3 border mb-6 text-sm ${
        isHigh
          ? "bg-red-500/8 border-red-500/25 text-red-300"
          : "bg-amber-500/8 border-amber-500/25 text-amber-300"
      }`}
    >
      <span className="text-lg leading-none mt-0.5">{isHigh ? "⚠" : "◈"}</span>
      <div>
        <p className="font-medium">
          {isHigh ? "High financial risk detected" : "Elevated spending risk"}
          <span className="ml-2 font-mono text-xs opacity-70">
            [{(aggregate * 100).toFixed(0)}% aggregate]
          </span>
        </p>
        {topSignal && (
          <p className="text-xs opacity-80 mt-0.5">{topSignal.description}</p>
        )}
      </div>
    </div>
  );
}
