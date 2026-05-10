"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";

const NAV = [
  { href: "/dashboard",      label: "Dashboard",      icon: "⬡" },
  { href: "/drs",            label: "DRS Score",       icon: "◎" },
  { href: "/transactions",   label: "Transactions",    icon: "⇄" },
  { href: "/predictions",    label: "Predictions",     icon: "◈" },
  { href: "/interventions",  label: "Interventions",   icon: "⚡" },
  { href: "/narrative",      label: "Narrative",       icon: "✦" },
];

function avatarInitials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  return (parts[0]?.slice(0, 2) ?? "?").toUpperCase();
}

export function Sidebar() {
  const pathname = usePathname();
  const { data: demoUser } = useQuery({
    queryKey: ["demo-user"],
    queryFn: () => api.demo.user(),
  });

  const displayName = demoUser?.name ?? "Demo user";
  const initials = demoUser ? avatarInitials(demoUser.name) : "—";

  return (
    <aside className="w-56 shrink-0 flex flex-col h-full bg-panel border-r border-border">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-teal-500 to-teal-700 flex items-center justify-center text-xs font-bold text-white">
            A
          </div>
          <div>
            <p className="text-sm font-semibold text-white tracking-tight">Artha AI</p>
            <p className="text-[10px] text-muted">Finance Copilot</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {NAV.map(({ href, label, icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150",
                active
                  ? "bg-teal-500/10 text-teal-400 font-medium"
                  : "text-muted hover:text-white hover:bg-white/5"
              )}
            >
              <span className="w-4 text-center text-base leading-none">{icon}</span>
              {label}
            </Link>
          );
        })}
      </nav>

      {/* User footer */}
      <div className="px-4 py-4 border-t border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-[10px] font-bold text-white shrink-0 leading-none">
            {initials}
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium text-white truncate">{displayName}</p>
            <p className="text-[10px] text-muted">Demo Account</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
