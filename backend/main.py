from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/")
def root():
    return {"message": "Phishing Detector API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
