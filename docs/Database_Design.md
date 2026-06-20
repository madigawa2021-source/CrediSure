# CrediSure — Database Design

## ER Diagram

```mermaid
erDiagram
  USERS {
    int id PK
    string full_name
    string email
    string password_hash
    string phone
    enum role
    timestamp created_at
  }

  KYC_RECORDS {
    int id PK
    int user_id FK
    string bvn
    string nin
    string address
    enum status
    timestamp verified_at
  }

  BUSINESSES {
    int id PK
    int user_id FK
    string business_name
    string rc_number
    string industry
    timestamp created_at
  }

  CREDIT_ASSESSMENTS {
    int id PK
    int user_id FK
    float monthly_income
    float monthly_expense
    float existing_loans
    int credit_score
    string rating
    string risk_level
    timestamp assessed_at
  }

  UPLOADED_DOCUMENTS {
    int id PK
    int user_id FK
    string file_name
    string s3_key
    string file_type
    enum status
    timestamp uploaded_at
  }

  LOAN_APPLICATIONS {
    int id PK
    int user_id FK
    int assessment_id FK
    float amount_requested
    string purpose
    enum status
    timestamp applied_at
  }

  USERS ||--o{ KYC_RECORDS : has
  USERS ||--o{ BUSINESSES : owns
  USERS ||--o{ CREDIT_ASSESSMENTS : receives
  USERS ||--o{ UPLOADED_DOCUMENTS : uploads
  USERS ||--o{ LOAN_APPLICATIONS : applies
  CREDIT_ASSESSMENTS ||--o{ LOAN_APPLICATIONS : supports