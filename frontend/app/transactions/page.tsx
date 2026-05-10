"use client";

import { useState, useRef } from "react";
import { PageWrapper } from "@/components/layout/PageWrapper";
import { useTransactions, useUploadTransactions } from "@/hooks/useTransactions";
import { TableSkeleton } from "@/components/ui/SkeletonLoader";
import { Badge } from "@/components/ui/Badge";
import { formatINR, formatDate, categoryColor } from "@/lib/utils";

const CATEGORIES = [
  "All", "Food & Dining", "Transport", "Entertainment",
  "Shopping", "Utilities", "Health", "Rent/EMI", "Groceries",
];

export default function TransactionsPage() {
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const { data, isLoading } = useTransactions(page, 50, category);
  const upload = useUploadTransactions();

  const pipeline = upload.data?.data?.pipeline;

  const handleFile = (file: File) => {
    if (!file.name.endsWith(".csv")) {
      alert("Only CSV files are supported");
      return;
    }
    upload.mutate(file);
  };

  const UploadZone = (
    <div className="flex items-center gap-3">
      {upload.isPending && (
        <span className="text-xs text-muted animate-pulse">Processing CSV…</span>
      )}
      {upload.isSuccess && (
        <span className="text-xs text-teal-400">
          ✓ Imported · DRS & risks refreshed
        </span>
      )}
      <button
        onClick={() => fileRef.current?.click()}
        className="px-3 py-1.5 bg-teal-500/10 text-teal-400 border border-teal-500/20 rounded-lg text-sm hover:bg-teal-500/20 transition-colors"
      >
        ↑ Upload CSV
      </button>
      <input
        ref={fileRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={(e) => { if (e.target.files?.[0]) handleFile(e.target.files[0]); }}
      />
    </div>
  );

  return (
    <PageWrapper
      title="Transactions"
      subtitle={data ? `${data.total} transactions total` : undefined}
      action={UploadZone}
    >
      {upload.isSuccess && pipeline ? (
        <div className="mb-5 rounded-xl border border-teal-500/25 bg-teal-500/[0.06] px-4 py-3">
          <p className="text-sm text-teal-400 font-medium">Upload complete — profile recomputed</p>
          <p className="text-xs text-muted mt-1.5 leading-relaxed">
            Latest DRS{" "}
            <span className="font-mono text-white/90">{pipeline.drs_score.toFixed(1)}</span>
            {" · "}
            Risk index{" "}
            <span className="font-mono text-white/90">
              {(pipeline.risk_aggregate * 100).toFixed(0)}%
            </span>
            {pipeline.archetype ? (
              <>
                {" · "}
                Archetype refreshed ({pipeline.archetype.replace(/_/g, " ")})
              </>
            ) : null}
            {pipeline.intervention_generated ? (
              <>
                {" · "}
                New intervention ({pipeline.intervention_generated.urgency})
              </>
            ) : (
              <>
                {" · "}
                No new intervention — aggregate risk below threshold
              </>
            )}
          </p>
        </div>
      ) : null}

      {/* Drop zone overlay */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          const f = e.dataTransfer.files[0];
          if (f) handleFile(f);
        }}
        className={`transition-all ${dragOver ? "ring-2 ring-teal-500 ring-offset-2 ring-offset-surface rounded-xl" : ""}`}
      >
        {/* Category filter */}
        <div className="flex gap-2 flex-wrap mb-5">
          {CATEGORIES.map((cat) => {
            const active = (cat === "All" && !category) || cat === category;
            return (
              <button
                key={cat}
                onClick={() => setCategory(cat === "All" ? undefined : cat)}
                className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                  active
                    ? "bg-teal-500/15 text-teal-400 border-teal-500/30"
                    : "text-muted border-border hover:text-white hover:border-white/20"
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>

        {/* Table */}
        {isLoading ? (
          <TableSkeleton rows={10} />
        ) : (
          <div className="card p-0 overflow-hidden">
            {data?.transactions?.length ? (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left px-4 py-3 label-xs">Date</th>
                    <th className="text-left px-4 py-3 label-xs">Description</th>
                    <th className="text-left px-4 py-3 label-xs">Category</th>
                    <th className="text-left px-4 py-3 label-xs">Flags</th>
                    <th className="text-right px-4 py-3 label-xs">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {data.transactions.map((txn) => (
                    <tr
                      key={txn.id}
                      className="border-b border-border/50 hover:bg-white/3 transition-colors"
                    >
                      <td className="px-4 py-3 text-muted whitespace-nowrap font-mono text-xs">
                        {formatDate(txn.date)}
                      </td>
                      <td className="px-4 py-3 text-white max-w-xs truncate">
                        {txn.description.charAt(0) + txn.description.slice(1).toLowerCase()}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="badge"
                          style={{
                            color: categoryColor(txn.category),
                            background: `${categoryColor(txn.category)}18`,
                            border: `1px solid ${categoryColor(txn.category)}30`,
                          }}
                        >
                          {txn.category}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-1.5">
                          {txn.is_recurring && (
                            <Badge variant="info">↺ Recurring</Badge>
                          )}
                          {txn.is_emotional && (
                            <Badge variant="warning">⚡ Emotional</Badge>
                          )}
                        </div>
                      </td>
                      <td className={`px-4 py-3 text-right font-mono font-medium ${
                        txn.type === "credit" ? "text-drs-optimal" : "text-white"
                      }`}>
                        {txn.type === "credit" ? "+" : "−"}
                        {formatINR(txn.amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="py-16 text-center space-y-3">
                <p className="text-muted">No transactions found.</p>
                <p className="text-xs text-muted/60">Upload a CSV or run the seed script to load demo data.</p>
              </div>
            )}
          </div>
        )}

        {/* Pagination */}
        {data && data.total > 50 && (
          <div className="flex items-center justify-between mt-4 text-xs text-muted">
            <span>
              Showing {(page - 1) * 50 + 1}–{Math.min(page * 50, data.total)} of {data.total}
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1.5 border border-border rounded-lg hover:border-white/30 disabled:opacity-30"
              >
                ← Prev
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page * 50 >= data.total}
                className="px-3 py-1.5 border border-border rounded-lg hover:border-white/30 disabled:opacity-30"
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </div>
    </PageWrapper>
  );
}
