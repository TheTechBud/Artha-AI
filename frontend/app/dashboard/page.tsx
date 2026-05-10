"use client";

import { PageWrapper } from "@/components/layout/PageWrapper";
import { RiskAlertBanner } from "@/components/cards/RiskAlertBanner";
import { DRSCard } from "@/components/cards/DRSCard";
import { ChartFootnote } from "@/components/cards/ChartFootnote";
import { SpendingChart } from "@/components/charts/SpendingChart";
import { VelocitySparkline } from "@/components/charts/VelocitySparkline";
import { CategoryPie } from "@/components/charts/CategoryPie";
import { useAnalyticsSummary, useVelocity } from "@/hooks/useTransactions";
import { useRecalculateDRS } from "@/hooks/useDRS";
import { formatINR, formatINRCompact } from "@/lib/utils";
import { CardSkeleton, ChartSkeleton } from "@/components/ui/SkeletonLoader";
import type { AnalyticsSummary, VelocityPoint } from "@/types";

function CategoryBehaviorNote({ summary }: { summary: AnalyticsSummary }) {
  const top = summary.by_category[0];
  const emotionalPct =
    summary.total_spend > 0 ? (summary.emotional_spend_total / summary.total_spend) * 100 : 0;
  return (
    <>
      <span className="text-white/85">{top.category}</span> leads at{" "}
      <span className="font-mono text-white/90">{top.pct_of_total}%</span> of visible spend.
      {emotionalPct >= 18 ? (
        <>
          {" "}
          Emotional-context debits are about{" "}
          <span className="text-amber-400/90">{emotionalPct.toFixed(0)}%</span> — worth noticing when they bunch up on weekends or late nights.
        </>
      ) : (
        <>
          {" "}
          Emotional-context debits are a smaller slice right now; keep an eye on timing when totals climb.
        </>
      )}
    </>
  );
}

function VelocityBehaviorNote({ velocity }: { velocity: VelocityPoint[] }) {
  const last = velocity[velocity.length - 1]?.rolling_spend ?? 0;
  const slice = velocity.slice(-14);
  const avg = slice.reduce((s, v) => s + v.rolling_spend, 0) / Math.max(slice.length, 1);
  const ratio = avg > 0 ? last / avg : 1;
  let hint = "In line with your recent baseline.";
  if (ratio >= 1.25) hint = "Above your recent 2-week average — often bills plus discretionary stacking.";
  else if (ratio <= 0.85) hint = "Below your recent average — calmer pace than usual.";
  return (
    <>
      Rolling 7-day debit spend is{" "}
      <span className="font-mono text-white/90">₹{(last / 1000).toFixed(1)}K</span>. {hint}
    </>
  );
}

function PieBehaviorNote({ summary }: { summary: AnalyticsSummary }) {
  const top2 = summary.by_category.slice(0, 2);
  const sumPct = top2.reduce((s, c) => s + c.pct_of_total, 0);
  return (
    <>
      Top two categories cover{" "}
      <span className="font-mono text-white/90">{sumPct.toFixed(0)}%</span> of spend — concentration here drives how “volatile” spending feels week to week.
    </>
  );
}

function StatCard({
  label, value, sub, positive,
}: { label: string; value: string; sub?: string; positive?: boolean }) {
  return (
    <div className="card">
      <p className="label-xs mb-2">{label}</p>
      <p className="stat-number">{value}</p>
      {sub && (
        <p className={`text-xs mt-1 ${positive === undefined ? "text-muted" : positive ? "text-drs-optimal" : "text-drs-danger"}`}>
          {sub}
        </p>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const { data: summary, isLoading: summaryLoading } = useAnalyticsSummary();
  const { data: velocity, isLoading: velocityLoading } = useVelocity();
  const recalculate = useRecalculateDRS();

  const RefreshButton = (
    <button
      onClick={() => recalculate.mutate()}
      disabled={recalculate.isPending}
      className="flex items-center gap-2 px-3 py-1.5 bg-teal-500/10 text-teal-400 border border-teal-500/20 rounded-lg text-sm hover:bg-teal-500/20 transition-colors"
    >
      {recalculate.isPending ? (
        <>
          <span className="inline-block w-3 h-3 border border-teal-400 border-t-transparent rounded-full animate-spin" />
          Recalculating…
        </>
      ) : (
        "↺ Refresh DRS"
      )}
    </button>
  );

  return (
    <PageWrapper
      title="Dashboard"
      subtitle={summary?.month ?? "Financial Overview"}
      action={RefreshButton}
    >
      <RiskAlertBanner />

      {/* Stat row */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {summaryLoading ? (
          Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)
        ) : summary ? (
          <>
            <StatCard
              label="Total Spend"
              value={formatINRCompact(summary.total_spend)}
              sub={`${summary.month}`}
            />
            <StatCard
              label="Total Income"
              value={formatINRCompact(summary.total_income)}
              sub="Credited this month"
              positive
            />
            <StatCard
              label="Net Savings"
              value={formatINRCompact(Math.abs(summary.net))}
              sub={summary.net >= 0 ? "Surplus" : "Deficit"}
              positive={summary.net >= 0}
            />
            <StatCard
              label="Emotional Spend"
              value={formatINRCompact(summary.emotional_spend_total)}
              sub={`${((summary.emotional_spend_total / (summary.total_spend || 1)) * 100).toFixed(0)}% of total`}
              positive={summary.emotional_spend_total / (summary.total_spend || 1) < 0.2}
            />
          </>
        ) : null}
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-3 gap-4">
        {/* DRS Card — takes 1 col */}
        <div className="col-span-1">
          <DRSCard />
        </div>

        {/* Spending breakdown — 2 cols */}
        <div className="col-span-2 space-y-4">
          {/* Category Bar */}
          <div className="card">
            <p className="label-xs mb-3">Spending by Category</p>
            {summaryLoading ? (
              <ChartSkeleton height={260} />
            ) : summary?.by_category?.length ? (
              <SpendingChart data={summary.by_category} />
            ) : (
              <EmptyState label="No spending data yet" />
            )}
            {summary?.by_category?.length ? (
              <ChartFootnote title="Behavioral read">
                <CategoryBehaviorNote summary={summary} />
              </ChartFootnote>
            ) : null}
          </div>

          {/* Velocity */}
          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <p className="label-xs">7-Day Spending Velocity</p>
              {velocity && velocity.length > 0 && (
                <span className="text-xs text-muted font-mono">
                  Rolling ₹{(velocity[velocity.length - 1]?.rolling_spend / 1000).toFixed(1)}K
                </span>
              )}
            </div>
            {velocityLoading ? (
              <ChartSkeleton height={120} />
            ) : velocity?.length ? (
              <VelocitySparkline data={velocity} />
            ) : (
              <EmptyState label="No velocity data yet" />
            )}
            {velocity && velocity.length > 0 ? (
              <ChartFootnote title="Behavioral read">
                <VelocityBehaviorNote velocity={velocity} />
              </ChartFootnote>
            ) : null}
          </div>
        </div>

        {/* Category Pie */}
        <div className="col-span-1 card">
          <p className="label-xs mb-3">Category Distribution</p>
          {summaryLoading ? (
            <ChartSkeleton height={260} />
          ) : summary?.by_category?.length ? (
            <CategoryPie data={summary.by_category} />
          ) : (
            <EmptyState label="No data" />
          )}
          {summary?.by_category && summary.by_category.length >= 2 ? (
            <ChartFootnote title="Behavioral read">
              <PieBehaviorNote summary={summary} />
            </ChartFootnote>
          ) : null}
        </div>

        {/* Recurring bills */}
        <div className="col-span-2 card">
          <p className="label-xs mb-3">Recurring Bills</p>
          {summaryLoading ? (
            <ChartSkeleton height={120} />
          ) : summary?.recurring?.length ? (
            <div className="space-y-2">
              {summary.recurring.slice(0, 5).map((r) => (
                <div
                  key={r.name}
                  className="flex items-center justify-between py-2 border-b border-border last:border-0"
                >
                  <div>
                    <p className="text-sm text-white capitalize">{r.name.toLowerCase()}</p>
                    <p className="text-xs text-muted capitalize">{r.frequency}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-mono text-white">{formatINR(r.avg_amount)}</p>
                    {r.next_expected && (
                      <p className="text-xs text-muted">Next: {r.next_expected}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState label="No recurring patterns detected" />
          )}
        </div>
      </div>
    </PageWrapper>
  );
}

function EmptyState({ label }: { label: string }) {
  return (
    <div className="flex items-center justify-center h-24 text-muted text-sm">
      {label}
    </div>
  );
}
