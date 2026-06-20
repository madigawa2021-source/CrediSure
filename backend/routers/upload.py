from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from models.models import User, UploadedDocument, CreditAssessment
from utils.auth import get_current_user
from routers.analysis import (
    extract_text_from_pdf,
    parse_transactions,
    gemini_extract_transactions,
    categorize_transactions,
    calculate_credit_score,
    client,
)
from uuid import uuid4
import os

router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post("/upload-statement")
async def upload_statement(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    # Read file bytes
    file_bytes = await file.read()

    # Save metadata to DB immediately
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

    # Extract text from PDF
    text = extract_text_from_pdf(file_bytes)

    if not text:
        document.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from PDF",
        )

    # Parse transactions — regex first, Gemini fallback
    transactions = parse_transactions(text)
    extraction_method = "regex"

    if len(transactions) < 3:
        gemini_transactions = gemini_extract_transactions(text)
        if gemini_transactions:
            transactions = gemini_transactions
            extraction_method = "gemini"

    # Categorize spending
    categorized = categorize_transactions(transactions)

    # Calculate financial totals from real extracted data
    monthly_income = sum(
        t["amount"] for t in transactions if t["type"] == "credit"
    )
    monthly_expense = sum(
        t["amount"] for t in transactions if t["type"] == "debit"
    )
    existing_loans = sum(
        t["amount"]
        for t in categorized["categorized"]
        if t["category"] == "loan_repayment"
    )

    # Run credit scoring formula
    credit_score, rating, risk_level = calculate_credit_score(
        monthly_income, monthly_expense, existing_loans
    )

    # Save credit assessment to database
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

    # Generate Gemini risk summary
    risk_summary = None
    try:
        prompt = f"""
You are a financial risk analyst. Analyze this bank statement data.

Credit Score: {credit_score}
Rating: {rating}
Risk Level: {risk_level}
Monthly Income: {monthly_income}
Monthly Expenses: {monthly_expense}
Loan Repayments: {existing_loans}
Category Breakdown: {categorized['summary']}

Provide:
1. Financial health assessment (2 sentences)
2. Top spending categories and implications (2-3 sentences)
3. Risk level explanation (1 sentence)
4. One practical recommendation for improving creditworthiness

Keep under 200 words. Be specific and professional.
"""
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt,
        )
        risk_summary = response.text

    except Exception as e:
        print("Gemini summary error:", e)

    # Update document status
    document.status = "completed"
    db.commit()

    return {
        "file_name": file.filename,
        "status": "completed",
        "message": "Statement uploaded and analyzed successfully",
        "uploaded_at": str(document.uploaded_at),
        "extraction_method": extraction_method,
        "transactions_found": len(transactions),
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
        "categorized_transactions": categorized["categorized"][:10],
        "risk_summary": risk_summary,
    }