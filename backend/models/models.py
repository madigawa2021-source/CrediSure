from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(String(50), default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    kyc_records = relationship("KYCRecord", back_populates="user")
    businesses = relationship("Business", back_populates="user")
    credit_assessments = relationship("CreditAssessment", back_populates="user")
    uploaded_documents = relationship("UploadedDocument", back_populates="user")
    loan_applications = relationship("LoanApplication", back_populates="user")


class KYCRecord(Base):
    __tablename__ = "kyc_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bvn = Column(String(20))
    nin = Column(String(20))
    address = Column(Text)
    status = Column(String(50), default="pending")
    verified_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="kyc_records")


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_name = Column(String(255), nullable=False)
    rc_number = Column(String(50))
    industry = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="businesses")


class CreditAssessment(Base):
    __tablename__ = "credit_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    monthly_income = Column(Float)
    monthly_expense = Column(Float)
    existing_loans = Column(Float)
    credit_score = Column(Integer)
    rating = Column(String(10))
    risk_level = Column(String(20))
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="credit_assessments")
    loan_applications = relationship("LoanApplication", back_populates="assessment")


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    s3_key = Column(String(255), nullable=False)
    file_type = Column(String(50))
    status = Column(String(50), default="pending")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="uploaded_documents")


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("credit_assessments.id"))
    amount_requested = Column(Float, nullable=False)
    purpose = Column(Text)
    status = Column(String(50), default="pending")
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="loan_applications")
    assessment = relationship("CreditAssessment", back_populates="loan_applications")
