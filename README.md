# CrediSure — Credit Intelligence Platform

[![Live Frontend](https://img.shields.io/badge/Frontend-credi--sure.vercel.app-blue)](https://credi-sure.vercel.app)
[![Live API](https://img.shields.io/badge/API-credisure--api.onrender.com-green)](https://credisure-api.onrender.com/docs)
[![GitHub](https://img.shields.io/badge/GitHub-madigawa2021--source%2FCrediSure-black)](https://github.com/madigawa2021-source/CrediSure)

## Overview

CrediSure is a fully functional, deployed credit intelligence platform. Users register, upload bank statements, and receive AI-powered credit scores with professional risk analysis — all in a single workflow. The platform mirrors real-world fintech products: stateless JWT authentication, a FICO-aligned credit scoring engine, and a two-stage AI pipeline that combines a keyword prefilter with a Gemini LLM fallback.

**All six parts of the technical assessment are complete and live.**

---

## Live Demo

| Resource | URL |
|----------|-----|
| Frontend | https://credi-sure.vercel.app |
| API Documentation | https://credisure-api.onrender.com/docs |
| GitHub Repository | https://github.com/madigawa2021-source/CrediSure |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14 + TypeScript | SSR, routing, UI |
| Styling | Tailwind CSS | Utility-first responsive design + dark mode |
| Backend | FastAPI + Python | REST API, business logic |
| Validation | Pydantic v2 | Request/response schema validation |
| ORM | SQLAlchemy | Database abstraction layer |
| Auth | JWT (python-jose) + bcrypt | Stateless authentication |
| AI Extraction | pdfplumber | PDF text extraction preserving layout |
| AI Categorization | Keyword dict + Gemini fallback | Transaction categorization |
| AI Summary | google-genai (gemini-3.1-flash-lite-preview) | Professional risk narrative |
| Database | SQLite (dev) / MySQL (prod) | Structured data storage |
| File Storage | AWS S3 (designed) / local (dev) | PDF document storage |
| Deployment | Vercel + Render | Frontend + backend hosting |

---

## Project Structure

```
credisure/
├── backend/
│   ├── main.py                  # FastAPI app, CORS, router registration
│   ├── requirements.txt
│   ├── render.yaml              # Render deployment config
│   ├── database/
│   │   └── connection.py        # SQLAlchemy engine + get_db()
│   ├── models/
│   │   └── models.py            # SQLAlchemy ORM models (all 6 tables)
│   ├── schemas/
│   │   └── schemas.py           # Pydantic v2 schemas
│   ├── routers/
│   │   ├── auth.py              # POST /auth/register, POST /auth/login
│   │   ├── assessment.py        # POST /assessment/, GET /assessment/latest
│   │   ├── upload.py            # POST /upload/upload-statement
│   │   └── analysis.py          # POST /analysis/analyze-statement (full AI pipeline)
│   └── utils/
│       └── auth.py              # bcrypt hashing, JWT creation/verification
├── frontend/
│   └── app/
│       ├── layout.tsx
│       ├── page.tsx             # Landing/redirect
│       ├── login/page.tsx       # Login with password validation
│       ├── register/page.tsx    # Register with email regex validation
│       ├── dashboard/page.tsx   # Score display + dark mode toggle
│       ├── assessment/page.tsx  # Manual score calculator
│       ├── upload/page.tsx      # PDF upload
│       └── analysis/page.tsx    # Full AI analysis results
├── database/
│   └── schema.sql               # MySQL CREATE TABLE statements for all 6 tables
└── docs/
    ├── credisure_system_architecture.png
    ├── Database_Design.md       # ER diagram (Mermaid)
    ├── AI_Workflow.md           # AI engineering Q&A
    └── aws_architecture.md      # AWS production architecture design
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /auth/register | No | Accept UserCreate schema, bcrypt hash password, save user |
| POST | /auth/login | No | Verify credentials, return `{access_token, token_type}` |
| GET | /assessment/latest | JWT | Return most recent credit assessment for current user |
| POST | /assessment/ | JWT | Run scoring formula, save to DB, return score |
| POST | /upload/upload-statement | JWT | Accept PDF, save metadata to uploaded_documents |
| POST | /analysis/analyze-statement | JWT | Full AI pipeline — extract, parse, categorize, score, summarize |

### POST /assessment/ — Input & Output

**Request:**
```json
{
  "monthly_income": 500000,
  "monthly_expense": 250000,
  "existing_loans": 50000
}
```

**Response:**
```json
{
  "credit_score": 780,
  "rating": "Very Good",
  "risk_level": "Low Risk"
}
```

---

## Credit Scoring Algorithm

The scoring engine mirrors FICO methodology using three financially meaningful signals:

```python
savings_rate   = (monthly_income - monthly_expense) / monthly_income
debt_to_income = existing_loans / monthly_income if monthly_income > 0 else 1

score  = 300                              # FICO-aligned base floor
score += max(0, savings_rate * 300)       # rewards living below means
score -= min(200, debt_to_income * 200)   # penalizes over-leverage

# Income tier bonus — reflects repayment capacity
if   monthly_income >= 500000: score += 150
elif monthly_income >= 200000: score += 100
elif monthly_income >= 100000: score +=  50

score = max(300, min(850, int(score)))    # clamp to FICO range
```

### Rating Scale

| Score Range | Rating | Risk Level | Funding Readiness |
|-------------|--------|------------|-------------------|
| 750 – 850 | Excellent | Very Low Risk | ✅ Ready for Funding |
| 650 – 749 | Very Good | Low Risk | ✅ Ready for Funding |
| 550 – 649 | Good | Medium Risk | ⚠️ Needs Improvement |
| 450 – 549 | Fair | High Risk | ⚠️ Needs Improvement |
| 300 – 449 | Poor | Very High Risk | ❌ Not Ready |

---

## AI Pipeline

The full pipeline runs on a single POST /analysis/analyze-statement call:

1. **Extract** — `pdfplumber` opens PDF bytes and extracts text page-by-page, preserving column and table layout
2. **Parse** — Regex engine (`parse_transactions()`) isolates transaction lines: date + description + amount + CR/DR
3. **Fallback** — If regex finds fewer than 3 transactions, `gemini_extract_transactions()` sends raw text to Gemini with a JSON-only prompt
4. **Categorize** — `categorize_transactions()` runs keyword dictionary first (zero LLM cost), LLM only for ambiguous descriptions
5. **Aggregate** — Financial totals: `income = sum(credits)`, `expenses = sum(debits)`, `loans = sum(loan_repayment amounts)`
6. **Score** — Credit scoring formula runs on real extracted figures, saved to `credit_assessments`
7. **Summarize** — Gemini generates a professional risk narrative (<200 words): health assessment + spending analysis + recommendation
8. **Return** — `{credit_score, rating, risk_level, transactions_found, extraction_method, financial_metrics, categories, risk_summary}`

### Transaction Categories

Keyword dictionary covers 60–70% of Nigerian bank transactions at zero LLM cost:

| Category | Keywords |
|----------|---------|
| salary | salary, wages, payroll, income, payment from |
| food | shoprite, spar, chicken republic, kfc, pizza, restaurant |
| transport | uber, bolt, taxify, fuel, petrol, filling station |
| utilities | mtn, airtel, glo, 9mobile, dstv, gotv, electricity, nepa, internet |
| loan_repayment | loan, repayment, emi, installment, mortgage |
| entertainment | netflix, spotify, cinema, club, bar, hotel |
| other | anything not matched above |

### Why Prompt Engineering over Fine-Tuning or RAG?

- **Fine-tuning rejected** — requires thousands of labeled Nigerian transaction examples that don't exist yet; slow to iterate
- **RAG rejected** — designed for knowledge retrieval, not classification; adds complexity with no benefit here
- **Prompt engineering chosen** — works immediately with zero training data; updating categories takes minutes not days; produces structured JSON reliably

### AI Cost Reduction Strategies

| Strategy | Implementation | Impact |
|----------|---------------|--------|
| Keyword prefilter | Dictionary runs before any LLM call | 60-70% of transactions never hit the LLM |
| Dual-path extraction | Regex primary, Gemini only as fallback | Most PDFs parsed without LLM |
| Lightweight model | gemini-3.1-flash-lite-preview | ~10x cheaper than Pro models |
| Output constraint | "Keep under 200 words" in summary prompt | Caps token usage per call |
| Result caching (prod) | Redis keyed by transaction description | Identical descriptions never call LLM twice |

---

## Database Schema

Six tables with CASCADE DELETE relationships. Full SQL in `database/schema.sql`.

| Table | Purpose |
|-------|---------|
| users | Accounts: full_name, email, password_hash, phone, role |
| kyc_records | KYC: BVN, NIN, address, status, verified_at |
| businesses | Business profile: name, RC number, industry |
| credit_assessments | Score history: income, expense, loans, credit_score, rating, risk_level |
| uploaded_documents | File metadata: file_name, s3_key, file_type, status |
| loan_applications | Funding requests linked to a specific assessment_id |

**Key decisions:**
- `CASCADE DELETE` on all FKs — no orphaned rows when a user is deleted
- `credit_assessments` stores every score over time — enables trend analysis
- `uploaded_documents` stores only the `s3_key`, never binary data — DB stays lightweight
- `loan_applications.assessment_id` creates a full audit trail per funding decision

---

## Bonus Features

| Feature | Status | Details |
|---------|--------|---------|
| Dark Mode | ✅ Implemented | Toggle in dashboard navbar. Persists in localStorage. Tailwind `dark:` classes throughout. |
| Form Validation | ✅ Implemented | Email regex in register. Password min 6 chars in login. Inline red error messages block API calls. |

---

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and fill in your values (see Environment Variables below)
uvicorn main:app --reload
# API runs at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local (see Environment Variables below)
npm run dev
# App runs at http://localhost:3000
```

### Environment Variables

**Backend — `backend/.env`:**

```env
DATABASE_URL=sqlite:///./credisure.db
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY=your-gemini-api-key
```

**Frontend — `frontend/.env.local`:**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Database Initialization

SQLAlchemy auto-creates all tables on startup via:
```python
Base.metadata.create_all(bind=engine)  # in main.py
```

For MySQL in production, set `DATABASE_URL=mysql+pymysql://user:pass@host/dbname` — no other code changes needed.

To apply the raw SQL schema manually:
```bash
mysql -u root -p credisure_db < database/schema.sql
```

---

## Deployment

### Backend — Render

Configured via `render.yaml` in the repository.

```bash
# Render auto-deploys from GitHub main branch
# Set these environment variables in the Render dashboard:
# DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, GEMINI_API_KEY
```

Manual deploy:
```bash
# From the backend/ directory
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend — Vercel

```bash
# Install Vercel CLI
npm install -g vercel

cd frontend
vercel --prod
# Set NEXT_PUBLIC_API_URL to your Render backend URL in Vercel dashboard
```

### AWS Production Architecture (Design)

| Component | Service | Config |
|-----------|---------|--------|
| Frontend | AWS Amplify / Vercel | Global CDN, auto-deploy, HTTPS via ACM |
| Backend | AWS ECS Fargate | Containerized FastAPI, auto-scales on CPU/memory |
| Database | AWS RDS MySQL | Multi-AZ, daily backups, 7-day retention, private subnet |
| Storage | AWS S3 | Private bucket, pre-signed URLs (15-min expiry) |
| Load Balancer | AWS ALB | HTTPS termination, health checks |
| Monitoring | AWS CloudWatch | Logs, metrics, error rate alarms |
| Secrets | AWS Secrets Manager | All credentials injected at runtime |
| Network | AWS VPC | Private subnets for RDS/ECS, public subnet for ALB only |

Full design in `docs/aws_architecture.md`.

---

## Architecture

System architecture diagram: `docs/credisure_system_architecture.png`

Layers: Client (Next.js) → API Gateway (FastAPI/CORS) → Auth Service (JWT/bcrypt) → Backend (business logic + scoring) → Database (MySQL/SQLAlchemy) + File Storage (S3) → AI Layer (pdfplumber + Gemini) → Cloud Infrastructure (AWS ECS + RDS + S3 + CloudWatch)

**Why Layered MVC?** Evaluated monolithic (brittle at scale) and microservices (unnecessary complexity). Layered MVC gives each component a single job — independently testable, scalable, and maintainable.

---

## Candidate

| | |
|--|--|
| **Name** | Abdullahi Uba Madigawa |
| **Email** | abdullahiubaaliyu1234@gmail.com |
| **Phone** | +234 907 208 9052 |
| **GitHub** | [github.com/Madigawa2021-source](https://github.com/Madigawa2021-source) |
| **LinkedIn** | [linkedin.com/in/abdullahi-uba-madigawa-bb421b368](https://linkedin.com/in/abdullahi-uba-madigawa-bb421b368) |
