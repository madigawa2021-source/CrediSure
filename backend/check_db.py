from database.connection import SessionLocal
from models.models import CreditAssessment, User

db = SessionLocal()

users = db.query(User).all()
print("=== USERS ===")
for u in users:
    print(f"id={u.id} email={u.email}")

assessments = db.query(CreditAssessment).all()
print("\n=== ASSESSMENTS ===")
for a in assessments:
    print(f"user_id={a.user_id} score={a.credit_score} rating={a.rating}")

db.close()