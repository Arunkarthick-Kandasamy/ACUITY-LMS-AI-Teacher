# Run Commands

## Prerequisites

- **Python 3.12+** with packages installed:
  ```powershell
  cd Backend
  pip install -e .
  ```

- **Node.js** with dependencies installed:
  ```powershell
  cd acuity-frontend
  npm install
  ```

## 1. Initialize Database (first time only)

```powershell
cd Backend
python scripts\init_db.py
```

## 2. Start Backend (FastAPI)

```powershell
cd Backend
python -m uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs for interactive API docs.

## 3. Start Frontend (Vite + React)

```powershell
cd acuity-frontend
npm run dev
```

Open http://localhost:5173 in your browser.

## Environment Setup

### Backend (`Backend/.env`)
```
DATABASE_URL=sqlite+aiosqlite:///./acuity.db
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
```

### Frontend (`acuity-frontend/.env`)
```
VITE_API_URL=http://localhost:8000
```
