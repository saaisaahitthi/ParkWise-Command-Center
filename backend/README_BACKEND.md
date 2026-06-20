# ParkWise Command Center

## AI-Powered Parking Impact Intelligence Platform

ParkWise Command Center is an AI-powered traffic enforcement intelligence system built for detecting parking-induced congestion, ranking illegal parking hotspots, forecasting future risk, allocating enforcement officers, and generating patrol routes.

The system is designed around the theme:

**Poor Visibility on Parking-Induced Congestion**

Illegal on-street parking, wrong parking, footpath parking, main-road parking, and spillover parking reduce road capacity and create congestion around junctions, commercial zones, metro stations, and event-heavy areas. Traditional enforcement is usually patrol-based and reactive. ParkWise converts historical police violation data into actionable enforcement intelligence.

---

## 1. Problem Statement

Cities often have large volumes of parking violation records, but enforcement teams do not always have a clear way to answer questions like:

* Where are illegal parking hotspots concentrated?
* Which hotspots create the highest congestion risk?
* Which time windows need stronger enforcement?
* Which hotspots are likely to remain risky in the future?
* How should limited officers be allocated?
* What patrol route should be followed?
* What happens if officer availability or enforcement intensity changes?

ParkWise solves this by building an end-to-end decision intelligence pipeline:

```text
Raw police violation data
→ hotspot detection
→ enriched violation records
→ temporal intelligence
→ EIS risk scoring
→ ML forecasting
→ officer allocation
→ patrol route generation
→ dashboard + simulator
```

---

## 2. Key Features

### 2.1 Hotspot Detection

ParkWise processes police violation records and groups them into hotspot zones using junction-level grouping and coordinate-based fallback grouping.

The hotspot module identifies:

* hotspot name
* centroid latitude and longitude
* total violation count
* dominant violation type
* dominant vehicle category
* number of unique active dates
* violation density indicators

This gives enforcement teams a clear view of where parking-related violations are repeatedly happening.

---

### 2.2 Enriched Violation Layer

Raw violations are transformed into enriched records with severity scores.

Severity mapping is based on parking impact:

```text
DOUBLE PARKING              highest severity
PARKING IN A MAIN ROAD      high severity
FOOTPATH PARKING            high pedestrian impact
NO PARKING                  medium severity
WRONG PARKING               base severity
```

This enriched layer helps downstream modules understand that all violations are not equal. A double-parked vehicle or main-road obstruction should have more impact than a minor parking issue.

---

### 2.3 Temporal Intelligence

ParkWise detects peak violation windows by analyzing:

* hour of day
* day of week
* hotspot-level recurrence
* violation count per time bucket
* peak enforcement windows

The system generates time-based recommendations such as:

* morning rush windows
* lunch-hour peaks
* evening rush windows
* night/off-peak patterns

This helps enforcement teams decide not only where to deploy officers, but also when.

---

### 2.4 Enforcement Impact Score

ParkWise computes an Enforcement Impact Score, also called EIS, for every hotspot.

The EIS score combines multiple risk dimensions:

```text
frequency_score
recurrence_score
density_score
temporal_risk_score
severity_norm
exposure_score
severity_multiplier
```

The final score is converted into a risk category:

```text
0–24.99      Low
25–49.99     Medium
50–74.99     High
75–100       Critical
```

This allows the system to rank hotspots by enforcement priority.

---

### 2.5 Machine Learning Forecasting

The forecasting module predicts future hotspot risk using features generated from EIS and violation history.

Training features include:

```text
hotspot_id
frequency_score
recurrence_score
density_score
temporal_risk_score
severity_norm
exposure_score
severity_multiplier
total_violations
```

The model predicts future EIS/risk values for hotspots and stores the forecasts in the database.

Forecasting helps the system answer:

* Which hotspots are likely to remain risky?
* Which currently medium-risk hotspots may increase?
* Where should enforcement be planned proactively?

---

### 2.6 Officer Allocation

ParkWise allocates available officers across high-priority hotspots using latest risk scores and forecasts.

Allocation considers:

* current EIS
* forecasted EIS
* risk category
* priority rank
* available officer pool
* minimum coverage rules for Critical and High hotspots

Example allocation request:

```json
{
  "total_officers": 20,
  "top_n_hotspots": 4
}
```

The allocation output includes:

* officers allocated per hotspot
* allocation fraction
* deployment window
* EIS snapshot
* risk category

---

### 2.7 Patrol Route Generation

ParkWise generates patrol routes from allocated hotspots.

The routing module calculates:

* route stops
* total distance
* estimated travel time
* estimated total enforcement time
* route geometry
* route summary

The route generation uses internal fallback geospatial logic to ensure the system works even without external APIs.

Example route generation request:

```json
{
  "route_date": "2026-06-19",
  "max_routes": 4,
  "max_stops_per_route": 10
}
```

---

### 2.8 What-If Simulator

The simulator allows users to test different enforcement scenarios.

Supported scenarios include:

```text
Increase officers by 20%
Reduce frequency by 15%
Reduce temporal risk by 20%
Critical hotspot surge deployment
Low enforcement scenario
```

Example simulator request:

```json
{
  "scenario_name": "Increase officers by 20%",
  "overrides": {
    "total_officers": 24
  }
}
```

Simulator output includes:

* total hotspots analyzed
* improved hotspots
* worsened hotspots
* unchanged hotspots
* baseline average EIS
* simulated average EIS
* average EIS delta
* officer changes
* impact notes

This allows decision-makers to evaluate how changes in enforcement strategy may affect congestion risk.

---

### 2.9 Dashboard API Layer

The backend exposes frontend-ready dashboard endpoints.

The dashboard layer combines outputs from:

* hotspots
* EIS scores
* forecasts
* allocations
* patrol routes
* simulator data

Main dashboard output includes:

```text
executive_summary
risk_distribution
hotspot_map
forecast overview
allocation overview
routing overview
temporal overview
```

---

### 2.10 Optional MapMyIndia / Mappls Integration

ParkWise is designed to support MapMyIndia / Mappls as a mapping intelligence layer.

The current system already has internal geospatial fallback routing. Mappls can be added as an optional enhancement without replacing the existing working pipeline.

The intended integration strategy is:

```text
Existing internal routing engine remains active
Mappls is added for route preview / map intelligence
If Mappls credentials exist, Mappls can be used
If credentials are missing, system falls back to internal geometry
```

Planned optional endpoints:

```text
GET  /api/v1/mappls/status
POST /api/v1/mappls/route-preview
```

This approach keeps the backend reliable while allowing Mappls-backed visualization or route preview if credentials are available.

Example Mappls status response:

```json
{
  "enabled": false,
  "has_client_id": false,
  "has_client_secret": false,
  "has_access_token": false,
  "provider": "mappls",
  "mode": "internal_fallback"
}
```

Example route preview request:

```json
{
  "stops": [
    {
      "latitude": 12.9812,
      "longitude": 77.6086,
      "hotspot_id": 5739,
      "name": "Safina Plaza Junction"
    },
    {
      "latitude": 12.9644,
      "longitude": 77.5772,
      "hotspot_id": 5761,
      "name": "KR Market Junction"
    }
  ]
}
```

Example fallback response:

```json
{
  "provider": "internal_fallback",
  "mode": "fallback",
  "route_geometry": [
    {
      "latitude": 12.9812,
      "longitude": 77.6086
    },
    {
      "latitude": 12.9644,
      "longitude": 77.5772
    }
  ],
  "message": "Mappls credentials not configured. Using internal route geometry."
}
```

This partial Mappls approach is intentionally lightweight and safe. It avoids disrupting the already working hotspot, forecasting, allocation, and patrol route pipeline.

---

## 3. Tech Stack

### Backend

```text
Python 3.12
FastAPI
SQLAlchemy
Pydantic
Alembic
PostgreSQL
PostGIS
GeoAlchemy2
LightGBM
scikit-learn
pytest
```

### Database

```text
PostgreSQL with PostGIS extension
```

### ML / Data Processing

```text
pandas
numpy
LightGBM
scikit-learn
joblib
```

### API Documentation

```text
Swagger UI
OpenAPI JSON
```

---

## 4. Project Structure

```text
parkwise-backend/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── router.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   │
│   ├── ml/
│   │   ├── forecast_model.py
│   │   └── feature_builder.py
│   │
│   ├── models/
│   │   └── database models
│   │
│   ├── repositories/
│   │   └── database access layer
│   │
│   ├── schemas/
│   │   └── Pydantic request/response schemas
│   │
│   ├── services/
│   │   └── business logic layer
│   │
│   └── main.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── scripts/
│   └── load_violations.py
│
├── tests/
│   ├── unit/
│   └── sqlite_helpers.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

---

## 5. Environment Variables

Create a `.env` file locally using `.env.example`.

Example:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/parkwise
TEST_DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/parkwise_test

DEBUG=true
SECRET_KEY=change-me

USE_MAPPLS=false
MAPPLS_CLIENT_ID=
MAPPLS_CLIENT_SECRET=
MAPPLS_ACCESS_TOKEN=
```

Important:

```text
Do not commit .env
Do not expose real secrets
Use .env.example for sharing configuration format
```

---

## 6. Local Setup

### 6.1 Clone Repository

```bash
git clone <repository-url>
cd parkwise-backend
```

---

### 6.2 Create Virtual Environment

Windows:

```cmd
C:\Windows\py.exe -3.12 -m venv .venv
.venv\Scripts\activate
```

If virtual environment is not used, commands can still be run with:

```cmd
C:\Windows\py.exe -3.12
```

---

### 6.3 Install Dependencies

```cmd
C:\Windows\py.exe -3.12 -m pip install -r requirements.txt
```

---

## 7. Database Setup

ParkWise uses PostgreSQL with PostGIS.

### 7.1 Start PostGIS Using Docker

```cmd
docker run --name parkwise-postgres ^
  -e POSTGRES_USER=postgres ^
  -e POSTGRES_PASSWORD=postgres ^
  -e POSTGRES_DB=parkwise ^
  -p 5433:5432 ^
  -d postgis/postgis:16-3.4
```

The backend uses port `5433` locally because port `5432` may already be used by another PostgreSQL installation.

---

### 7.2 Start Existing Database Container

If the container already exists:

```cmd
docker start parkwise-postgres
```

---

### 7.3 Stop Database Container

To stop PostgreSQL without deleting data:

```cmd
docker stop parkwise-postgres
```

Do not run `docker rm parkwise-postgres` unless you intentionally want to remove the container.

---

## 8. Run Migrations

Apply database migrations:

```cmd
C:\Windows\py.exe -3.12 -m alembic upgrade head
```

This creates required tables such as:

```text
violations
hotspots
enriched_violations
peak_windows
eis_scores
forecasts
allocations
patrol_routes
```

---

## 9. Load Police Violation Data

The ingestion script loads police violation CSV data into the database.

Example:

```cmd
C:\Windows\py.exe -3.12 scripts/load_violations.py
```

Expected result after successful ingestion:

```text
Total rows read: 298450
Inserted count: 298450
Skipped count: 0
DB count: 298450
```

The dataset file should stay local and should not be committed.

---

## 10. Run Backend Server

Start FastAPI server:

```cmd
C:\Windows\py.exe -3.12 -m uvicorn app.main:app --reload
```

Server runs at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

Expected health response:

```json
{
  "status": "ok",
  "app": "ParkWise Command Center",
  "version": "1.0.0",
  "env": "development"
}
```

---

## 11. Pipeline Execution Order

The full backend pipeline should be executed in this order:

```text
1. Run migrations
2. Load violations CSV
3. Run hotspot pipeline
4. Run temporal pipeline
5. Run EIS pipeline
6. Train forecast model
7. Generate forecasts
8. Compute officer allocation
9. Generate patrol route
10. Run dashboard/simulator APIs
```

---

## 12. Pipeline API Commands

### 12.1 Run Hotspot Pipeline

Endpoint:

```text
POST /api/v1/hotspots/run-pipeline
```

This creates:

```text
hotspots
enriched_violations
```

Expected database counts:

```text
hotspots             5872
enriched_violations  298450
```

---

### 12.2 Run Temporal Pipeline

Endpoint:

```text
POST /api/v1/temporal/run-pipeline
```

Example body:

```json
{
  "truncate_existing": true,
  "min_window_violations": 5
}
```

Expected output:

```text
peak_windows 13032
```

---

### 12.3 Run EIS Pipeline

Endpoint:

```text
POST /api/v1/eis/run-pipeline
```

Expected output:

```text
eis_scores 5872
```

---

### 12.4 Train Forecast Model

Endpoint:

```text
POST /api/v1/forecast/train
```

Example body:

```json
{
  "horizon_days": 1,
  "model_version": "forecast-v1",
  "min_history_per_hotspot": 1
}
```

Example response:

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
  "r2": 0.8698
}
```

---

### 12.5 Generate Forecasts

Endpoint:

```text
POST /api/v1/forecast/generate
```

Example body:

```json
{
  "horizon_days": 1,
  "replace_existing": true
}
```

Expected database count:

```text
forecasts 5872
```

Note:

```text
This endpoint is intended as an admin/pipeline action.
Frontend should not call it automatically on page load.
```

---

### 12.6 Compute Allocation

Endpoint:

```text
POST /api/v1/allocation/compute
```

Example body:

```json
{
  "total_officers": 20,
  "top_n_hotspots": 4
}
```

Expected output:

```text
allocations 4
```

---

### 12.7 Generate Patrol Route

Endpoint:

```text
POST /api/v1/routing/generate
```

Example body:

```json
{
  "route_date": "2026-06-19",
  "max_routes": 4,
  "max_stops_per_route": 10
}
```

Expected output:

```text
patrol_routes 1
```

---

## 13. Important API Endpoints

### Health

```text
GET /health
```

---

### Dashboard

```text
GET /api/v1/dashboard/summary
GET /api/v1/dashboard/risk-distribution
GET /api/v1/dashboard/map
GET /api/v1/dashboard/temporal
GET /api/v1/dashboard/forecast
GET /api/v1/dashboard/allocation
GET /api/v1/dashboard/routing
GET /api/v1/dashboard/full
```

---

### Hotspots

```text
GET  /api/v1/hotspots/
GET  /api/v1/hotspots/map/pins
GET  /api/v1/hotspots/{hotspot_id}
POST /api/v1/hotspots/run-pipeline
```

---

### EIS

```text
GET  /api/v1/eis/scores
GET  /api/v1/eis/scores/{hotspot_id}
GET  /api/v1/eis/priority-queue
POST /api/v1/eis/run-pipeline
```

---

### Temporal

```text
GET  /api/v1/temporal/peak-windows
GET  /api/v1/temporal/enforcement-schedule
GET  /api/v1/temporal/heatmap
GET  /api/v1/temporal/hotspots/{hotspot_id}/windows
GET  /api/v1/temporal/hotspots/{hotspot_id}/risk-score
POST /api/v1/temporal/run-pipeline
```

---

### Forecast

```text
POST /api/v1/forecast/train
POST /api/v1/forecast/generate
GET  /api/v1/forecast
GET  /api/v1/forecast/top
GET  /api/v1/forecast/hotspots/{hotspot_id}
GET  /api/v1/forecast/summary
```

---

### Allocation

```text
POST /api/v1/allocation/compute
GET  /api/v1/allocation/latest
```

---

### Routing

```text
POST /api/v1/routing/generate
GET  /api/v1/routing
GET  /api/v1/routing/latest
GET  /api/v1/routing/summary
GET  /api/v1/routing/{route_id}
```

---

### Patrol

```text
GET /api/v1/patrol/
GET /api/v1/patrol/{route_id}
```

---

### Simulator

```text
GET  /api/v1/simulator/presets
GET  /api/v1/simulator/baseline
POST /api/v1/simulator/run
```

---

### Optional Mappls

```text
GET  /api/v1/mappls/status
POST /api/v1/mappls/route-preview
```

These endpoints are optional and intended for partial MapMyIndia / Mappls integration.

---

## 14. Frontend Integration Guidance

For normal frontend page load, use read-only endpoints.

Recommended frontend APIs:

```text
GET /api/v1/dashboard/full
GET /api/v1/hotspots/?page=1&page_size=50
GET /api/v1/eis/scores
GET /api/v1/forecast/summary
GET /api/v1/forecast/top
GET /api/v1/allocation/latest
GET /api/v1/routing/latest
GET /api/v1/simulator/presets
GET /api/v1/simulator/baseline
```

Avoid calling these automatically on page load:

```text
POST /api/v1/hotspots/run-pipeline
POST /api/v1/eis/run-pipeline
POST /api/v1/temporal/run-pipeline
POST /api/v1/forecast/train
POST /api/v1/forecast/generate
POST /api/v1/allocation/compute
POST /api/v1/routing/generate
POST /api/v1/simulator/run
```

POST endpoints should be used only through admin buttons or controlled user actions.

---

## 15. Suggested Frontend Screens

Minimum demo screens:

```text
1. Dashboard Overview
2. Hotspot Map
3. Hotspot Table
4. Risk / EIS Explainability
5. Forecast + Allocation
6. Patrol Route
7. What-If Simulator
```

Optional screen:

```text
AI Commander
```

AI Commander can be generated in frontend using:

```text
GET /api/v1/dashboard/full
GET /api/v1/eis/scores
GET /api/v1/allocation/latest
GET /api/v1/routing/latest
```

Example commander card:

```text
Critical hotspot detected at Safina Plaza Junction.
Deploy 5 officers.
Recommended route available.
Forecasted EIS remains high.
```

---

## 16. Current Verified Backend Data

The backend pipeline has been verified with the following database counts:

```text
violations              298450
hotspots                5872
enriched_violations     298450
peak_windows            13032
eis_scores              5872
forecasts               5872
allocations             4
patrol_routes           1
```

---

## 17. Testing

Run unit tests:

```cmd
C:\Windows\py.exe -3.12 -m pytest tests/unit -v --basetemp=C:\Users\sudhe\OneDrive\Desktop\pytest-temp
```

If the default Windows temp folder gives permission errors, use a project-local pytest temp folder:

```cmd
mkdir C:\Users\sudhe\OneDrive\Desktop\pytest-temp
set TMP=C:\Users\sudhe\OneDrive\Desktop\pytest-temp
set TEMP=C:\Users\sudhe\OneDrive\Desktop\pytest-temp
C:\Windows\py.exe -3.12 -m pytest tests/unit -v --basetemp=C:\Users\sudhe\OneDrive\Desktop\pytest-temp
```

Verified result:

```text
All unit tests passed.
```

---

## 18. Common Issues

### 18.1 Docker Makes System Slow

The PostgreSQL/PostGIS database runs in Docker.

If no one is testing, stop it:

```cmd
docker stop parkwise-postgres
```

Restart later:

```cmd
docker start parkwise-postgres
```

Do not remove the container unless you want to delete the database.

---

### 18.2 Swagger UI Becomes Unresponsive

Swagger can freeze when rendering very large JSON responses.

Avoid opening huge full-list APIs in Swagger such as:

```text
GET /api/v1/eis/scores
GET /api/v1/forecast
GET /api/v1/dashboard/full
```

Use limited endpoints:

```text
GET /api/v1/hotspots/?page=1&page_size=10
GET /api/v1/eis/scores?risk_category=Critical
GET /api/v1/dashboard/summary
```

---

### 18.3 Forecast Generate Takes Time

Forecast generation is a pipeline/admin action.

It should not be called repeatedly from frontend page load.

Use read APIs instead:

```text
GET /api/v1/forecast/summary
GET /api/v1/forecast/top
GET /api/v1/dashboard/forecast
```

---

### 18.4 Routing Requires route_date

Invalid request:

```json
{
  "max_routes": 4,
  "max_stops_per_route": 10
}
```

Correct request:

```json
{
  "route_date": "2026-06-19",
  "max_routes": 4,
  "max_stops_per_route": 10
}
```

---

### 18.5 Simulator Requires scenario_name

Invalid request:

```json
{
  "total_officers": 24
}
```

Correct request:

```json
{
  "scenario_name": "Increase officers by 20%",
  "overrides": {
    "total_officers": 24
  }
}
```

---

## 19. Design Philosophy

ParkWise follows a modular design:

```text
Data ingestion is separate from hotspot detection
Hotspot detection is separate from temporal intelligence
Temporal intelligence is separate from EIS scoring
EIS scoring is separate from forecasting
Forecasting is separate from allocation
Allocation is separate from routing
Routing is separate from dashboard presentation
```

This makes the system easier to test, debug, and extend.

---

## 20. Why Optional Mappls Instead of Full Replacement

The existing backend already computes hotspots, forecasts, allocation, and patrol routes.

Replacing routing with an external API at the end of development could risk breaking:

```text
dashboard routing
allocation-to-route conversion
patrol route persistence
unit tests
frontend map rendering
```

Therefore, Mappls is planned as an optional route-preview and map intelligence layer.

This gives the project MapMyIndia support while preserving reliability.

---

## 21. Summary

ParkWise Command Center converts historical parking violation data into actionable enforcement intelligence.

It supports:

```text
parking hotspot detection
temporal risk analysis
EIS risk ranking
ML-based risk forecasting
officer allocation
patrol route generation
what-if simulation
dashboard APIs
optional Mappls integration
```

The system is backend-ready, test-covered, and designed for frontend dashboard integration.
