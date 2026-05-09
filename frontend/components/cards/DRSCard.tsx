"use client";

import { useDRS } from "@/hooks/useDRS";
import { DRSGauge } from "@/components/charts/DRSGauge";
import { CardSkeleton } from "@/components/ui/SkeletonLoader";
import { componentLabel, drsColor } from "@/lib/utils";

export function DRSCard() {
  const { data, isLoading, error } = useDRS();

  if (isLoading) return <CardSkeleton />;
  if (error || !data) {
    return (
      <div className="card flex items-center justify-center h-48 text-muted text-sm">
        Failed to load DRS
      </div>
    );
  }

  const components = data.components;

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <p className="label-xs">Decision Readiness Score</p>
        <span
          className="text-xs font-semibold px-2 py-0.5 rounded-full"
          style={{
            color: drsColor(data.score),
            background: `${drsColor(data.score)}18`,
          }}
        >
          {data.label}
        </span>
      </div>

      <DRSGauge score={data.score} label={data.label} />

      {/* Component breakdown */}
      <div className="space-y-2 pt-1">
        {Object.entries(components).map(([key, value]) => {
          const pct = Math.round(value * 100);
          const barColor = pct >= 70 ? "#22c55e" : pct >= 40 ? "#f59e0b" : "#ef4444";
          return (
            <div key={key}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-muted">{componentLabel(key)}</span>
                <span className="font-mono" style={{ color: barColor }}>{pct}%</span>
              </div>
              <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${pct}%`, background: barColor }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {data.explanation && (
        <p className="text-xs text-muted border-t border-border pt-3 leading-relaxed">
          {data.explanation}
        </p>
      )}
    </div>
  );
}
