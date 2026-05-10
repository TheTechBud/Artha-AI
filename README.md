# Artha AI — Behavioral Finance Copilot

AI-powered financial behavior analysis. Analyzes transactions, calculates a Decision Readiness Score (DRS), predicts risky spending patterns, and generates interventions and narratives.

---

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Frontend    | Next.js 14 (App Router), TypeScript |
| Styling     | Tailwind CSS                        |
| Charts      | Plotly.js + react-plotly.js         |
| Data fetch  | TanStack React Query                |
| Backend     | Python FastAPI                      |
| AI          | Google Gemini (AI Studio) + LangChain (light) |
| Database    | SQLite via SQLAlchemy               |
| Analytics   | pandas + numpy                      |
| Logging     | Python logging + OpenTelemetry      |

---

## Project Structure

```
artha-ai/
├── backend/
│   ├── main.py                  ← FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── api/
│   │   ├── routes/
│   │   │   ├── transactions.py  ← Upload & list endpoints
│   │   │   ├── analytics.py     ← Summary, velocity, recurring
│   │   │   ├── drs.py           ← DRS current, history, recalculate
│   │   │   ├── interventions.py ← Generate & dismiss interventions
│   │   │   ├── narrative.py     ← Weekly narrative generation
│   │   │   └── ai.py            ← Archetype, risks, calendar
│   │   └── middleware/
│   │       ├── logging.py
│   │       └── error_handler.py
│   ├── db/
│   │   ├── database.py          ← SQLAlchemy engine + session
│   │   ├── models.py            ← All ORM models
│   │   └── crud.py              ← DB read/write operations
│   ├── schemas/                 ← Pydantic request/response models
│   ├── services/
│   │   ├── drs_service.py       ← DRS calculation orchestration
│   │   ├── transaction_service.py ← CSV upload pipeline
│   │   ├── analytics_service.py
│   │   ├── intervention_service.py
│   │   └── narrative_service.py
│   ├── analytics/
│   │   ├── engine.py            ← Main analytics engine (pandas)
│   │   ├── velocity.py          ← 7-day rolling spend
│   │   ├── recurring.py         ← Recurring transaction detection
│   │   ├── risk_signals.py      ← 5 risk signal scorers
│   │   ├── budget_tracker.py    ← Budget adherence scoring
│   │   └── salary_cycle.py      ← Salary gap + emotional spend
│   ├── ai/
│   │   ├── orchestrator.py      ← Main AI entry point
│   │   ├── chains/              ← LangChain chains
│   │   └── prompts/             ← Prompt templates
│   ├── utils/
│   │   ├── constants.py         ← Category rules, DRS weights
│   │   ├── date_utils.py
│   │   └── formatting.py
│   ├── observability/
│   │   ├── logger.py
│   │   └── otel_setup.py
│   └── evaluation/
│       └── runner.py            ← Prompt accuracy evals
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           ← Root layout with sidebar
│   │   ├── globals.css
│   │   ├── dashboard/page.tsx   ← Main overview
│   │   ├── drs/page.tsx         ← DRS detail + history
│   │   ├── transactions/page.tsx ← Table + CSV upload
│   │   ├── predictions/page.tsx ← Risk signals + calendar
│   │   ├── interventions/page.tsx ← AI interventions
│   │   ├── narrative/page.tsx   ← Weekly narrative + archetype
│   │   └── onboarding/page.tsx  ← First-run upload flow
│   ├── components/
│   │   ├── layout/              ← Sidebar, PageWrapper
│   │   ├── charts/              ← DRSGauge, SpendingChart, Pie, Velocity
│   │   ├── cards/               ← DRSCard, InterventionCard, NarrativeCard
│   │   └── ui/                  ← Badge, Skeleton
│   ├── hooks/                   ← useDRS, useTransactions, useInterventions
│   ├── lib/                     ← api.ts, utils.ts, providers.tsx
│   └── types/index.ts           ← All TypeScript interfaces
│
├── datasets/
│   ├── seed.py                  ← Demo data loader
│   └── transactions/
│       └── riya_transactions.csv ← 3-month demo dataset
│
└── Makefile
```

---

## Quick Start

### 1. Clone and configure environment

```bash
git clone <your-repo>
cd artha-ai

# Copy and fill in your Google AI Studio API key (Gemini)
cp backend/.env.example backend/.env
# Edit backend/.env: set GOOGLE_API_KEY=... (https://aistudio.google.com/apikey)
```

### 2. Install dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 3. Initialize database and seed demo data

```bash
cd backend
python ../datasets/seed.py --persona riya
```

This will:
- Create `backend/db/artha.db`
- Create demo user Riya Sharma (monthly income: ₹85,000)
- Import 3 months of realistic transaction data
- Set budget rules per category
- Calculate an initial DRS score

### 4. Start the backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API explorer: http://localhost:8000/docs

### 5. Start the frontend

```bash
cd frontend
npm run dev
```

App: http://localhost:3000 (redirects to `/dashboard`)

---

## What Works After First Boot

| Feature                      | Status   |
|------------------------------|----------|
| Transaction list + upload    | ✅ Working |
| Spending by category         | ✅ Working |
| 7-day velocity chart         | ✅ Working |
| Recurring bill detection     | ✅ Working |
| DRS calculation              | ✅ Working |
| DRS component breakdown      | ✅ Working |
| Risk signal scoring          | ✅ Working |
| Risk calendar                | ✅ Working |
| Sidebar navigation           | ✅ Working |
| AI interventions             | ✅ Full with GOOGLE_API_KEY · graceful fallback without |
| Weekly narrative             | ✅ Full with GOOGLE_API_KEY · graceful fallback without |
| Archetype classification     | ✅ Full with GOOGLE_API_KEY · graceful fallback without |
| DRS explanation              | ✅ Full with GOOGLE_API_KEY · graceful fallback without |
| Prompt evaluations           | ✅ Full with GOOGLE_API_KEY · graceful fallback without |

---

## Key API Endpoints

```
GET  /health                         Health check
GET  /api/drs/current                Latest DRS score + components
GET  /api/drs/history?days=30        Historical DRS trend
POST /api/drs/recalculate            Recalculate from latest data

GET  /api/analytics/summary          Spend breakdown, velocity, recurring
GET  /api/analytics/velocity         7-day rolling spend time series
GET  /api/analytics/recurring        Detected recurring transactions

POST /api/transactions/upload        Upload CSV file
GET  /api/transactions               Paginated transaction list

GET  /api/ai/archetype               Behavioral archetype classification
GET  /api/ai/risks                   5-signal risk score report
GET  /api/ai/predictions/calendar    Month-view calendar with risk flags

GET  /api/interventions              Active interventions
POST /api/interventions/generate     Generate AI intervention
PATCH /api/interventions/{id}/dismiss Dismiss intervention

GET  /api/narrative/latest           Latest weekly narrative
POST /api/narrative/generate         Generate new narrative
```

---

## DRS Formula

```
DRS = Σ (component_score × weight) × 100

Components:
  budget_adherence    × 0.25   How well spend stays within limits
  velocity_stability  × 0.20   Consistency of spend pace (low CV = better)
  savings_rate        × 0.20   (income − spend) / income, target 20%
  recurring_coverage  × 0.15   Available cash vs upcoming bills
  emotional_spend     × 0.10   Lower emotional spend fraction = better
  salary_gap          × 0.10   Spend pace vs month elapsed

Score bands:
  81–100 → Optimal
  61–80  → Stable
  41–60  → Caution
  21–40  → Danger
  0–20   → Critical
```

---

## CSV Upload Format

```csv
date,description,amount,type
2025-05-01,SALARY CREDIT,85000,credit
2025-05-02,ZOMATO ORDER,840,debit
2025-05-03,NETFLIX SUBSCRIPTION,499,debit
```

- `date`: Any of `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`
- `amount`: Positive number (sign derived from `type`)
- `type`: `debit` or `credit` (optional, defaults to `debit`)

---

## What to Build Next

1. **Budget management UI** — CRUD screen for category limits
2. **Multi-month analytics** — Month-over-month comparison charts
3. **Archetype persistence** — Auto-reclassify on new transaction upload
4. **DRS explanation UI** — Display AI explanation when score changes >5 pts
5. **Notification system** — Trigger intervention generation when risk > threshold
6. **Export feature** — Download DRS report as PDF
7. **Multi-user support** — Replace `USER_ID=1` with auth sessions

---

## Makefile Commands

```bash
make install      # Install all dependencies
make seed         # Load Riya's demo data
make seed-reset   # Wipe DB and re-seed
make backend      # Start FastAPI (port 8000)
make frontend     # Start Next.js (port 3000)
make eval         # Run prompt evaluation suite
make clean        # Clear pycache and DB files
```
