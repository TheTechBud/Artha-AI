import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "success" | "warning" | "danger" | "info";
}

const variantClass = {
  default: "bg-white/5 text-muted border border-border",
  success: "bg-teal-500/10 text-teal-400 border border-teal-500/20",
  warning: "bg-amber-500/10 text-amber-400 border border-amber-500/20",
  danger:  "bg-red-500/10 text-red-400 border border-red-500/20",
  info:    "bg-blue-500/10 text-blue-400 border border-blue-500/20",
};

export function Badge({ children, className, variant = "default" }: BadgeProps) {
  return (
    <span className={cn("badge", variantClass[variant], className)}>
      {children}
    </span>
  );
}

export function RiskDot({ score }: { score: number }) {
  const color =
    score >= 0.7 ? "bg-red-500" :
    score >= 0.4 ? "bg-amber-500" :
    "bg-teal-500";
  return <span className={cn("inline-block w-2 h-2 rounded-full", color)} />;
}
