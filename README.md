# ParkWise Command Center

**ParkWise Command Center** is an AI-powered parking and congestion intelligence platform designed to help traffic enforcement teams identify parking-induced congestion hotspots, predict future risk, allocate officers, and generate optimized patrol routes.

The system uses real traffic violation data, geospatial hotspot detection, risk scoring, machine learning forecasting, officer allocation logic, and patrol routing to support data-driven field enforcement.

---

## Overview

Illegal parking and spillover parking near commercial areas, metro stations, transit points, and busy roads can reduce carriageway capacity and create localized congestion. Traditional enforcement is mostly patrol-based and reactive.

ParkWise solves this by converting historical violation records into actionable enforcement intelligence:

* Detects parking violation hotspots
* Computes risk scores for each hotspot
* Forecasts future hotspot risk using ML
* Allocates enforcement officers based on risk priority
* Generates patrol route sequences for field deployment
* Displays everything in a command-center dashboard

---

## Key Features

### 1. Command Dashboard

The dashboard provides a city-wide overview of:

* Total violations analyzed
* Priority/high-risk zones
* Officers deployed/on duty
* Average risk score
* Bengaluru command map
* Risk distribution
* Top priority hotspots

The dashboard uses API-backed data and focuses on priority hotspots for clear operational visibility.

---

### 2. Hotspot Intelligence

The Hotspots page allows users to inspect detected parking-congestion clusters.

Features:

* Spatial hotspot map
* Ranked hotspot records
* Search and filtering
* Top-N hotspot display
* Risk badges
* Violation count, dominant violation, vehicle type, active days, and coordinates

Hotspots are generated from the uploaded traffic violation dataset.

---

### 3. Risk Score Breakdown

The Risk Score page explains why a hotspot is risky.

The risk score is based on components such as:

* Frequency
* Recurrence
* Density
* Temporal risk
* Severity
* Exposure

It helps enforcement teams understand why a specific hotspot is prioritized.

---

### 4. Forecast Intelligence

The Forecast page uses a LightGBM model to predict future hotspot risk.

Current trained model metrics:

* Model type: LightGBM
* Training mode: Cross-sectional hotspot-level training
* Rows used: 5,872
* Train size: 4,404
* Validation size: 1,468
* MAE: 3.30
* R²: 0.87

Recommended UI wording:

* Forecast Reliability: 87%
* Average Error: ±3.30 risk-score points

The model predicts continuous risk scores, so R² and MAE are used instead of classification accuracy.

---

### 5. Officer Allocation

The Officer Allocation module distributes enforcement officers across priority hotspots based on risk.

Features:

* Adjustable officer count
* Adjustable target hotspot count
* Backend-driven allocation
* Officer deployment plan
* Risk-tier badges
* Allocation summary

Allocations are generated from real hotspot/risk data, not from the original CSV directly.

---

### 6. Patrol Route Planning

The Patrol page generates route sequences for allocated hotspots.

Features:

* Patrol stop sequence
* Route map visualization
* Priority stop ordering
* Distance and estimated dispatch duration
* Route recalculation support

Patrol routes are generated recommendations based on the processed hotspot and allocation data.

---

## Data Pipeline

The platform follows this processing flow:

```text
Raw violation CSV
        ↓
Violation ingestion
        ↓
Hotspot generation
        ↓
Enriched violation generation
        ↓
Temporal analysis
        ↓
EIS / Risk score computation
        ↓
Forecast model training
        ↓
Forecast generation
        ↓
Officer allocation
        ↓
Patrol route generation
```

---

## Current Data Status

The system has been tested with the uploaded violation dataset:

```text
Raw violations loaded:       298,450
Detected hotspots:           5,872
Risk/EIS score rows:         5,872
Forecast rows:               5,872
Allocation recommendations:  103
Patrol route rows:           10
```

Forecasts, allocations, and patrol routes are generated outputs based on the real violation dataset.

---

## Tech Stack

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* Recharts
* Lucide Icons
* Map visualization components
* Axios/API service layer

### Backend

* FastAPI
* SQLAlchemy
* PostgreSQL
* PostGIS
* Alembic
* LightGBM
* Pandas / NumPy
* Scikit-learn

### Database

* PostgreSQL with PostGIS extension
* Dockerized PostGIS container

---

## Project Structure

```text
parkwise-backend/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── alembic/
│   ├── scripts/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── data/
│   │   ├── hooks/
│   │   ├── layout/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   ├── utils/
│   │   └── router.tsx
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── README.md
└── .gitignore
```

---

## Backend Setup

### 1. Start PostgreSQL/PostGIS

```bash
docker start parkwise-postgres
```

Verify it is running:

```bash
docker ps
```

Expected port mapping:

```text
0.0.0.0:5433->5432/tcp
```

If the container does not exist, create it:

```bash
docker run --name parkwise-postgres ^
  -e POSTGRES_USER=postgres ^
  -e POSTGRES_PASSWORD=postgres ^
  -e POSTGRES_DB=parkwise ^
  -p 5433:5432 ^
  -d postgis/postgis:16-3.4
```

---

### 2. Configure Backend Environment

Create or update:

```text
backend/.env
```

Use:

```env
SECRET_KEY=parkwise-super-secret-key-for-development-2026
DEBUG=true

DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/parkwise
TEST_DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/parkwise

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=parkwise
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
```

---

### 3. Install Backend Dependencies

```bash
cd backend
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

If virtual environment does not exist:

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

---

### 4. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

---

### 5. Start Backend Server

```bash
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend runs at:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

## Frontend Setup

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

---

### 2. Configure Frontend Environment

Create or update:

```text
frontend/.env
```

Use:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

---

### 3. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

---

### 4. Build Frontend

```bash
cd frontend
npm run build
```

---

## Dataset Setup

The dataset is not committed to GitHub.

Place the traffic violation CSV inside a local `data/` folder.

Example:

```text
backend/data/jan to may police violation_anonymized791b166.csv
```

Then run the ingestion script if needed:

```bash
cd backend
python scripts/load_violations.py "data/jan to may police violation_anonymized791b166.csv"
```

---

## Backend Pipeline Execution

After loading violations, run the backend pipelines in this order.

### 1. Generate Hotspots

Use Swagger or API:

```text
POST /api/v1/hotspots/run-pipeline
```

Expected output:

```text
violations_read: 298450
hotspots_created: 5872
enriched_violations_created: 298450
```

---

### 2. Run Temporal Analysis

```text
POST /api/v1/temporal/run-pipeline
```

Expected output:

```text
peak_windows_created: 13032
```

---

### 3. Compute EIS / Risk Scores

```text
POST /api/v1/eis/run-pipeline
```

Expected output:

```text
eis_scores_created: 5872
```

---

### 4. Train Forecast Model

```text
POST /api/v1/forecast/train
```

Use request body:

```json
{
  "horizon_days": 1,
  "hotspot_id": null,
  "model_version": "forecast-v1-h1",
  "min_history_per_hotspot": 1
}
```

Expected response:

```json
{
  "status": "trained",
  "horizon_days": 1,
  "model_version": "forecast-v1-h1",
  "model_type": "lightgbm",
  "training_mode": "cross_sectional",
  "rows_used": 5872,
  "train_size": 4404,
  "validation_size": 1468,
  "mae": 3.3045,
  "r2": 0.8699
}
```

---

### 5. Generate Forecasts

```text
POST /api/v1/forecast/generate
```

Use request body:

```json
{
  "horizon_days": 1,
  "hotspot_id": null,
  "replace_existing": true,
  "pipeline_run_id": "forecast-v1-h1"
}
```

Expected output:

```text
forecasts_created: 5872
```

---

### 6. Generate Officer Allocations

Use the available allocation endpoint from Swagger.

The allocation service distributes officers across priority hotspots based on risk score and selected officer capacity.

Expected database output:

```text
allocations > 0
```

---

### 7. Generate Patrol Routes

Use the available patrol/routing endpoint from Swagger.

The route service generates patrol stop sequences based on allocated hotspots.

Expected database output:

```text
patrol_routes > 0
```

---

## Useful Database Checks

Check main table counts:

```bash
docker exec -it parkwise-postgres psql -U postgres -d parkwise -c "select count(*) from violations; select count(*) from hotspots; select count(*) from eis_scores;"
```

Check generated intelligence tables:

```bash
docker exec -it parkwise-postgres psql -U postgres -d parkwise -c "select count(*) from forecasts; select count(*) from allocations; select count(*) from patrol_routes;"
```

Expected tested values:

```text
violations:     298450
hotspots:       5872
eis_scores:     5872
forecasts:      5872
allocations:    103
patrol_routes:  10
```

---

## API Endpoints

Important endpoints include:

```text
GET  /health
GET  /api/v1/dashboard/full
GET  /api/v1/dashboard/summary

GET  /api/v1/hotspots
POST /api/v1/hotspots/run-pipeline

POST /api/v1/temporal/run-pipeline

GET  /api/v1/eis/scores
POST /api/v1/eis/run-pipeline

POST /api/v1/forecast/train
POST /api/v1/forecast/generate
GET  /api/v1/forecast/summary
GET  /api/v1/forecast/top

GET  /api/v1/allocation/latest

GET  /api/v1/routing/latest
GET  /api/v1/routing/summary
```

Refer to Swagger for the latest full API list:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Pages

```text
/              Landing page
/dashboard     Command dashboard
/hotspots      Hotspot intelligence
/temporal      Risk score breakdown
/forecast      Forecast intelligence
/allocation    Officer allocation
/patrol        Patrol route planner
```

Simulator has been intentionally removed from the final app.

---

## Real Data vs Generated Outputs

The original CSV contains violation records.

The following are computed/generated by ParkWise:

```text
Hotspots
Risk/EIS scores
Forecasts
Officer allocations
Patrol routes
```

So the correct explanation is:

> ParkWise uses the real uploaded violation dataset to detect hotspots, compute risk scores, forecast future risk, and generate officer allocation and patrol-route recommendations.

Do not claim the original dataset already contained forecasts, allocations, or patrol routes.

---

## Model Performance

The current forecasting model was trained on hotspot-level EIS/risk-score data.

```text
Model: LightGBM
Rows used: 5872
Validation rows: 1468
R²: 0.8699
MAE: 3.3045
```

Recommended UI/demo wording:

```text
Forecast Reliability: 87%
Average Error: ±3.30 risk-score points
```

Technical explanation:

> Since the model predicts a continuous hotspot risk score, it is evaluated using regression metrics. The validation R² of 0.87 means the model explains about 87% of the variation in hotspot risk, with an average error of 3.30 risk-score points.

---

## Demo Flow

Recommended demo sequence:

1. Open Landing page
2. Go to Dashboard
3. Show total violations and priority hotspots
4. Open Hotspots page
5. Show spatial hotspot records and risk tiers
6. Open Risk Score page
7. Explain how risk score is calculated
8. Open Forecast page
9. Show model reliability, MAE, and forecast watchlist
10. Open Allocation page
11. Adjust officer count and optimize allocation
12. Open Patrol page
13. Show generated route sequence for allocated hotspots

---

## Git Notes

Do not commit:

```text
.env
data/
*.csv
node_modules/
dist/
__pycache__/
.venv/
```

Recommended `.gitignore` entries:

```gitignore
.env
*.env
data/
*.csv
*.xlsx

node_modules/
dist/
.vite/

.venv/
venv/
__pycache__/
.pytest_cache/

app/ml/artifacts/
*.pkl
*.joblib
```

---

## Common Issues

### 1. Backend says database connection refused

Start Docker DB:

```bash
docker start parkwise-postgres
docker ps
```

---

### 2. Backend says SECRET_KEY missing

Update:

```text
backend/.env
```

Add:

```env
SECRET_KEY=parkwise-super-secret-key-for-development-2026
```

---

### 3. Forecast training says not enough EIS rows

Use:

```json
{
  "horizon_days": 1,
  "hotspot_id": null,
  "model_version": "forecast-v1-h1",
  "min_history_per_hotspot": 1
}
```

Do not use:

```json
{
  "hotspot_id": 0,
  "min_history_per_hotspot": 4
}
```

---

### 4. Forecast generation creates 0 rows

Use:

```json
{
  "horizon_days": 1,
  "hotspot_id": null,
  "replace_existing": true,
  "pipeline_run_id": "forecast-v1-h1"
}
```

Do not use:

```json
{
  "hotspot_id": 0
}
```

---

### 5. Frontend shows stale data

Restart frontend and hard refresh:

```bash
cd frontend
npm run dev
```

Then in browser:

```text
Ctrl + Shift + R
```

---

## Final Status

ParkWise Command Center currently supports:

* Real violation data ingestion
* Hotspot detection
* Risk scoring
* Forecast training and generation
* Officer allocation
* Patrol route generation
* Full command-center frontend connected to backend APIs

The platform is suitable for demonstrating an end-to-end AI-driven parking intelligence workflow for congestion-aware traffic enforcement.
