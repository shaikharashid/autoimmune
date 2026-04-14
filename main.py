from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from schemas import PatientData
from model import predict
from pdf_parser import extract_text_from_pdf, extract_lab_values
from database import init_db, get_db, ReportHistory
from auth import (
    create_user, get_user, verify_password,
    create_access_token, verify_token
)
from datetime import datetime

app = FastAPI(
    title="ImmunoAI Backend",
    description="Autoimmune Disease Detection API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE"],
    allow_headers=["*"],
)

# Initialize database on startup
init_db()

security = HTTPBearer()

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return email

@app.get("/")
def home():
    return {"status": "ImmunoAI backend is running! ✅"}

@app.post("/register")
def register(data: RegisterRequest):
    user = create_user(data.email, data.password, data.name)
    if not user:
        raise HTTPException(status_code=400, detail="Email already registered")
    token = create_access_token(data.email)
    return {"token": token, "name": user["name"], "email": user["email"]}

@app.post("/login")
def login(data: LoginRequest):
    user = get_user(data.email)
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(data.email)
    return {"token": token, "name": user["name"], "email": user["email"]}

@app.post("/predict")
def get_prediction(
    data: PatientData,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = predict(data.dict())

    # Save to database
    entry = ReportHistory(
        user_email=email,
        disease=result["disease"],
        confidence=result["confidence"],
        date=datetime.now().strftime("%b %d, %Y")
    )
    db.add(entry)
    db.commit()

    return result

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    pdf_bytes = await file.read()
    text = extract_text_from_pdf(pdf_bytes)
    lab_values = extract_lab_values(text)
    result = predict(lab_values)
    result["extracted_values"] = lab_values

    # Save to database
    entry = ReportHistory(
        user_email=email,
        disease=result["disease"],
        confidence=result["confidence"],
        date=datetime.now().strftime("%b %d, %Y")
    )
    db.add(entry)
    db.commit()

    return result

@app.get("/history")
def get_history(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reports = db.query(ReportHistory)\
        .filter(ReportHistory.user_email == email)\
        .order_by(ReportHistory.created_at.desc())\
        .limit(20)\
        .all()

    return [
        {
            "id": str(r.id),
            "disease": r.disease,
            "confidence": r.confidence,
            "date": r.date
        }
        for r in reports
    ]

@app.delete("/history/{report_id}")
def delete_history(
    report_id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = db.query(ReportHistory)\
        .filter(ReportHistory.id == report_id, ReportHistory.user_email == email)\
        .first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully"}

@app.delete("/history")
def clear_history(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(ReportHistory)\
        .filter(ReportHistory.user_email == email)\
        .delete()
    db.commit()
    return {"message": "History cleared successfully"}