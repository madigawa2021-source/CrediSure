from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import engine, Base
from routers import auth, assessment, upload

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CrediSure API",
    description="Credit Intelligence Platform API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(assessment.router)
app.include_router(upload.router)


@app.get("/")
def root():
    return {"message": "CrediSure API is running", "version": "1.0.0"}
