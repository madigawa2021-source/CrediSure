# CrediSure Parse AI — Workflow Design

## Overview
CrediSure uses an integrated AI pipeline that combines PDF upload 
and bank statement analysis into a single endpoint. Users upload 
once and receive a complete credit assessment with AI risk summary.

## Merged Pipeline Flow

User uploads PDF bank statement

↓

## FILE STORAGE

Save PDF to uploads/ folder (local) / S3 (production)

Save metadata to uploaded_documents table

↓

## TEXT EXTRACTION

pdfplumber reads PDF bytes

Extracts text from every page

Fallback: pytesseract OCR for scanned PDFs

↓

## TRANSACTION PARSING

Regex identifies transaction lines

Pattern: date + description + amount + CR/DR indicator

Output: list of {date, description, amount, type} objects

↓

## SPENDING CATEGORIZATION

Keyword dictionary classifies each transaction:

- salary: ["salary", "wages", "payroll", "income"]
- food: ["shoprite", "spar", "kfc", "restaurant"]
- transport: ["uber", "bolt", "fuel", "petrol"]
- utilities: ["dstv", "mtn", "airtel", "electricity"]
- loan_repayment: ["loan", "repayment", "emi"]
- entertainment: ["netflix", "cinema", "spotify"]

Covers 60–70% of Nigerian bank transactions by keyword alone

↓

## FINANCIAL CALCULATION

- income = sum of all credit/salary transactions  
- expenses = sum of all debit transactions  
- loans = sum of loan_repayment transactions  

These feed directly into the credit scoring formula

↓

## CREDIT SCORING

score = 300 base  
+ savings_rate × 300  
- debt_to_income × 200  
+ income_tier_bonus (50–150)

Clamped to 300–850 range (FICO standard)

↓

## AI RISK SUMMARY (Gemini)

Prompt includes: transaction count, category totals

Returns:
- financial health assessment  
- spending behavior analysis  
- risk level  
- recommendation  

Model: gemini-3.1-flash-lite-preview

↓

## UNIFIED RESPONSE

{
  credit_score,
  rating,
  risk_level,
  transactions_found,
  categories,
  risk_summary,
  document_id
}

---

## Technology Choices

### Why Prompt Engineering over Fine-tuning or RAG?
- Fine-tuning: requires thousands of labeled Nigerian transaction examples — data we don't have yet
- RAG: designed for knowledge retrieval, not classification tasks
- Prompt Engineering: flexible, fast to iterate, works immediately, produces structured JSON output reliably

### Why pdfplumber?
- Preserves layout and column structure of bank statements
- Handles digital PDFs natively
- Lightweight, no server-side dependencies

### Cost Reduction Strategy
1. Keyword pre-filter handles 60–70% of transactions before any LLM call — reduces AI costs significantly
2. Batch transactions into single prompt (50 per call vs 1)
3. Cache results by transaction description using Redis
4. Use lightweight model (flash) instead of heavyweight (pro/ultra)

## Endpoint

POST /upload/upload-statement

- Accepts: PDF file (multipart/form-data)
- Auth: Bearer JWT token required
- Returns: full analysis result in a single response
- Processing time: 5–15 seconds depending on statement size