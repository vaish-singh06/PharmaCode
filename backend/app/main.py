from fastapi import FastAPI
from app.routes.analyze import router as analyze_router
from app.routes.report import router as report_router   # ⭐ ADD THIS
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="PharmaGuard API")

app.include_router(analyze_router, prefix="/analyze")
app.include_router(report_router, prefix="/report")   # ⭐ ADD THIS

@app.get("/")
def root():
    return {"message": "PharmaGuard running"}

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "PharmaGuard"}

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
