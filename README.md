# CrediSure — Credit Intelligence Platform

## Overview

CrediSure is a full stack credit assessment platform that allows
users to register, upload bank statements, receive AI-powered
credit scores, and apply for funding.

## Live Demo

* Frontend: [CrediSure Frontend](https://credi-sure.vercel.app?utm_source=chatgpt.com)
* API Documentation: [CrediSure API Docs](https://credisure-api.onrender.com/docs?utm_source=chatgpt.com)
* GitHub: [CrediSure GitHub Repository](https://github.com/madigawa2021-source/CrediSure?utm_source=chatgpt.com)

## Tech Stack

| Layer      | Technology              | Purpose                         |
| ---------- | ----------------------- | ------------------------------- |
| Frontend   | Next.js 14 + TypeScript | SSR, routing, UI                |
| Styling    | Tailwind CSS            | Utility-first responsive design |
| Backend    | FastAPI + Python        | REST API, business logic        |
| Validation | Pydantic v2             | Request/response validation     |
| ORM        | SQLAlchemy              | Database abstraction layer      |
| Auth       | JWT (python-jose)       | Stateless authentication        |
| AI         | pdfplumber + Gemini     | PDF extraction + risk analysis  |
| Database   | MySQL / SQLite          | Structured data storage         |
| Storage    | AWS S3 (designed)       | PDF document storage            |
| Deployment | Vercel + Render         | Frontend + backend hosting      |

## Project Structure

```
credisure/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── database/connection.py
│   ├── models/models.py
│   ├── schemas/schemas.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── assessment.py
│   │   ├── upload.py
│   │   └── analysis.py
│   └── utils/auth.py
├── frontend/
│   └── app/
│       ├── login/
│       ├── register/
│       ├── dashboard/
│       ├── assessment/
│       └── upload/
├── database/
│   └── schema.sql
└── docs/
    └── architecture.png
```

## API Endpoints

| Method | Endpoint                 | Auth | Description                               |
| ------ | ------------------------ | ---- | ----------------------------------------- |
| POST   | /auth/register           | No   | Register new user                         |
| POST   | /auth/login              | No   | Login, returns JWT token                  |
| GET    | /assessment/latest       | Yes  | Get user's latest credit score            |
| POST   | /assessment/             | Yes  | Calculate credit score                    |
| POST   | /upload/upload-statement | Yes  | Upload PDF, run AI analysis, return score |

## Credit Scoring Algorithm

Score formula:

```
Score = 300 base
+ savings_rate × 300 (rewards living below means)
- debt_to_income × 200 (penalizes overleveraged borrowers)
+ income_tier_bonus (50-150 based on income bracket)
```

Range: 300–850 (mirrors FICO standard)

Rating scale:

| Score Range | Rating    | Risk Level     |
| ----------- | --------- | -------------- |
| 750–850     | Excellent | Very Low Risk  |
| 650–749     | Very Good | Low Risk       |
| 550–649     | Good      | Medium Risk    |
| 450–549     | Fair      | High Risk      |
| 300–449     | Poor      | Very High Risk |

## AI Pipeline

1. User uploads PDF bank statement
2. pdfplumber extracts text from PDF
3. Regex parser identifies transactions
4. Keyword dictionary categorizes spending
5. Income/expense/loan totals calculated from real data
6. Credit scoring formula runs on extracted numbers
7. Gemini generates professional risk summary
8. Full results returned: score + categories + risk summary

## Local Setup

### Prerequisites

* Python 3.10+
* Node.js 18+
* Git

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
uvicorn main:app --reload
# API runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:3000
```

### Environment Variables

Backend (.env):

```
DATABASE_URL=sqlite:///./credisure.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY=your-gemini-key
```

Frontend (.env.local):

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

Backend: Deployed on Render

* Auto-deploys from GitHub main branch
* Environment variables set in Render dashboard
* [https://render.com](https://render.com)

Frontend: Deployed on Vercel

* Auto-deploys from GitHub main branch
* NEXT_PUBLIC_API_URL points to Render backend
* [https://vercel.com](https://vercel.com)

## Database Schema

Full schema in `database/schema.sql`

Tables:

* users
* kyc_records
* businesses
* credit_assessments
* uploaded_documents
* loan_applications

## Candidate

Name: Abdullahi Uba Madigawa
Email: [abdullahiubaaliyu1234@gmail.com](mailto:abdullahiubaaliyu1234@gmail.com)
GitHub: [GitHub Profile](https://github.com/Madigawa2021-source?utm_source=chatgpt.com)
LinkedIn: [LinkedIn Profile](https://linkedin.com/in/abdullahi-uba-madigawa-bb421b368?utm_source=chatgpt.com)
