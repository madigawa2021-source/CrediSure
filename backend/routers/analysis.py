from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from utils.auth import get_current_user
from models.models import (
    User,
    UploadedDocument,
    CreditAssessment,
)
import pdfplumber
import google.genai as genai
import os
import io
import re
import json
from uuid import uuid4

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

                trans_type = (
                    "credit"
                    if any(
                        keyword in line_lower
                        for keyword in ["cr", "credit", "deposit"]
                    )
                    else "debit"
                )

                transactions.append(
                    {
                        "date": date,
                        "description": description,
                        "amount": amount,
                        "type": trans_type,
                    }
                )

            except ValueError:
                continue

    return transactions


def gemini_extract_transactions(text: str) -> list[dict]:
    """
    Fallback extraction using Gemini when regex fails.
    """

    try:
        prompt = f"""
You are a bank statement parser.

Extract all transactions from this statement.

Return ONLY valid JSON.

Format:

[
  {{
    "date": "string",
    "description": "string",
    "amount": number,
    "type": "credit" or "debit"
  }}
]

Statement:

{text}
"""

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt,
        )

        result = response.text.strip()

        # Remove markdown fences if present
        result = result.replace("```json", "")
        result = result.replace("```", "").strip()

        transactions = json.loads(result)

        cleaned = []

        for t in transactions:
            cleaned.append(
                {
                    "date": t.get("date", ""),
                    "description": t.get("description", ""),
                    "amount": float(t.get("amount", 0)),
                    "type": str(t.get("type", "debit")).lower(),
                }
            )

        return cleaned

    except Exception as e:
        print("Gemini extraction error:", e)
        return []


def categorize_transactions(transactions: list[dict]) -> dict:
    keywords = {
        "salary": [
            "salary",
            "wages",
            "payroll",
            "income",
            "payment from",
        ],
        "food": [
            "shoprite",
            "spar",
            "chicken republic",
            "food",
            "restaurant",
            "eatery",
            "kfc",
            "mcdonalds",
            "pizza",
        ],
        "transport": [
            "uber",
            "bolt",
            "taxify",
            "transport",
            "fuel",
            "petrol",
            "filling station",
        ],
        "utilities": [
            "dstv",
            "gotv",
            "electricity",
            "nepa",
            "ekedc",
            "ikedc",
            "water",
            "internet",
            "mtn",
            "airtel",
            "glo",
            "9mobile",
        ],
        "loan_repayment": [
            "loan",
            "repayment",
            "emi",
            "installment",
            "mortgage",
        ],
        "entertainment": [
            "cinema",
            "netflix",
            "spotify",
            "club",
            "bar",
            "hotel",
        ],
    }

    categorized = []

    summary = {
        "salary": 0.0,
        "food": 0.0,
        "transport": 0.0,
        "utilities": 0.0,
        "loan_repayment": 0.0,
        "entertainment": 0.0,
        "other": 0.0,
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
        "summary": summary,
    }


def calculate_credit_score(
    monthly_income,
    monthly_expense,
    existing_loans,
):
    savings_rate = (
        (monthly_income - monthly_expense) / monthly_income
        if monthly_income > 0
        else 0
    )

    debt_to_income = (
        existing_loans / monthly_income
        if monthly_income > 0
        else 1
    )

    score = 300

    score += max(0, savings_rate * 300)

    score -= min(200, debt_to_income * 200)

    if monthly_income >= 500000:
        score += 150
    elif monthly_income >= 200000:
        score += 100
    elif monthly_income >= 100000:
        score += 50

    score = max(300, min(850, int(score)))

    if score >= 750:
        rating = "Excellent"
        risk = "Very Low Risk"

    elif score >= 650:
        rating = "Very Good"
        risk = "Low Risk"

    elif score >= 550:
        rating = "Good"
        risk = "Medium Risk"

    elif score >= 450:
        rating = "Fair"
        risk = "High Risk"

    else:
        rating = "Poor"
        risk = "Very High Risk"

    return score, rating, risk


@router.post("/analyze-statement")
async def analyze_statement(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    file_bytes = await file.read()

    text = extract_text_from_pdf(file_bytes)

    if not text:
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from PDF",
        )

    # Save metadata immediately
    s3_key = f"{uuid4()}-{file.filename}"

    document = UploadedDocument(
        user_id=current_user.id,
        file_name=file.filename,
        s3_key=s3_key,
        file_type="pdf",
        status="processing",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Primary extraction: Regex
    transactions = parse_transactions(text)

    extraction_method = "regex"

    # Fallback: Gemini
    if len(transactions) < 3:
        gemini_transactions = gemini_extract_transactions(text)

        if gemini_transactions:
            transactions = gemini_transactions
            extraction_method = "gemini"

    categorized = categorize_transactions(transactions)

    # Financial metrics
    monthly_income = sum(
        t["amount"]
        for t in transactions
        if t["type"] == "credit"
    )

    monthly_expense = sum(
        t["amount"]
        for t in transactions
        if t["type"] == "debit"
    )

    existing_loans = sum(
        t["amount"]
        for t in categorized["categorized"]
        if t["category"] == "loan_repayment"
    )

    # Credit scoring
    credit_score, rating, risk_level = calculate_credit_score(
        monthly_income,
        monthly_expense,
        existing_loans,
    )

    # Save assessment
    assessment = CreditAssessment(
        user_id=current_user.id,
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        existing_loans=existing_loans,
        credit_score=credit_score,
        rating=rating,
        risk_level=risk_level,
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    # Gemini narrative summary
    risk_summary = None

    try:
        prompt = f"""
You are a financial risk analyst.

Credit Score: {credit_score}
Rating: {rating}
Risk Level: {risk_level}

Income: {monthly_income}
Expenses: {monthly_expense}
Loan Repayments: {existing_loans}

Category Breakdown:
{categorized['summary']}

Provide:

1. Financial health assessment (2 sentences)
2. Top spending categories and implications
3. Risk explanation
4. One practical recommendation

Keep under 200 words.
"""

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt,
        )

        risk_summary = response.text

    except Exception as e:
        print("Gemini summary error:", e)

    document.status = "completed"

    db.commit()

    return {
        "file_name": document.file_name,
        "uploaded_at": str(document.uploaded_at),
        "status": document.status,

        "transactions_found": len(transactions),
        "extraction_method": extraction_method,

        "financial_metrics": {
            "monthly_income": monthly_income,
            "monthly_expense": monthly_expense,
            "existing_loans": existing_loans,
        },

        "credit_assessment": {
            "credit_score": credit_score,
            "rating": rating,
            "risk_level": risk_level,
        },

        "categories": categorized["summary"],

        "categorized_transactions":
            categorized["categorized"][:10],

        "risk_summary": risk_summary,
    }
