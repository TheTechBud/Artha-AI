"use client";

import { useDRS } from "@/hooks/useDRS";
import { DRSGauge } from "@/components/charts/DRSGauge";
import { CardSkeleton } from "@/components/ui/SkeletonLoader";
import { componentLabel, drsColor } from "@/lib/utils";
import { rankDrivers, weakestLinks } from "@/lib/drsInsights";

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
  const drivers = rankDrivers(components).slice(0, 2);
  const gaps = weakestLinks(components, 2);

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

      <div className="rounded-lg border border-border/80 bg-white/[0.02] px-3 py-2.5 space-y-1.5">
        <p className="text-[10px] uppercase tracking-wide text-muted">Behavioral focus</p>
        <p className="text-xs text-white/75 leading-relaxed">
          Strongest drivers right now:{" "}
          <span className="text-teal-400/95">
            {drivers.map((d) => componentLabel(d.key)).join(" · ")}
          </span>
          . Watch{" "}
          <span className="text-amber-400/90">
            {gaps.map((g) => componentLabel(g.key)).join(" · ")}
          </span>{" "}
          — small shifts here move your score the most.
        </p>
      </div>

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
        <div className="border-t border-border pt-3 space-y-1">
          <p className="text-[10px] uppercase tracking-wide text-muted">Why it moved</p>
          <p className="text-xs text-white/70 leading-relaxed">{data.explanation}</p>
        </div>
      )}
    </div>
  );
}
