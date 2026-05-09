"use client";

import { PageWrapper } from "@/components/layout/PageWrapper";
import { DRSGauge } from "@/components/charts/DRSGauge";
import { DRSLine } from "@/components/charts/VelocitySparkline";
import { useDRS, useDRSHistory, useRecalculateDRS } from "@/hooks/useDRS";
import { CardSkeleton, ChartSkeleton } from "@/components/ui/SkeletonLoader";
import { componentLabel, drsColor } from "@/lib/utils";

export default function DRSPage() {
  const { data: drs, isLoading } = useDRS();
  const { data: history } = useDRSHistory(30);
  const recalc = useRecalculateDRS();

  return (
    <PageWrapper
      title="Decision Readiness Score"
      subtitle="Your behavioral finance health score"
      action={
        <button
          onClick={() => recalc.mutate()}
          disabled={recalc.isPending}
          className="px-3 py-1.5 bg-teal-500/10 text-teal-400 border border-teal-500/20 rounded-lg text-sm hover:bg-teal-500/20 transition-colors"
        >
          {recalc.isPending ? "Recalculating…" : "↺ Recalculate"}
        </button>
      }
    >
      <div className="grid grid-cols-3 gap-4">
        {/* Gauge */}
        <div className="card col-span-1 flex flex-col items-center">
          {isLoading ? (
            <CardSkeleton />
          ) : drs ? (
            <>
              <p className="label-xs self-start mb-2">Current Score</p>
              <DRSGauge score={drs.score} label={drs.label} />
              <p className="text-xs text-muted mt-2 text-center">
                Calculated at{" "}
                {new Date(drs.calculated_at).toLocaleTimeString("en-IN", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
              {drs.explanation && (
                <p className="text-sm text-white/70 mt-4 border-t border-border pt-4 leading-relaxed">
                  {drs.explanation}
                </p>
              )}
            </>
          ) : null}
        </div>

        {/* Component breakdown */}
        <div className="card col-span-2">
          <p className="label-xs mb-5">Score Components</p>
          {isLoading ? (
            <CardSkeleton />
          ) : drs ? (
            <div className="space-y-5">
              {Object.entries(drs.components).map(([key, value]) => {
                const pct = Math.round(value * 100);
                const color = pct >= 70 ? "#22c55e" : pct >= 40 ? "#f59e0b" : "#ef4444";
                const descriptions: Record<string, string> = {
                  budget_adherence: "How well spending stays within set category limits",
                  velocity_stability: "Consistency of spending pace over rolling 7-day windows",
                  savings_rate: "Percentage of income preserved after expenses",
                  recurring_coverage: "Ability to cover upcoming recurring bills from available balance",
                  emotional_spend: "Proportion of spending driven by emotional contexts",
                  salary_gap: "Risk of running out of money before next salary arrives",
                };
                return (
                  <div key={key}>
                    <div className="flex items-center justify-between mb-1.5">
                      <div>
                        <p className="text-sm text-white font-medium">{componentLabel(key)}</p>
                        <p className="text-xs text-muted">{descriptions[key]}</p>
                      </div>
                      <span
                        className="text-lg font-semibold font-mono ml-4 shrink-0"
                        style={{ color }}
                      >
                        {pct}
                      </span>
                    </div>
                    <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${pct}%`, background: color }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : null}
        </div>

        {/* History chart */}
        <div className="card col-span-3">
          <p className="label-xs mb-3">30-Day DRS History</p>
          {history && history.length > 1 ? (
            <DRSLine data={history} height={180} />
          ) : (
            <ChartSkeleton height={180} />
          )}
        </div>

        {/* DRS scale legend */}
        <div className="card col-span-3">
          <p className="label-xs mb-4">Score Reference</p>
          <div className="grid grid-cols-5 gap-3">
            {[
              { range: "81–100", label: "Optimal", color: "#22c55e", desc: "Excellent financial discipline. Keep it up." },
              { range: "61–80",  label: "Stable",  color: "#14b8a6", desc: "Good habits. Small improvements possible." },
              { range: "41–60",  label: "Caution", color: "#f59e0b", desc: "Some risk factors active. Action recommended." },
              { range: "21–40",  label: "Danger",  color: "#f97316", desc: "Multiple risk signals. Immediate attention needed." },
              { range: "0–20",   label: "Critical", color: "#ef4444", desc: "Severe financial stress. Take action now." },
            ].map((tier) => (
              <div
                key={tier.label}
                className="rounded-xl p-3 border"
                style={{ borderColor: `${tier.color}30`, background: `${tier.color}08` }}
              >
                <p className="text-xs font-semibold mb-0.5" style={{ color: tier.color }}>{tier.label}</p>
                <p className="text-xs font-mono text-muted mb-2">{tier.range}</p>
                <p className="text-xs text-white/60 leading-relaxed">{tier.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageWrapper>
  );
}
