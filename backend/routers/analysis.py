from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from utils.auth import get_current_user
from models.models import User, UploadedDocument
import pdfplumber
from google import genai
import os
import io
import re
from datetime import datetime

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter(prefix="/analysis", tags=["AI Analysis"])


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        pdf = pdfplumber.open(io.BytesIO(file_bytes))
        full_text = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
        pdf.close()
        return "\n".join(full_text)
    except Exception:
        return ""


def parse_transactions(text: str) -> list[dict]:
    transactions = []
    # Regex pattern to match: date (dd/mm or dd-mm-yyyy), description, amount
    pattern = re.compile(
        r"(\d{1,2}[/-]\d{1,2}[/-]?\d{0,4})\s+(.*?)\s+([\d,]+\.?\d{0,2})"
    )
    lines = text.split("\n")
    for line in lines:
        line_lower = line.lower()
        match = pattern.search(line)
        if match:
            date = match.group(1)
            description = match.group(2).strip()
            amount_str = match.group(3).replace(",", "")
            try:
                amount = float(amount_str)
                trans_type = "credit" if any(
                    keyword in line_lower for keyword in ["cr", "credit", "deposit"]
                ) else "debit"
                transactions.append({
                    "date": date,
                    "description": description,
                    "amount": amount,
                    "type": trans_type
                })
            except ValueError:
                continue
    return transactions


def categorize_transactions(transactions: list[dict]) -> dict:
    keywords = {
        "salary": ["salary", "wages", "payroll", "income", "payment from"],
        "food": ["shoprite", "spar", "chicken republic", "food", "restaurant",
                 "eatery", "kfc", "mcdonalds", "pizza"],
        "transport": ["uber", "bolt", "taxify", "transport", "fuel", "petrol",
                      "filling station"],
        "utilities": ["dstv", "gotv", "electricity", "nepa", "ekedc", "ikedc",
                      "water", "internet", "mtn", "airtel", "glo", "9mobile"],
        "loan_repayment": ["loan", "repayment", "emi", "installment", "mortgage"],
        "entertainment": ["cinema", "netflix", "spotify", "club", "bar", "hotel"]
    }

    categorized = []
    summary = {
        "salary": 0.0,
        "food": 0.0,
        "transport": 0.0,
        "utilities": 0.0,
        "loan_repayment": 0.0,
        "entertainment": 0.0,
        "other": 0.0
    }

    for transaction in transactions:
        desc_lower = transaction["description"].lower()
        category = "other"
        for cat, words in keywords.items():
            if any(word in desc_lower for word in words):
                category = cat
                break
        transaction["category"] = category
        categorized.append(transaction)
        summary[category] += transaction["amount"]

    return {
        "categorized": categorized,
        "summary": summary
    }


@router.post("/analyze-statement")
async def analyze_statement(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)

    if not text:
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from PDF"
        )

    transactions = parse_transactions(text)
    categorized = categorize_transactions(transactions)

    risk_summary = ""
    status = "partial"

    try:
        prompt = f"""
        You are a financial risk analyst. Analyze this bank statement data and
        provide a concise risk summary.

        Extracted transactions: {len(transactions)} transactions found
        Spending categories: {categorized['summary']}

        Based on this data provide:
        1. Overall financial health assessment (2 sentences)
        2. Top spending categories and what they indicate (2-3 sentences)
        3. Risk level: Low / Medium / High with one sentence justification
        4. One practical recommendation for improving creditworthiness

        Keep the entire response under 200 words. Be specific and professional.
        """
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        risk_summary = response.text
        status = "success"
    except Exception as e:
        print(f"Gemini error: {e}")
        risk_summary = None

    return {
        "transactions_found": len(transactions),
        "categories": categorized["summary"],
        "categorized_transactions": categorized["categorized"][:10],
        "risk_summary": risk_summary,
        "status": status
    }
