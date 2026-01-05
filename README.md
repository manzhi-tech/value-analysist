# Value Analyst Tool - Setup & Run Instructions

## Prerequisites
1. **Model Provider Keys**: Ensure `.env` is populated with your Aliyun or Volcengine API keys.
2. **Conda**: Ensure the `cut-agent` environment is created and dependencies are installed.

## 1. Start Infrastructure (Docker)
This starts the Database (Postgres) and Vector Store (ChromaDB).
```bash
docker-compose up -d
```

## 2. Start Backend
The backend runs on `http://localhost:8000`.
```bash
chmod +x start_backend.sh
./start_backend.sh
```
*Note: This strictly uses the `cut-agent` conda environment.*

## 3. Start Frontend
The frontend runs on `http://localhost:3000`.
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

## Usage
1. Open `http://localhost:3000`.
2. Upload a Company's Annual Report (PDF).
3. Follow the analysis steps (Business -> MD&A -> Financial -> Valuation).
