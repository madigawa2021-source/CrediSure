# CrediSure Parse AI — Workflow Design

## PDF Extraction
Use pdfplumber for digital PDFs, pytesseract fallback for scanned.

## Transaction Structure
Each transaction normalized to:
{date, description, amount, type, balance}

## Categorization
Keyword dictionary (60-70% coverage) + LLM prompt engineering for remainder.
Categories: salary, food, transport, utilities, loan_repayment, entertainment, transfer.

## Approach: Prompt Engineering
Chosen over fine-tuning (no labeled data yet) and RAG (classification not retrieval).

## Cost Reduction
1. Keyword pre-filter before any LLM call
2. Batch 50 transactions per API call
3. Cache results by transaction description
