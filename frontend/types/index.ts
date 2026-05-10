// ── Core entities ──────────────────────────────────────────────────────────────

export interface Transaction {
  id: number;
  user_id: number;
  date: string;
  description: string;
  amount: number;
  type: "debit" | "credit";
  category: string;
  is_recurring: boolean;
  is_emotional: boolean;
  recurring_group_id?: string;
}

export interface TransactionList {
  transactions: Transaction[];
  total: number;
  page: number;
  page_size: number;
}

// ── DRS ────────────────────────────────────────────────────────────────────────

export interface DRSComponents {
  budget_adherence: number;
  velocity_stability: number;
  savings_rate: number;
  recurring_coverage: number;
  emotional_spend: number;
  salary_gap: number;
}

export interface DRSResult {
  score: number;
  label: "Optimal" | "Stable" | "Caution" | "Danger" | "Critical";
  color: "green" | "teal" | "amber" | "orange" | "red";
  components: DRSComponents;
  explanation?: string;
  calculated_at: string;
}

export interface DRSHistoryPoint {
  score: number;
  calculated_at: string;
}

// ── Analytics ──────────────────────────────────────────────────────────────────

export interface CategorySpend {
  category: string;
  total: number;
  count: number;
  pct_of_total: number;
}

export interface VelocityPoint {
  date: string;
  rolling_spend: number;
}

export interface RecurringItem {
  name: string;
  avg_amount: number;
  frequency: "weekly" | "biweekly" | "monthly";
  next_expected?: string;
  last_seen?: string;
  occurrence_count?: number;
}

export interface AnalyticsSummary {
  total_spend: number;
  total_income: number;
  net: number;
  by_category: CategorySpend[];
  velocity_data: VelocityPoint[];
  recurring: RecurringItem[];
  emotional_spend_total: number;
  top_category: string;
  month: string;
}

// ── Interventions ─────────────────────────────────────────────────────────────

export interface Intervention {
  id: number;
  title: string;
  action: string;
  reason: string;
  urgency: "low" | "medium" | "high";
  savings_potential: number;
  status: "active" | "dismissed" | "completed";
  generated_at: string;
}

// ── Narrative ─────────────────────────────────────────────────────────────────

export interface Narrative {
  id: number;
  narrative_text: string;
  key_insights?: string;
  drs_at_generation?: number;
  generated_at: string;
}

// ── Archetype ─────────────────────────────────────────────────────────────────

export interface Archetype {
  archetype: string;
  confidence: number;
  key_signals: string[];
}

// ── Risk Signals ──────────────────────────────────────────────────────────────

export interface RiskSignal {
  signal_type: string;
  risk_score: number;
  description: string;
  predicted_for_date?: string;
}

export interface RiskPayload {
  signals: RiskSignal[];
  aggregate: number;
}

// ── Calendar ──────────────────────────────────────────────────────────────────

export interface CalendarDay {
  date: string;
  day: number;
  type: "normal" | "amber" | "red";
  is_today: boolean;
  is_past: boolean;
}

// ── API wrapper ───────────────────────────────────────────────────────────────

export interface APIResponse<T> {
  data: T;
  meta?: Record<string, unknown>;
  timestamp?: string;
}

// ── Upload (multipart returns full envelope) ──────────────────────────────────

export interface UploadPipelineResult {
  drs_score: number;
  archetype?: string;
  risk_aggregate: number;
  intervention_generated: { id: number; urgency: string } | null;
}

export interface TransactionUploadData {
  inserted: number;
  rows_processed: number;
  pipeline?: UploadPipelineResult;
}

export interface TransactionUploadEnvelope {
  data: TransactionUploadData;
  message: string;
}
