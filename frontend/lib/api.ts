import type {
  DRSResult, DRSHistoryPoint, AnalyticsSummary,
  TransactionList, Intervention, Narrative,
  Archetype, RiskPayload, CalendarDay, APIResponse,
  VelocityPoint, RecurringItem,
  TransactionUploadEnvelope,
  DemoUser,
} from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? err.error ?? `API error ${res.status}`);
  }
  const json: APIResponse<T> = await res.json();
  return json.data;
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? err.error ?? `API error ${res.status}`);
  }
  const json: APIResponse<T> = await res.json();
  return json.data;
}

async function patch<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { method: "PATCH" });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  const json: APIResponse<T> = await res.json();
  return json.data;
}

// ── Endpoints ──────────────────────────────────────────────────────────────────

export const api = {
  demo: {
    user: () => get<DemoUser>("/api/demo/user"),
  },

  // DRS
  drs: {
    current: () => get<DRSResult>("/api/drs/current"),
    history: (days = 30) => get<DRSHistoryPoint[]>(`/api/drs/history?days=${days}`),
    recalculate: () => post<DRSResult>("/api/drs/recalculate"),
  },

  // Analytics
  analytics: {
    summary: () => get<AnalyticsSummary>("/api/analytics/summary"),
    velocity: () => get<VelocityPoint[]>("/api/analytics/velocity"),
    recurring: () => get<RecurringItem[]>("/api/analytics/recurring"),
  },

  // Transactions
  transactions: {
    list: (page = 1, pageSize = 50, category?: string) => {
      const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
      if (category) params.set("category", category);
      return get<TransactionList>(`/api/transactions?${params}`);
    },
    upload: async (file: File): Promise<TransactionUploadEnvelope> => {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${BASE}/api/transactions/upload`, { method: "POST", body: form });
      if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
      return res.json();
    },
  },

  // Interventions
  interventions: {
    list: () => get<Intervention[]>("/api/interventions"),
    generate: (riskType = "velocity_spike") =>
      post<Intervention>(`/api/interventions/generate?risk_type=${riskType}`),
    dismiss: (id: number) => patch<{ id: number; status: string }>(`/api/interventions/${id}/dismiss`),
  },

  // Narrative
  narrative: {
    latest: () => get<Narrative | null>("/api/narrative/latest"),
    generate: () => post<Narrative>("/api/narrative/generate"),
  },

  // AI
  ai: {
    archetype: () => get<Archetype>("/api/ai/archetype"),
    risks: () => get<RiskPayload>("/api/ai/risks"),
    calendar: () => get<CalendarDay[]>("/api/ai/predictions/calendar"),
  },
};
