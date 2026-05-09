import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatINR(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatINRCompact(amount: number): string {
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`;
  return `₹${amount.toFixed(0)}`;
}

export function drsColor(score: number): string {
  if (score >= 81) return "#22c55e";
  if (score >= 61) return "#14b8a6";
  if (score >= 41) return "#f59e0b";
  if (score >= 21) return "#f97316";
  return "#ef4444";
}

export function drsLabel(score: number): string {
  if (score >= 81) return "Optimal";
  if (score >= 61) return "Stable";
  if (score >= 41) return "Caution";
  if (score >= 21) return "Danger";
  return "Critical";
}

export function drsTailwind(score: number): string {
  if (score >= 81) return "text-drs-optimal";
  if (score >= 61) return "text-drs-stable";
  if (score >= 41) return "text-drs-caution";
  if (score >= 21) return "text-drs-danger";
  return "text-drs-critical";
}

export function urgencyColor(urgency: string): string {
  return urgency === "high" ? "#ef4444" : urgency === "medium" ? "#f59e0b" : "#14b8a6";
}

export function urgencyBg(urgency: string): string {
  return urgency === "high"
    ? "bg-red-500/10 border-red-500/30 text-red-400"
    : urgency === "medium"
    ? "bg-amber-500/10 border-amber-500/30 text-amber-400"
    : "bg-teal-500/10 border-teal-500/30 text-teal-400";
}

export function relativeTime(dateStr: string): string {
  const d = new Date(dateStr);
  const now = new Date();
  const diff = Math.floor((now.getTime() - d.getTime()) / 1000);
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function categoryColor(category: string): string {
  const palette: Record<string, string> = {
    "Food & Dining": "#f97316",
    Transport: "#3b82f6",
    Entertainment: "#a855f7",
    Shopping: "#ec4899",
    Utilities: "#64748b",
    Health: "#22c55e",
    "Rent/EMI": "#ef4444",
    Groceries: "#f59e0b",
    Income: "#14b8a6",
    Savings: "#6366f1",
    Uncategorized: "#475569",
  };
  return palette[category] ?? "#475569";
}

export function riskLabel(score: number): string {
  if (score >= 0.7) return "High Risk";
  if (score >= 0.4) return "Medium Risk";
  return "Low Risk";
}

export function riskBadgeClass(score: number): string {
  if (score >= 0.7) return "bg-red-500/10 text-red-400 border border-red-500/20";
  if (score >= 0.4) return "bg-amber-500/10 text-amber-400 border border-amber-500/20";
  return "bg-teal-500/10 text-teal-400 border border-teal-500/20";
}

export function componentLabel(key: string): string {
  const labels: Record<string, string> = {
    budget_adherence: "Budget Adherence",
    velocity_stability: "Velocity Stability",
    savings_rate: "Savings Rate",
    recurring_coverage: "Recurring Coverage",
    emotional_spend: "Emotional Spend",
    salary_gap: "Salary Gap",
  };
  return labels[key] ?? key;
}
