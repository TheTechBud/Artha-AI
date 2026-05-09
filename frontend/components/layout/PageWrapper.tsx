import { cn } from "@/lib/utils";

interface PageWrapperProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export function PageWrapper({ title, subtitle, action, children, className }: PageWrapperProps) {
  return (
    <div className={cn("min-h-full flex flex-col", className)}>
      {/* Page header */}
      <header className="px-8 pt-7 pb-5 border-b border-border flex items-start justify-between gap-4">
        <div>
          <h1 className="text-lg font-semibold text-white">{title}</h1>
          {subtitle && <p className="text-sm text-muted mt-0.5">{subtitle}</p>}
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </header>

      {/* Page content */}
      <div className="flex-1 px-8 py-6">{children}</div>
    </div>
  );
}
