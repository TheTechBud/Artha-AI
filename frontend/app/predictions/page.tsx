"use client";

import { PageWrapper } from "@/components/layout/PageWrapper";
import { useRisks, usePredictionsCalendar } from "@/hooks/useInterventions";
import { CardSkeleton } from "@/components/ui/SkeletonLoader";
import { riskBadgeClass, riskLabel } from "@/lib/utils";
import { RiskDot } from "@/components/ui/Badge";

const SIGNAL_LABELS: Record<string, { title: string; icon: string }> = {
  velocity_spike:  { title: "Spending Velocity Spike",    icon: "⚡" },
  salary_gap_risk: { title: "Salary Gap Risk",            icon: "⏳" },
  budget_overflow: { title: "Budget Overflow",            icon: "◈" },
  emotional_spend: { title: "Emotional Spending Pattern", icon: "🌊" },
  recurring_miss:  { title: "Recurring Bill Pressure",    icon: "↺" },
};

export default function PredictionsPage() {
  const { data: risks, isLoading: risksLoading } = useRisks();
  const { data: calendar } = usePredictionsCalendar();

  const aggregate = risks?.aggregate ?? 0;
  const signals = risks?.signals ?? [];

  return (
    <PageWrapper
      title="Predictions"
      subtitle="AI-powered behavioral risk forecasts"
    >
      <div className="grid grid-cols-3 gap-4">
        {/* Aggregate risk meter */}
        <div className="card col-span-1">
          <p className="label-xs mb-4">Aggregate Risk Score</p>
          {risksLoading ? (
            <CardSkeleton />
          ) : (
            <div className="space-y-4">
              <div className="flex items-end gap-3">
                <span className="text-5xl font-semibold tabular-nums" style={{
                  color: aggregate >= 0.7 ? "#ef4444" : aggregate >= 0.4 ? "#f59e0b" : "#22c55e"
                }}>
                  {(aggregate * 100).toFixed(0)}
                </span>
                <span className="text-muted text-lg mb-1">/100</span>
              </div>
              <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${aggregate * 100}%`,
                    background: aggregate >= 0.7 ? "#ef4444" : aggregate >= 0.4 ? "#f59e0b" : "#22c55e",
                  }}
                />
              </div>
              <p className="text-sm text-white/70">{riskLabel(aggregate)}</p>
              <p className="text-xs text-muted leading-relaxed">
                {aggregate >= 0.7
                  ? "Multiple high-risk signals detected. Immediate action recommended."
                  : aggregate >= 0.4
                  ? "Elevated risk. Monitor your spending velocity and upcoming bills."
                  : "Financial risk is currently low. Keep maintaining healthy habits."}
              </p>
            </div>
          )}
        </div>

        {/* Signal breakdown */}
        <div className="card col-span-2">
          <p className="label-xs mb-4">Risk Signal Breakdown</p>
          {risksLoading ? (
            <CardSkeleton />
          ) : signals.length ? (
            <div className="space-y-3">
              {signals
                .sort((a, b) => b.risk_score - a.risk_score)
                .map((sig) => {
                  const meta = SIGNAL_LABELS[sig.signal_type] ?? { title: sig.signal_type, icon: "◎" };
                  const pct = Math.round(sig.risk_score * 100);
                  return (
                    <div key={sig.signal_type} className="border border-border rounded-xl p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span>{meta.icon}</span>
                          <p className="text-sm font-medium text-white">{meta.title}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <RiskDot score={sig.risk_score} />
                          <span className={`badge ${riskBadgeClass(sig.risk_score)}`}>
                            {riskLabel(sig.risk_score)}
                          </span>
                        </div>
                      </div>
                      <p className="text-xs text-muted">{sig.description}</p>
                      <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${pct}%`,
                            background: sig.risk_score >= 0.7 ? "#ef4444" : sig.risk_score >= 0.4 ? "#f59e0b" : "#22c55e",
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
            </div>
          ) : (
            <p className="text-muted text-sm py-8 text-center">No risk signals available.</p>
          )}
        </div>

        {/* Calendar */}
        {calendar && calendar.length > 0 && (
          <div className="card col-span-3">
            <div className="flex items-center justify-between mb-4">
              <p className="label-xs">Monthly Risk Calendar</p>
              <div className="flex items-center gap-4 text-xs text-muted">
                <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-white/10 inline-block" />Normal</span>
                <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-amber-500 inline-block" />Bill Due</span>
                <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-red-500 inline-block" />High Risk</span>
              </div>
            </div>
            <div className="grid grid-cols-7 gap-1.5">
              {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((d) => (
                <div key={d} className="text-center text-xs text-muted py-1 font-medium">{d}</div>
              ))}
              {calendar.map((day) => (
                <div
                  key={day.date}
                  className={`aspect-square rounded-lg flex items-center justify-center text-xs transition-colors relative
                    ${day.is_today ? "ring-2 ring-teal-500" : ""}
                    ${day.is_past ? "opacity-40" : ""}
                    ${day.type === "red" ? "bg-red-500/15 text-red-400 font-semibold" :
                      day.type === "amber" ? "bg-amber-500/15 text-amber-400 font-semibold" :
                      "bg-white/3 text-white/60 hover:bg-white/6"}
                  `}
                >
                  {day.day}
                  {day.type !== "normal" && (
                    <span className={`absolute top-0.5 right-0.5 w-1.5 h-1.5 rounded-full ${
                      day.type === "red" ? "bg-red-500" : "bg-amber-500"
                    }`} />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </PageWrapper>
  );
}
