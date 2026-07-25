import os

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from heuristics import run_heuristics
from ml.features import extract_features

app = FastAPI(
    title="Phishing & Malicious URL Detector API",
    description="Backend service that analyzes URLs using heuristics + ML to detect phishing attempts",
    version="0.1.0",
)

# Allow the browser extension (running from any origin) to call this API during development.
# Tighten this list once you deploy and know your extension's origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
_model_bundle = joblib.load(MODEL_PATH)
_ml_model = _model_bundle["model"]

# How much each component contributes to the final 0-100 risk score.
HEURISTIC_WEIGHT = 0.5
ML_WEIGHT = 0.5


class AnalyzeRequest(BaseModel):
    url: str = Field(..., min_length=1, examples=["http://secure-paypal-login.tk/confirm"])


class AnalyzeResponse(BaseModel):
    url: str
    risk_score: float
    risk_level: str
    heuristic_score: float
    ml_score: float
    flags: list[str]


def _risk_level(score: float) -> str:
    if score < 30:
        return "safe"
    if score < 60:
        return "warning"
    return "phishing"


@app.get("/")
def root():
    return {"message": "Phishing Detector API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_url(payload: AnalyzeRequest):
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="url must not be empty")

    heuristic_result = run_heuristics(url)
    heuristic_score = float(heuristic_result["heuristic_score"])

    features = [extract_features(url)]
    ml_score = float(_ml_model.predict_proba(features)[0][1] * 100)

    combined_score = (HEURISTIC_WEIGHT * heuristic_score) + (ML_WEIGHT * ml_score)
    combined_score = round(min(max(combined_score, 0), 100), 2)

    return AnalyzeResponse(
        url=url,
        risk_score=combined_score,
        risk_level=_risk_level(combined_score),
        heuristic_score=heuristic_score,
        ml_score=round(ml_score, 2),
        flags=heuristic_result["flags"],
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)