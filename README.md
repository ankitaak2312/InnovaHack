# PhishGuard — Phishing & Malicious URL Detector

**InnovaHack Chapter-1 | Domain: Cybersecurity | Problem Statement 2**

PhishGuard is a browser extension that analyzes the URL of the page you're currently viewing and returns a real-time risk score, flagging phishing attempts using a combination of rule-based heuristics and a trained machine learning classifier — with a plain-English explanation of *why* a link was flagged.

**Live API:** https://innovahack-8q1t.onrender.com
**Live API docs (Swagger UI):** https://innovahack-8q1t.onrender.com/docs

> Note: the API runs on a free-tier instance that spins down after inactivity. The first request after idle time can take 30–50 seconds to wake up — this is expected, not a bug.

---

## The Problem

Phishing remains one of the most common entry points for cyberattacks, and most people have no quick way to tell whether a link is safe before clicking. Traditional blocklists only catch known bad URLs and miss new or slightly-varied attacks.

## Our Approach

Instead of relying on a static blocklist, PhishGuard combines two independent signals into one score:

1. **Heuristics engine** — checks the URL's structure directly for known red flags (no ML needed to catch these):
   - IP address used instead of a domain name
   - Missing HTTPS
   - Excessive number of subdomains
   - Suspicious keywords (`login`, `verify`, `secure`, `banking`, `urgent`, `suspended`, etc.)

2. **ML classifier (Random Forest)** — trained on a synthetic dataset of safe vs. phishing-style URLs, using 12 numeric features per URL (length, dot/hyphen/digit counts, subdomain count, IP usage, HTTPS presence, `@` symbol presence, suspicious keyword count, shortener detection, path length, query param count). This catches subtler patterns that fixed rules alone would miss.

The two scores are blended 50/50 into a single 0–100 risk score, bucketed into **Safe / Warning / Phishing**, and paired with a short, human-readable explanation of the top reasons behind the score.

```
combined_score = 0.5 × heuristic_score + 0.5 × ml_confidence
```

## Architecture

```
┌─────────────────────┐        POST /analyze         ┌──────────────────────────┐
│  Chrome Extension    │ ────────────────────────────▶│   FastAPI Backend        │
│  (Manifest V3)       │        { url }                │   (Render, Docker)       │
│                      │◀──────────────────────────── │                          │
│  popup.html/js/css   │   { risk_score, risk_level,   │  ┌────────────────────┐  │
│  background.js       │     explanation, flags }      │  │ heuristics.py      │  │
└─────────────────────┘                               │  └────────────────────┘  │
                                                        │  ┌────────────────────┐  │
                                                        │  │ ml/ (RandomForest) │  │
                                                        │  └────────────────────┘  │
                                                        └──────────────────────────┘
```

**Flow:**
1. User clicks "Scan Current Tab" in the extension popup.
2. `background.js` grabs the active tab's URL and POSTs it to `/analyze`.
3. The backend runs both the heuristics module and the ML model on the URL, blends the scores, and returns a risk level + explanation.
4. `popup.js` renders a color-coded gauge (green/yellow/red) and the explanation text.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI, Pydantic, Uvicorn |
| ML | Scikit-learn (Random Forest), Pandas, Joblib |
| Frontend | Chrome Extension (Manifest V3), vanilla JS, TailwindCSS/custom CSS |
| Deployment | Docker, Render |

## Project Structure

```
InnovaHack-main/
├── backend/
│   ├── main.py              # FastAPI app, /analyze endpoint, score blending
│   ├── heuristics.py         # Rule-based structural red-flag checks
│   ├── model.pkl              # Trained Random Forest bundle (model + feature names)
│   ├── ml/
│   │   ├── features.py       # Shared feature extraction (training + live API)
│   │   ├── generate_dataset.py  # Synthetic safe/phishing URL dataset generator
│   │   └── train_model.py    # Trains and saves the classifier
│   ├── Dockerfile
│   └── requirements.txt
├── extension/
│   ├── manifest.json         # Manifest V3 config, permissions
│   ├── background.js         # Service worker: fetches active tab URL, calls API
│   ├── popup.html / popup.js / popup.css  # UI: scan button, gauge, explanation
│   └── icons/
└── requirements.txt
```

## Running Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
# API available at http://localhost:8000, docs at http://localhost:8000/docs
```

To retrain the model from scratch:
```bash
cd backend
python -m ml.train_model
```

### Extension
1. Open `chrome://extensions` (or `edge://extensions`)
2. Enable **Developer mode**
3. Click **Load unpacked** and select the `extension/` folder
4. Click the PhishGuard icon on any tab and hit **Scan Current Tab**

By default the extension points at the deployed Render API. To test against a local backend instead, update `API_BASE_URL` in `background.js` and `host_permissions` in `manifest.json` to `http://localhost:8000/*`.

## API Reference

### `POST /analyze`
**Request:**
```json
{ "url": "http://secure-paypal-login.tk/confirm" }
```

**Response:**
```json
{
  "url": "http://secure-paypal-login.tk/confirm",
  "risk_score": 87.5,
  "risk_level": "phishing",
  "heuristic_score": 75.0,
  "ml_score": 100.0,
  "flags": [
    "URL does not use HTTPS",
    "URL contains suspicious keywords: login, secure, confirm"
  ],
  "explanation": "Flagged as phishing because it does not use HTTPS and contains suspicious keywords: login, secure, confirm."
}
```

### `GET /health`
Basic liveness check, returns `{ "status": "ok" }`.

## Known Limitations & Next Steps

- The ML model is trained on a **synthetic dataset** (structurally generated, not real crawled phishing data). Swapping in a real labeled dataset (e.g. PhishTank + Tranco top sites) is the natural next step and requires no changes outside `generate_dataset.py`.
- CORS is currently open (`allow_origins=["*"]`) for hackathon convenience; a production version would restrict this to the extension's origin.
- Currently scans URLs only; the problem statement also mentions email scanning as a stretch goal, which is a natural extension via a Gmail/Outlook add-in reusing the same `/analyze` endpoint.
- Free-tier hosting means occasional cold-start delays (30–50s) on first use after idle time.

## Team

- Team Name: *Invictus*
- Team Leader: *Sanjana Baid*
- Team Members: *Ankita Kumari, Sanjana Baid*
- Track / Problem Statement: Domain 2 — Cybersecurity, Problem Statement 2 (Phishing & Malicious URL Detector)
