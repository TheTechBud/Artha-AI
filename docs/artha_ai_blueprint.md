# Artha AI — Complete Implementation Blueprint
### Hackathon CTO Architecture Document | Solo Developer | 6-Day Build

---

## TABLE OF CONTENTS

1. Complete System Architecture
2. Project Folder Structure
3. Frontend Architecture (Next.js)
4. Backend Architecture (FastAPI)
5. Database Design (SQLite)
6. LangChain Usage
7. OpenAI Integration Design
8. Analytics Engine
9. Decision Readiness Score (DRS)
10. Dataset Design
11. Demo Architecture (90-second flow)
12. Build Roadmap (6 days)
13. Hackathon Strategy
14. Final Deliverables

---

## 1. COMPLETE SYSTEM ARCHITECTURE

### Overall Data Flow

```
User → Next.js UI
         ↓ HTTP (fetch/axios)
     FastAPI Router
         ↓
    ┌────────────────────────────────────────┐
    │ Service Layer                          │
    │  TransactionService                    │
    │  AnalyticsService   ← pandas/numpy     │
    │  DRSService         ← pure Python math │
    │  AIOrchestrator     ← LangChain        │
    └────────────────────────────────────────┘
         ↓
    OpenAI GPT-4o (4 use cases only)
         ↓ structured JSON
    SQLite via SQLAlchemy (sync)
         ↓
    OpenTelemetry spans + file logger
```

### Frontend → Backend Interaction

- All state fetched via REST (no WebSockets needed for demo)
- Optimistic UI updates with `useSWR` or `react-query`
- Auth: None for demo — single hard-coded user (user_id=1)
- File upload for CSV transactions via `multipart/form-data`

### AI Service Flow

```
Request → AIOrchestrator.run(task, context)
  ├── task = "classify_archetype"  → LLMChain with classification prompt
  ├── task = "generate_narrative"  → LLMChain with narrative prompt
  ├── task = "generate_intervention" → LLMChain with intervention prompt
  └── task = "explain_drs"         → Direct OpenAI call (simple, no chain)

All outputs → Pydantic parser → validated dict → stored to DB + returned
```

### Transaction Pipeline

```
CSV Upload
  → pandas.read_csv()
  → clean_transactions() [strip nulls, parse dates, normalize amounts]
  → classify_categories() [rule-based first, GPT fallback for unknowns]
  → detect_recurring() [frequency analysis with pandas groupby]
  → compute_velocity() [rolling 7-day spend sum]
  → insert_bulk() [SQLAlchemy bulk insert]
  → trigger analytics recalculation [async task or sync if small]
```

### Prediction Pipeline

```
Scheduler or on-demand trigger
  → load_transactions(last_90_days)
  → run_risk_signals() [rule-based: salary_gap, velocity_spike, etc.]
  → score_each_signal() [0–1 per signal, weighted]
  → aggregate_risk_score()
  → if score > ALERT_THRESHOLD: create alert record
  → store prediction_history row
  → return prediction payload to frontend
```

### Intervention Pipeline

```
On alert creation OR user request
  → load context [user profile, recent txns, DRS, behavioral archetype]
  → build_intervention_prompt(context)
  → LLMChain.run() → structured JSON {title, action, reason, urgency}
  → store interventions row
  → push to frontend as "action card"
```

### DRS Calculation Pipeline

```
Daily or on upload completion
  → load_user_financial_data()
  → compute_component_scores() [6 components, see §9]
  → normalize_and_weight()
  → clamp to [0, 100]
  → store drs_history row
  → if delta > 5 points: generate_drs_explanation() via GPT
```

### Where LangChain is Used vs. Raw Python

| Task                        | Technology         | Why                                        |
|-----------------------------|--------------------|--------------------------------------------|
| Archetype classification    | LangChain LLMChain | Structured output + easy prompt swapping   |
| Weekly narrative            | LangChain LLMChain | Chained persona + data context injection   |
| Intervention generation     | LangChain LLMChain | Reusable chain with schema validation      |
| DRS score explanation       | Direct OpenAI call | Single simple call, no chain needed        |
| Category classification     | Pure Python regex  | Rules cover 85%+ of transactions           |
| Recurring detection         | pandas groupby     | Deterministic math, no AI needed           |
| Spending velocity           | pandas rolling sum | Deterministic, fast                        |
| Risk scoring                | Pure Python        | Rule-based thresholds                      |
| Budget tracking             | Pure Python        | Simple arithmetic                          |

---

## 2. PROJECT FOLDER STRUCTURE

```
artha-ai/
├── README.md
├── .env.example
├── docker-compose.yml         ← optional, for demo env
│
├── backend/
│   ├── main.py                ← FastAPI app entry point
│   ├── requirements.txt
│   ├── .env
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── transactions.py   ← /api/transactions/*
│   │   │   ├── analytics.py      ← /api/analytics/*
│   │   │   ├── ai.py             ← /api/ai/*
│   │   │   ├── drs.py            ← /api/drs/*
│   │   │   ├── narrative.py      ← /api/narrative/*
│   │   │   └── interventions.py  ← /api/interventions/*
│   │   └── middleware/
│   │       ├── logging.py
│   │       └── error_handler.py
│   │
│   ├── services/
│   │   ├── transaction_service.py
│   │   ├── analytics_service.py
│   │   ├── drs_service.py
│   │   ├── intervention_service.py
│   │   └── narrative_service.py
│   │
│   ├── ai/
│   │   ├── orchestrator.py        ← main AIOrchestrator class
│   │   ├── chains/
│   │   │   ├── archetype_chain.py
│   │   │   ├── narrative_chain.py
│   │   │   └── intervention_chain.py
│   │   ├── prompts/
│   │   │   ├── archetype.py
│   │   │   ├── narrative.py
│   │   │   ├── intervention.py
│   │   │   └── explainability.py
│   │   └── parsers/
│   │       ├── archetype_parser.py
│   │       ├── narrative_parser.py
│   │       └── intervention_parser.py
│   │
│   ├── analytics/
│   │   ├── engine.py              ← AnalyticsEngine class
│   │   ├── velocity.py            ← spending velocity
│   │   ├── recurring.py           ← recurring detection
│   │   ├── risk_signals.py        ← rule-based risk
│   │   ├── budget_tracker.py
│   │   └── salary_cycle.py
│   │
│   ├── db/
│   │   ├── database.py            ← SQLAlchemy session setup
│   │   ├── models.py              ← all ORM models
│   │   ├── crud.py                ← reusable DB operations
│   │   └── artha.db               ← SQLite file (gitignored)
│   │
│   ├── schemas/
│   │   ├── transaction.py         ← Pydantic request/response schemas
│   │   ├── analytics.py
│   │   ├── drs.py
│   │   ├── intervention.py
│   │   └── narrative.py
│   │
│   ├── utils/
│   │   ├── date_utils.py
│   │   ├── formatting.py
│   │   └── constants.py
│   │
│   ├── observability/
│   │   ├── otel_setup.py          ← OpenTelemetry init
│   │   └── logger.py              ← structured logging
│   │
│   └── evaluation/
│       ├── runner.py              ← runs prompt evals
│       ├── golden_dataset.json    ← ground truth for prompts
│       └── metrics.py
│
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   │
│   ├── app/
│   │   ├── layout.tsx             ← root layout with sidebar
│   │   ├── page.tsx               ← redirect to /dashboard
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── transactions/
│   │   │   └── page.tsx
│   │   ├── predictions/
│   │   │   └── page.tsx
│   │   ├── drs/
│   │   │   └── page.tsx
│   │   ├── narrative/
│   │   │   └── page.tsx
│   │   ├── interventions/
│   │   │   └── page.tsx
│   │   └── onboarding/
│   │       └── page.tsx
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── TopBar.tsx
│   │   │   └── PageWrapper.tsx
│   │   ├── charts/
│   │   │   ├── SpendingChart.tsx   ← Plotly wrapper
│   │   │   ├── DRSGauge.tsx
│   │   │   ├── CategoryPie.tsx
│   │   │   └── VelocitySparkline.tsx
│   │   ├── cards/
│   │   │   ├── DRSCard.tsx
│   │   │   ├── InterventionCard.tsx
│   │   │   ├── RiskAlertBanner.tsx
│   │   │   └── NarrativeCard.tsx
│   │   ├── modals/
│   │   │   ├── InterventionModal.tsx
│   │   │   └── OnboardingModal.tsx
│   │   └── ui/
│   │       ├── Badge.tsx
│   │       ├── SkeletonLoader.tsx
│   │       └── Tooltip.tsx
│   │
│   ├── lib/
│   │   ├── api.ts                 ← typed API client
│   │   └── utils.ts
│   │
│   ├── hooks/
│   │   ├── useDRS.ts
│   │   ├── useTransactions.ts
│   │   └── useInterventions.ts
│   │
│   └── types/
│       └── index.ts               ← shared TypeScript interfaces
│
├── datasets/
│   ├── personas/
│   │   ├── persona_riya.json      ← salaried, emotional spender
│   │   ├── persona_arjun.json     ← freelancer, irregular income
│   │   └── persona_priya.json     ← disciplined, high DRS
│   ├── transactions/
│   │   ├── riya_transactions.csv
│   │   ├── arjun_transactions.csv
│   │   └── priya_transactions.csv
│   └── seed.py                    ← loads demo data into SQLite
│
├── prompts/
│   ├── archetype_v1.txt
│   ├── narrative_v1.txt
│   ├── intervention_v1.txt
│   └── explainability_v1.txt
│
└── docs/
    ├── architecture.png
    ├── drs_formula.md
    └── demo_script.md
```

---

## 3. FRONTEND ARCHITECTURE (Next.js)

### Routing Structure

| Route              | Purpose                                      |
|--------------------|----------------------------------------------|
| `/onboarding`      | First visit — persona selection, CSV upload   |
| `/dashboard`       | Main hub: DRS, top alerts, spend summary      |
| `/transactions`    | Full transaction list with filters            |
| `/predictions`     | Risk calendar, overspend predictions          |
| `/drs`             | DRS gauge, score breakdown, history chart     |
| `/narrative`       | Weekly AI-written finance story               |
| `/interventions`   | All action cards, history, status tracking    |

### Key Components

**Sidebar** — Fixed left nav with 6 icons + label. No hamburger menu (wastes demo time). Show DRS score numerically in the sidebar itself — judges see it at all times.

**DRS Gauge** — Plotly gauge chart, 0–100, color bands:
- 0–30: Red (Danger)
- 31–60: Amber (Caution)
- 61–80: Teal (Stable)
- 81–100: Green (Optimal)
Animate on load with a 1.2s transition.

**InterventionCard** — Appears as a dismissable card with:
- Urgency badge (High/Medium/Low)
- Title + 2-line explanation
- "Take Action" CTA button
- "Dismiss" link

**RiskAlertBanner** — Sticky banner at top of dashboard when DRS < 40. Shows prediction reason + link to intervention.

**NarrativeCard** — Full-width card on `/narrative`. Shows AI-generated paragraph + key metrics that informed it. Add a "Regenerate" button for demo wow-factor.

**SpendingChart** — Plotly bar chart, grouped by category, last 30 days. Enable `click` event on bars to drill into category transactions.

**PredictiveCalendar** — Simple month grid. Highlight danger dates (predicted overspend) in red, upcoming recurring bills in amber. Build this as a custom grid, NOT a heavyweight calendar library.

### State Management

Use `react-query` (TanStack Query) for all server state. Do NOT use Redux — overkill.

```typescript
// Example hook pattern
export function useDRS(userId: number) {
  return useQuery({
    queryKey: ['drs', userId],
    queryFn: () => api.get(`/drs/${userId}`),
    staleTime: 60_000,   // 1 min cache
  });
}
```

### Onboarding UI

3-step wizard — keep it under 60 seconds:
1. Select persona (3 cards: Salaried Professional, Freelancer, Student)
2. Upload CSV (or click "Use demo data" — this is the real path for judges)
3. AI processes → redirect to dashboard with animation

### Animations That Matter

- DRS gauge fill on mount (Plotly's built-in transition)
- InterventionCard slides in from right on appearance (`framer-motion` or CSS)
- Number counters on dashboard stats (count up from 0)
- Skeleton loaders on every data card — judges must never see blank white

### What NOT to Build

- Dark mode toggle — pick one and ship it
- Notifications system
- User authentication / login
- Settings page
- Mobile responsive layout (demo on desktop)
- Multi-user support
- Real-time WebSocket updates

---

## 4. BACKEND ARCHITECTURE (FastAPI)

### API Endpoints

```
POST  /api/transactions/upload        ← multipart CSV
GET   /api/transactions               ← paginated list
GET   /api/transactions/{id}
GET   /api/analytics/summary          ← spend by category, velocity
GET   /api/analytics/velocity         ← rolling spend data
GET   /api/analytics/recurring        ← detected recurring items
GET   /api/drs/current                ← latest DRS score + breakdown
GET   /api/drs/history                ← DRS over time
POST  /api/drs/recalculate            ← trigger fresh calc
GET   /api/predictions/risks          ← current risk signals
GET   /api/predictions/calendar       ← month-view data
GET   /api/interventions              ← all active interventions
POST  /api/interventions/generate     ← trigger AI intervention
PATCH /api/interventions/{id}/dismiss
GET   /api/narrative/latest           ← latest weekly narrative
POST  /api/narrative/generate         ← trigger AI narrative
GET   /api/ai/archetype               ← behavioral archetype
```

### Service Layer Structure

```python
# services/drs_service.py
class DRSService:
    def __init__(self, db: Session, analytics: AnalyticsEngine):
        self.db = db
        self.analytics = analytics

    def calculate(self, user_id: int) -> DRSResult:
        data = self.analytics.load_user_data(user_id)
        components = self._compute_components(data)
        score = self._weighted_sum(components)
        self._store_history(user_id, score, components)
        return DRSResult(score=score, components=components)
```

Every service follows the same pattern: `__init__` takes db + dependencies, public methods return Pydantic models, private `_methods` do the math.

### AI Orchestration Layer

```python
# ai/orchestrator.py
class AIOrchestrator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.chains = {
            "archetype": build_archetype_chain(self.llm),
            "narrative": build_narrative_chain(self.llm),
            "intervention": build_intervention_chain(self.llm),
        }

    async def run(self, task: str, context: dict) -> dict:
        chain = self.chains[task]
        result = await chain.ainvoke(context)
        return result  # already parsed to dict by output parser
```

### Middleware

```python
# middleware/logging.py — add to main.py
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} {response.status_code} {duration:.3f}s")
    return response
```

### Error Handling

All routes wrapped in try/except. Return consistent error shape:
```json
{"error": "description", "code": "ANALYTICS_FAILED", "detail": "..."}
```

Use FastAPI's `HTTPException` for 4xx, generic handler for 500s.

### Async Strategy

- CSV upload + processing: synchronous (small files, <5s acceptable for demo)
- All AI calls: `async` with `await chain.ainvoke()`
- DB queries: synchronous SQLAlchemy (no async ORM needed for SQLite at this scale)

### Response Schema Pattern

```python
# All endpoints return this wrapper
class APIResponse(BaseModel, Generic[T]):
    data: T
    meta: dict = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

---

## 5. DATABASE DESIGN (SQLite)

### Schema

```sql
-- Core user table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    monthly_income REAL,
    salary_day INTEGER,          -- day of month salary arrives
    currency TEXT DEFAULT 'INR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Behavioral profile (updated by AI)
CREATE TABLE behavioral_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    archetype TEXT,              -- 'Stress Spender', 'Planner', etc.
    archetype_confidence REAL,   -- 0.0–1.0
    emotional_trigger TEXT,      -- 'weekend_social', 'late_night', etc.
    spending_pattern TEXT,       -- 'front_loaded', 'end_loaded', 'volatile'
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions (core table)
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT,               -- Food, Transport, Entertainment, etc.
    subcategory TEXT,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_group_id INTEGER,
    emotional_flag BOOLEAN DEFAULT FALSE,  -- weekend / late-night / stress
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_txn_user_date ON transactions(user_id, date);
CREATE INDEX idx_txn_category ON transactions(category);

-- Recurring transaction groups
CREATE TABLE recurring_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    name TEXT,
    avg_amount REAL,
    frequency TEXT,              -- 'monthly', 'weekly', 'daily'
    next_expected_date DATE,
    confidence REAL
);

-- DRS score history
CREATE TABLE drs_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    score REAL NOT NULL,          -- 0–100
    budget_score REAL,
    velocity_score REAL,
    savings_score REAL,
    recurring_score REAL,
    emotional_score REAL,
    salary_gap_score REAL,
    explanation TEXT,             -- AI-generated explanation
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_drs_user ON drs_history(user_id, calculated_at);

-- Risk predictions
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    signal_type TEXT NOT NULL,    -- 'velocity_spike', 'salary_gap', etc.
    severity TEXT,                -- 'low', 'medium', 'high', 'critical'
    score REAL,
    description TEXT,
    predicted_for_date DATE,      -- when the risk will materialize
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI interventions
CREATE TABLE interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    prediction_id INTEGER REFERENCES predictions(id),
    title TEXT NOT NULL,
    action TEXT NOT NULL,         -- what to do
    reason TEXT NOT NULL,         -- why (explainability)
    urgency TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'active', -- active, dismissed, completed
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weekly AI narratives
CREATE TABLE narratives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    week_start DATE,
    narrative_text TEXT NOT NULL,
    key_insights TEXT,            -- JSON array of bullet points
    drs_at_generation REAL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Budget rules
CREATE TABLE budget_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    category TEXT NOT NULL,
    monthly_limit REAL NOT NULL,
    alert_at_percent INTEGER DEFAULT 80  -- alert when 80% spent
);
```

### Key Relationships

- `users` → `transactions` (one-to-many)
- `users` → `drs_history` (one-to-many, ordered by time)
- `users` → `behavioral_profiles` (one-to-one, updated in place)
- `predictions` → `interventions` (one-to-one optional)
- `transactions` → `recurring_patterns` (many-to-one via recurring_group_id)

---

## 6. LANGCHAIN USAGE

### Where LangChain Adds Real Value

**Use it for chains that need structured output parsing + retry logic.**

```python
# ai/chains/intervention_chain.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

class InterventionOutput(BaseModel):
    title: str
    action: str
    reason: str
    urgency: str  # "low" | "medium" | "high"
    savings_potential: float

def build_intervention_chain(llm: ChatOpenAI):
    parser = JsonOutputParser(pydantic_object=InterventionOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", INTERVENTION_SYSTEM_PROMPT),
        ("human", "{context}")
    ])
    return prompt | llm | parser
```

The `| parser` at the end auto-retries on malformed JSON and validates against your Pydantic model. This is the main value of LangChain here.

### Where Direct OpenAI Calls Are Better

The DRS explanation is a single simple call — no chain, no parser needed:

```python
# In drs_service.py
async def generate_explanation(self, score: float, components: dict) -> str:
    client = AsyncOpenAI()
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": EXPLAIN_SYSTEM},
            {"role": "user", "content": f"Score: {score}. Components: {components}"}
        ],
        max_tokens=200
    )
    return response.choices[0].message.content
```

### Prompt Chaining Strategy

Only one chain has multiple steps — the narrative chain:

```
Step 1: Summarize transaction data → compressed context (cheaper input to step 2)
Step 2: Generate narrative from compressed context + archetype

This reduces token cost by ~40% vs passing raw transaction list to the narrative prompt.
```

### Memory

Do NOT use LangChain memory. It adds complexity and the demo is stateless (preloaded data). If a "conversational" feel is needed for demo, fake it with preloaded Q&A pairs.

### What to Skip

- Agents (too slow, too unpredictable for demo)
- Tools / tool-calling via LangChain (use direct OpenAI tool calls if needed)
- VectorStore / embeddings (no RAG needed for this scope)
- LangSmith (nice but not essential for 6 days)

---

## 7. OPENAI INTEGRATION DESIGN

### The 4 OpenAI Use Cases

#### 1. Archetype Classification (once per user or on demand)

```python
ARCHETYPE_SYSTEM = """
You are a behavioral finance expert. Analyze the user's transaction patterns
and classify them into exactly one archetype. Return JSON only.

Archetypes:
- stress_spender: high spend on weekends/evenings, spikes after work events
- impulse_buyer: high variance, frequent small unplanned purchases
- planner: consistent spend, tracks categories, low variance
- social_spender: high F&B and entertainment, correlates with weekends
- anxiety_saver: under-spends budget heavily, hoards cash
- status_seeker: high fashion/electronics spend, aspirational categories

Return: {"archetype": "...", "confidence": 0.0-1.0, "key_signals": ["...", "..."]}
"""
```

**Input**: compressed spending summary (not raw transactions). Max ~800 tokens input.
**Output**: structured JSON, validated by Pydantic.

#### 2. Weekly Narrative Generation

```python
NARRATIVE_SYSTEM = """
You are Artha, a behavioral finance coach who writes warm, insightful weekly
summaries. You address the user by name. You use financial data to tell a story,
not just list numbers. Tone: direct but caring, like a trusted advisor.

Your narrative must:
- Be 3–4 paragraphs
- Start with the most important behavioral insight
- End with one forward-looking suggestion
- Never use the word "budget" more than once
- Mention the user's DRS score and what it means for them specifically
"""
```

**Input**: `{name, archetype, week_summary, drs_score, top_categories, risk_flags}`
**Output**: plain text narrative (no JSON needed here).

#### 3. Intervention Generation

```python
INTERVENTION_SYSTEM = """
You are Artha's intervention engine. Generate a specific, actionable intervention
for a financial risk. Return valid JSON only, no markdown, no explanation.

Schema: {"title": str, "action": str, "reason": str, "urgency": "low|medium|high", 
         "savings_potential": float}

Rules:
- action must be 1 specific thing the user can do today
- reason must explain the behavioral pattern causing this risk
- savings_potential is estimated monthly savings in user's currency
- Do not moralize. Be specific. Be concrete.
"""
```

#### 4. DRS Explanation (direct call, not chain)

Short call, max 200 tokens output. Explain score change in 2 sentences.

### Token Cost Reduction

| Technique | Saving |
|-----------|--------|
| Summarize transactions before passing to LLM | 40–60% |
| Use gpt-4o-mini for classification, gpt-4o for narrative | 80% on classification |
| Set max_tokens to tight limits per task | 20–30% |
| Cache archetype result (only regenerate if data changes significantly) | Per-user savings |
| Use compressed date ranges not raw ISO timestamps | Small but real |

### Avoiding Hallucinations

- Always provide actual numbers in the prompt context — never ask GPT to "estimate" from vague descriptions
- Use `temperature=0.2` for classification tasks, `0.7` for narrative
- Add this to every system prompt: `"If you are uncertain about a specific figure, say so rather than inventing one."`
- Validate all numeric fields from JSON output with Pydantic min/max constraints
- For narrative: provide exact totals so it can't invent spending figures

### Consistent Output Structure

Use `JsonOutputParser` with strict Pydantic models for all structured outputs. If parsing fails, LangChain retries once automatically. If it fails twice, fall back to a hard-coded fallback response (don't crash the demo).

---

## 8. ANALYTICS ENGINE

### Clear Separation

**Rule-based (Python/Pandas) — fast, deterministic:**
- Transaction categorization (regex + keyword matching)
- Recurring transaction detection
- Spending velocity calculation
- Budget limit tracking
- Salary cycle detection
- Overspend flag generation

**AI-generated (OpenAI) — slow, expensive, but qualitatively better:**
- Behavioral archetype labeling
- Narrative generation
- Intervention text
- DRS score explanation

### Spending Velocity

```python
# analytics/velocity.py
def compute_velocity(df: pd.DataFrame, window_days: int = 7) -> pd.Series:
    """Rolling 7-day spend sum, normalized by monthly income."""
    df = df.sort_values('date')
    df['rolling_spend'] = (
        df.set_index('date')['amount']
          .rolling(f'{window_days}D')
          .sum()
          .values
    )
    return df['rolling_spend']

def detect_velocity_spike(df: pd.DataFrame, multiplier: float = 1.8) -> bool:
    """True if current 7-day velocity > 1.8x the historical median."""
    velocity = compute_velocity(df)
    current = velocity.iloc[-1]
    historical_median = velocity.median()
    return current > (historical_median * multiplier)
```

### Recurring Detection

```python
# analytics/recurring.py
def detect_recurring(df: pd.DataFrame) -> list[dict]:
    groups = df.groupby('description')
    recurring = []
    for desc, group in groups:
        if len(group) < 2:
            continue
        group = group.sort_values('date')
        gaps = group['date'].diff().dt.days.dropna()
        avg_gap = gaps.mean()
        std_gap = gaps.std()
        if std_gap < 5:  # consistent interval
            recurring.append({
                "name": desc,
                "avg_amount": group['amount'].mean(),
                "frequency": classify_frequency(avg_gap),
                "next_expected": group['date'].max() + timedelta(days=avg_gap)
            })
    return recurring
```

### Risk Signals

```python
# analytics/risk_signals.py
SIGNALS = {
    "velocity_spike":   {"weight": 0.30, "fn": detect_velocity_spike},
    "salary_gap_risk":  {"weight": 0.25, "fn": detect_salary_gap},
    "budget_overflow":  {"weight": 0.20, "fn": detect_budget_overflow},
    "emotional_spend":  {"weight": 0.15, "fn": detect_emotional_pattern},
    "recurring_miss":   {"weight": 0.10, "fn": detect_missed_recurring},
}

def score_all_signals(data: dict) -> dict:
    scores = {}
    for name, cfg in SIGNALS.items():
        raw = cfg["fn"](data)  # returns 0.0–1.0
        scores[name] = raw * cfg["weight"]
    scores["aggregate"] = sum(scores.values())
    return scores
```

### Emotional Spending Detection

Flag transactions as "emotional" if:
- Occurred between 10pm–2am
- Occurred on Saturday/Sunday AND exceed 2x daily average
- Category is Food/Entertainment AND day-of-week matches user's historical spike day

```python
def flag_emotional(df: pd.DataFrame) -> pd.DataFrame:
    df['hour'] = pd.to_datetime(df['date']).dt.hour
    df['dow'] = pd.to_datetime(df['date']).dt.dayofweek
    daily_avg = df['amount'].mean()
    df['emotional_flag'] = (
        (df['hour'].between(22, 23) | df['hour'].between(0, 2)) |
        ((df['dow'].isin([5, 6])) & (df['amount'] > daily_avg * 2))
    )
    return df
```

### Salary Cycle Analysis

Find the day(s) of month where income spikes. After that, track days since salary to predict "salary gap" risk (running out before next payday).

```python
def detect_salary_day(df: pd.DataFrame) -> int:
    income = df[df['amount'] > 0]  # positive = credit
    day_totals = income.groupby(income['date'].dt.day)['amount'].sum()
    return day_totals.idxmax()  # the day with highest total credits
```

---

## 9. DECISION READINESS SCORE (DRS)

### Definition

The DRS measures how "financially healthy and decision-ready" a person is at this moment. A high DRS means: on-budget, predictable spending, no emerging risks, emotionally stable financially.

### Mathematical Formula

```
DRS = Σ(component_score_i × weight_i) × 100

Components:
  C1 = Budget Adherence Score     weight = 0.25
  C2 = Velocity Stability Score   weight = 0.20
  C3 = Savings Rate Score         weight = 0.20
  C4 = Recurring Coverage Score   weight = 0.15
  C5 = Emotional Spend Score      weight = 0.10
  C6 = Salary Gap Score           weight = 0.10
  
All component scores ∈ [0.0, 1.0]
Final DRS ∈ [0, 100], clamped.
```

### Component Formulas

**C1 — Budget Adherence**
```
For each category with a budget rule:
  usage_ratio = spent / limit
  category_score = max(0, 1 - max(0, usage_ratio - 0.8) / 0.2)
  (starts penalizing at 80%, hits 0 at 100% and beyond)

C1 = mean(category_scores)
```

**C2 — Velocity Stability**
```
cv = rolling_7d_spend.std() / rolling_7d_spend.mean()  # coefficient of variation
C2 = max(0, 1 - cv)  # low variance → high score
```

**C3 — Savings Rate**
```
savings_rate = (monthly_income - monthly_spend) / monthly_income
C3 = min(1.0, max(0, savings_rate / 0.20))  # 20%+ savings = score 1.0
```

**C4 — Recurring Coverage**
```
days_to_salary = salary_day - today.day  (handle month wraparound)
recurring_due = sum of recurring bills due before next salary
available_cash = income - spent_this_cycle
C4 = min(1.0, available_cash / recurring_due) if recurring_due > 0 else 1.0
```

**C5 — Emotional Spend**
```
emotional_ratio = emotional_spend_this_month / total_spend_this_month
C5 = max(0, 1 - emotional_ratio * 3)  # >33% emotional spend → 0
```

**C6 — Salary Gap**
```
pct_month_elapsed = today.day / days_in_month
pct_budget_used = total_spend / monthly_income
gap_pressure = pct_budget_used - pct_month_elapsed
C6 = max(0, 1 - max(0, gap_pressure) * 4)
```

### Score Interpretation

| Range | Label     | Color  | Action |
|-------|-----------|--------|--------|
| 81–100 | Optimal  | Green  | Keep it up, suggest stretch goals |
| 61–80  | Stable   | Teal   | Minor tune-ups suggested |
| 41–60  | Caution  | Amber  | Specific interventions generated |
| 21–40  | Danger   | Orange | Urgent interventions, narrative alert |
| 0–20   | Critical | Red    | Full intervention suite triggered |

### Score Update Logic

- Recalculate on every new transaction batch upload
- Recalculate daily at midnight (via a scheduled endpoint call from the frontend on load)
- Store every recalculation in `drs_history`
- Generate AI explanation only when score changes by ≥ 5 points (cost control)

### Visual Presentation

- Primary: Plotly gauge chart with animated needle
- Secondary: 6-component radar chart (one axis per component)
- Tertiary: DRS history line chart (last 30 days)
- Inline: Numerical DRS in sidebar at all times

---

## 10. DATASET DESIGN

### Personas

#### Persona 1: Riya Sharma (Stress Spender)

```json
{
  "id": 1,
  "name": "Riya Sharma",
  "monthly_income": 85000,
  "salary_day": 1,
  "archetype": "stress_spender",
  "profile": "Software engineer, 28. Spends heavily on weekends after stressful work weeks. Zomato and Swiggy orders spike on Fridays. Regularly hits 90% of food budget by week 3."
}
```

**Transaction patterns:**
- Monthly fixed: rent (22000), gym (800), Netflix (499), Spotify (119)
- Food: ₹1800–4500/week with Friday/Saturday spike (₹3000+ on weekends)
- Weekend Zomato binges: ₹600–900 per order, 3–4x per weekend
- Occasional late-night orders (11pm–1am) flagged as emotional
- DRS: typically 42–55 (Caution zone), dips to 30s by month end

#### Persona 2: Arjun Mehta (Freelancer / Irregular Income)

```json
{
  "id": 2,
  "name": "Arjun Mehta",
  "monthly_income": 120000,
  "salary_day": null,
  "archetype": "impulse_buyer",
  "profile": "Freelance designer, 31. Irregular income — sometimes 150k, sometimes 60k. Spends heavily when projects land, anxious when dry."
}
```

**Transaction patterns:**
- Income: 2–3 irregular credits per month (40k–80k each)
- Electronics/gadgets: occasional large purchases (8k–25k)
- High variance: some weeks ₹8000 total, some weeks ₹40000
- Subscriptions: 7–8 overlapping, some forgotten

#### Persona 3: Priya Nair (High DRS / Planner)

```json
{
  "id": 3,
  "name": "Priya Nair",
  "monthly_income": 95000,
  "salary_day": 5,
  "archetype": "planner",
  "profile": "Finance analyst, 33. Strict budgets per category. Saves 25%+ monthly. DRS typically 78–88."
}
```

### CSV Format

```csv
date,description,amount,type
2024-01-01,SALARY CREDIT,85000,credit
2024-01-02,ZOMATO ORDER,840,debit
2024-01-03,METRO CARD RECHARGE,500,debit
2024-01-05,SWIGGY ORDER,1200,debit
2024-01-06,H&M PURCHASE,3400,debit
2024-01-07,NETFLIX SUBSCRIPTION,499,debit
```

### Transaction Categories (Rule-Based Mapping)

```python
CATEGORY_RULES = {
    "Food & Dining":    ["ZOMATO", "SWIGGY", "RESTAURANT", "CAFE", "DOMINOS", "KFC"],
    "Transport":        ["UBER", "OLA", "METRO", "RAPIDO", "PETROL", "FUEL"],
    "Entertainment":    ["NETFLIX", "PRIME VIDEO", "SPOTIFY", "BOOKMYSHOW", "HOTSTAR"],
    "Shopping":         ["AMAZON", "FLIPKART", "MYNTRA", "H&M", "ZARA", "NYKAA"],
    "Utilities":        ["ELECTRICITY", "WATER", "GAS", "BROADBAND", "WIFI"],
    "Health":           ["PHARMACY", "APOLLO", "DOCTOR", "HOSPITAL", "GYM"],
    "Rent/EMI":         ["RENT", "EMI", "HOME LOAN", "SOCIETY"],
    "Groceries":        ["BIGBASKET", "BLINKIT", "DMART", "ZEPTO", "SUPERMARKET"],
    "Income":           ["SALARY", "CREDIT", "NEFT RECEIVED", "IMPS RECEIVED"],
}
```

### Seeding the Demo Database

```bash
# Run before demo
cd backend
python datasets/seed.py --persona riya  # loads Riya with 90 days of transactions
```

---

## 11. DEMO ARCHITECTURE (90-Second Flow)

### Setup Before Demo

1. Pre-seed Riya Sharma's data (90 days)
2. DRS calculated: currently at 38 (Danger zone, dropping from 55 last week)
3. 2 active interventions pre-generated
4. Weekly narrative pre-generated
5. Browser open to `/dashboard`, full-screen, zoom at 110%

### Screen-by-Screen Script

**0:00–0:15 — Dashboard**

"This is Artha AI, a behavioral finance copilot. The first thing you notice is Riya's Decision Readiness Score — 38 out of 100, in the danger zone. This isn't just a budget tracker. This number measures whether Riya is financially ready to make good decisions right now."

*Action: Point to DRS gauge. Point to red alert banner.*

"Artha has detected a velocity spike — Riya's 7-day spending is 2.3x her historical average. An AI-generated intervention is already waiting."

**0:15–0:30 — Intervention Modal**

*Action: Click the intervention card.*

"Here's what makes Artha different from any budgeting app. It doesn't just say 'you overspent on food.' It identifies that Riya's Friday evening Zomato orders spike 340% after late meetings — a behavioral pattern. And it gives her one specific action: reschedule her grocery delivery to Friday noon, before the craving hits."

*Action: Point to "reason" field — behavioral explanation.*

**0:30–0:50 — Predictions Page**

*Action: Navigate to `/predictions`.*

"Artha predicts risks before they happen. This calendar shows that Riya is on track to hit zero usable balance 6 days before her next salary. It can see her Netflix, gym, and rent hitting in the same 4-day window."

*Action: Click a red date on the calendar. Show risk detail popup.*

**0:50–1:10 — Narrative Page**

*Action: Navigate to `/narrative`.*

"Every week, Artha writes Riya a personal finance story — not a spreadsheet, a narrative. [Read first 2 lines aloud.] This was generated by GPT-4o with Riya's actual spend data, her behavioral archetype, and her DRS trend. It ends with one specific thing she can do differently next week."

*Action: Click "Regenerate" — wait 3s — new narrative appears.*

**1:10–1:30 — DRS Breakdown**

*Action: Navigate to `/drs`.*

"The DRS isn't a black box. Every component is explainable. Riya's savings rate score is 0.82 — good. But her emotional spend score is 0.21 — she's spending 31% of her food budget during emotional triggers. Artha knows this because it flags late-night and weekend-spike transactions automatically."

*Action: Point to radar chart. Point to score history showing the drop from 55 → 38.*

"That's Artha AI. Behavioral intelligence, proactive intervention, explainable AI."

### What Is Real vs. Simulated

| Feature | Reality |
|---------|---------|
| DRS calculation | Real — Python math, live from DB |
| Risk signals | Real — pandas analysis on seeded data |
| Intervention text | Real — GPT-4o generated, stored |
| Narrative text | Real — GPT-4o generated, stored |
| "Regenerate narrative" | Real — live GPT call |
| Transaction CSV upload | Real — works live |
| Archetype classification | Real — GPT-4o |
| Predictive calendar | Real — pandas date math |
| User data | Seeded / fake (Riya persona) |

---

## 12. BUILD ROADMAP (6 DAYS)

### Day 1 — Foundation

**Goal**: Working backend skeleton + database seeded

Morning:
- [ ] FastAPI app scaffold (`main.py`, router structure)
- [ ] SQLAlchemy models (`models.py`)
- [ ] SQLite DB created + `seed.py` writes Riya's data

Afternoon:
- [ ] `/api/transactions` endpoint returning seeded data
- [ ] Basic analytics: categorization, spend-by-category
- [ ] OpenTelemetry + logging setup

Evening:
- [ ] Test all DB queries working
- [ ] Next.js app scaffold (`app/` router, layout, sidebar stub)

**Milestone**: curl `/api/transactions` returns Riya's transactions.

---

### Day 2 — Analytics Engine

**Goal**: All rule-based analytics working end-to-end

Morning:
- [ ] Spending velocity (`analytics/velocity.py`)
- [ ] Recurring detection (`analytics/recurring.py`)
- [ ] Category classifier (regex rules)

Afternoon:
- [ ] Risk signals engine (all 5 signals)
- [ ] DRS calculator (all 6 components)
- [ ] `/api/analytics/summary` and `/api/drs/current` endpoints

Evening:
- [ ] Wire frontend dashboard to real API
- [ ] DRS gauge component with real data

**Milestone**: Dashboard shows real DRS number from actual calculations.

---

### Day 3 — AI Integration

**Goal**: All 4 OpenAI features working

Morning:
- [ ] `AIOrchestrator` class
- [ ] Archetype classification chain + prompt
- [ ] Test archetype on Riya's data

Afternoon:
- [ ] Intervention generation chain + prompt
- [ ] `/api/interventions/generate` endpoint working
- [ ] Narrative generation chain + prompt

Evening:
- [ ] `/api/narrative/generate` endpoint
- [ ] DRS explanation (direct call)
- [ ] Test all 4 AI features end-to-end

**Milestone**: All 4 AI endpoints return real GPT responses.

---

### Day 4 — Frontend Polish

**Goal**: All pages built, charts working

Morning:
- [ ] Transactions page (table + filters)
- [ ] Predictions page + calendar grid
- [ ] Interventions page (cards + modal)

Afternoon:
- [ ] Narrative page
- [ ] DRS breakdown page (radar chart + history line)
- [ ] All Plotly charts: spending bar, DRS gauge, velocity sparkline

Evening:
- [ ] InterventionModal animations
- [ ] Skeleton loaders on all cards
- [ ] RiskAlertBanner logic

**Milestone**: All 6 pages fully functional with real data.

---

### Day 5 — Integration + Edge Cases

**Goal**: End-to-end flow works flawlessly

Morning:
- [ ] CSV upload flow (multipart → process → redirect to dashboard)
- [ ] Onboarding wizard (3 steps)
- [ ] DRS history chart

Afternoon:
- [ ] Error handling on all API endpoints
- [ ] Fallback responses when AI fails
- [ ] Budget rules setup in DB

Evening:
- [ ] Full end-to-end test: seed → calculate → generate → display
- [ ] Fix any broken state on page refresh
- [ ] Performance: all pages load under 2s

**Milestone**: Complete demo flow works without touching the console.

---

### Day 6 — Demo Prep + Polish

**Goal**: Demo-ready, polished, rehearsed

Morning:
- [ ] Finalize `seed.py` with perfect demo data (Riya at DRS 38)
- [ ] Pre-generate all AI content (interventions, narrative, archetype)
- [ ] README with setup instructions

Afternoon:
- [ ] Architecture diagram finalized
- [ ] Presentation slides (5 slides max)
- [ ] Record backup demo video (in case of WiFi issues)

Evening:
- [ ] Rehearse demo 3x — time it
- [ ] Deploy locally, test on clean machine
- [ ] GitHub repo organized and pushed

**Milestone**: Can demo confidently in 90 seconds.

---

## 13. HACKATHON STRATEGY

### What Judges Will Score Hardest (per problem statement)

| Criterion | Your Approach |
|-----------|---------------|
| Categorization accuracy | Show rule-based + GPT fallback. Mention accuracy metric from eval dataset. |
| Budget plan realism | Show budget rules that match Riya's actual income. DRS makes it concrete. |
| Explainability | Every AI output has a "reason" field. DRS breaks into 6 components. |
| Security/privacy | Mention: no API keys in code, dotenv, local SQLite (data never leaves device). |
| UX: alerts + goals | Show risk alert banner, intervention cards, predictive calendar. |

### How to Maximize Perceived Intelligence

1. **Never show raw numbers without context.** Not "₹4200 on food" — "₹4200 on food, 23% above your average, with 60% occurring on weekend evenings."

2. **Make the DRS the hero.** It's a single number that encodes complex analysis. Judges love a single number they can point at.

3. **The "behavioral" angle is your differentiator.** Every other team will show a budget tracker. You show *why* people overspend. Lead with this in your opening sentence.

4. **Interventions feel agentic even if they're not.** A well-timed, specific intervention card that appears automatically feels like the system is "acting." This is the "wow moment."

5. **The regenerate button is magic.** Live GPT call during the demo. Judges can see it's real.

### Mistakes to Avoid

- Don't demo a slow AI call (pre-warm the narrative generation before presenting)
- Don't show an empty state — seed data must be rich and interesting
- Don't explain the tech stack in the demo — explain the user problem
- Don't say "we plan to add X in the future" — only show what works
- Don't apologize for what's missing — redirect to what's impressive

### Features NOT to Build

- Real bank API integration (Plaid/YODLEE) — overkill, not needed for demo
- Multi-user support — single user is fine
- Email/push notifications — UI cards are sufficient
- Mobile app — desktop web is enough
- Custom ML model — GPT-4o is your model
- PDF export / reporting — not in evaluation criteria

### Where to Focus Polish

1. DRS gauge animation (first impression)
2. Intervention card design (most "AI-feeling" component)
3. Narrative page typography (premium feel)
4. Risk alert banner (urgency + clarity)
5. Dashboard load speed (must be instant)

---

## 14. FINAL DELIVERABLES

### GitHub Repo

```
artha-ai/
├── README.md          ← setup, run instructions, architecture summary
├── backend/
├── frontend/
├── datasets/
├── prompts/
└── docs/
    ├── architecture.png
    ├── demo_script.md
    └── drs_formula.md
```

README must include: one-command setup, `.env.example`, architecture diagram embed, and a 3-sentence "What is Artha AI" description.

### Architecture Diagrams Needed

1. System architecture (layer diagram) — included above
2. DRS component breakdown (radar or bar) — build in Plotly
3. AI pipeline flow (which calls go to GPT vs Python) — simple flowchart

### Presentation Slides (5 slides max)

1. **Problem** — "People don't know where their money goes. But the real problem is they don't know *why*."
2. **Solution** — Artha AI: behavioral finance copilot with 4 capabilities
3. **Architecture** — system diagram + tech stack callouts
4. **Demo screenshots** — DRS gauge, intervention card, narrative, prediction calendar
5. **Evaluation** — accuracy metrics from golden dataset, DRS formula, explainability approach

### Demo Script

See §11 above. Practice until you can do it in 85 seconds. Leave 5 seconds of buffer.

### Evaluation Strategy

```json
// evaluation/golden_dataset.json
[
  {
    "input": "Zomato, Swiggy, restaurant transactions comprising 40% of spend",
    "expected_archetype": "stress_spender",
    "acceptable": ["stress_spender", "social_spender"]
  },
  {
    "input": "DRS 35, velocity spike, salary gap risk",
    "expected_intervention_urgency": "high",
    "intervention_must_contain": ["specific action", "behavioral reason"]
  }
]
```

Run `python evaluation/runner.py` — prints pass/fail + accuracy score. Mention this in your presentation: "We evaluated our prompts against a golden dataset of 20 scenarios."

### Testing Checklist

- [ ] CSV upload → transactions appear in table
- [ ] DRS calculated correctly for all 3 personas (verify by hand)
- [ ] Archetype classified correctly for Riya (stress_spender)
- [ ] Intervention generated and stored for velocity spike risk
- [ ] Narrative generated and readable
- [ ] All 6 pages load without errors
- [ ] DRS gauge animates on load
- [ ] Intervention modal opens and closes
- [ ] Prediction calendar shows red dates
- [ ] No hard-coded API keys in any file
- [ ] Demo seed runs clean on fresh DB
- [ ] App runs with `uvicorn main:app` + `next dev` with no config changes

---

*Artha AI — Built for Hackathon #47: Personal Finance Copilot*
*Stack: FastAPI · Next.js · OpenAI GPT-4o · LangChain · SQLite · Plotly · OTel*
