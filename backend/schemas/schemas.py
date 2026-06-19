from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class AssessmentInput(BaseModel):
    monthly_income: float
    monthly_expense: float
    existing_loans: float


class AssessmentOutput(BaseModel):
    credit_score: int
    rating: str
    risk_level: str


class UploadResponse(BaseModel):
    file_name: str
    status: str
    message: str
