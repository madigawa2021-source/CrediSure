from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from models.models import User, CreditAssessment
from schemas.schemas import AssessmentInput, AssessmentOutput
from utils.auth import get_current_user

router = APIRouter(prefix="/assessment", tags=["Credit Assessment"])


def calculate_credit_score(monthly_income, monthly_expense, existing_loans):
    savings_rate = (monthly_income - monthly_expense) / monthly_income
    debt_to_income = existing_loans / monthly_income if monthly_income > 0 else 1
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
        rating, risk = "Excellent", "Very Low Risk"
    elif score >= 650:
        rating, risk = "Very Good", "Low Risk"
    elif score >= 550:
        rating, risk = "Good", "Medium Risk"
    elif score >= 450:
        rating, risk = "Fair", "High Risk"
    else:
        rating, risk = "Poor", "Very High Risk"
    return score, rating, risk


@router.post("/", response_model=AssessmentOutput)
def create_assessment(
    data: AssessmentInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    score, rating, risk = calculate_credit_score(
        data.monthly_income,
        data.monthly_expense,
        data.existing_loans
    )
    new_assessment = CreditAssessment(
        user_id=current_user.id,
        monthly_income=data.monthly_income,
        monthly_expense=data.monthly_expense,
        existing_loans=data.existing_loans,
        credit_score=score,
        rating=rating,
        risk_level=risk
    )
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)
    return {
        "credit_score": score,
        "rating": rating,
        "risk_level": risk
    }
