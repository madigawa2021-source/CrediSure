# CrediSure — Credit Intelligence Platform

A full stack credit assessment platform built with Next.js,
FastAPI, and AI-powered bank statement analysis.

## Live Demo
- Frontend: [Deploy link here]
- API Docs: [Deploy link here]/docs

## GitHub
`https://github.com/madigawa2021-source/CrediSure`

## Tech Stack
- Frontend: Next.js 14, TypeScript, Tailwind CSS
- Backend: FastAPI, Python, SQLAlchemy, JWT Auth
- Database: MySQL (SQLite for development)
- Storage: AWS S3
- AI: pdfplumber, LLM prompt engineering (GPT-4o/Gemini)
- Cloud: AWS ECS, RDS, S3, CloudWatch

## Project Structure
credisure/
├── backend/        # FastAPI Python backend
├── frontend/       # Next.js TypeScript frontend
├── database/       # MySQL schema and migrations
├── docs/           # Architecture diagrams
└── README.md

## Setup Instructions

### Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload

### Frontend
cd frontend
npm install
npm run dev

## API Endpoints
- POST /auth/register — Register new user
- POST /auth/login — Login, returns JWT token
- POST /assessment/ — Calculate credit score (authenticated)
- POST /upload/upload-statement — Upload PDF bank statement

## Credit Scoring Formula
Score = 300 base
+ savings_rate × 300 (rewards living below means)
- debt_to_income × 200 (penalizes overleveraged borrowers)
+ income_tier_bonus (50–150 based on income bracket)
Range: 300–850 (mirrors FICO standard)

## Architecture
See docs/architecture.png for full system diagram.
