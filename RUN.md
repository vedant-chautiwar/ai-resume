# AI Resume Intelligence & Job Matcher

This project is a learning-friendly AI resume matcher.

The frontend is a React/Vite app. The backend is a FastAPI app that stores resumes and jobs in MongoDB, creates embeddings with Ollama `nomic-embed-text`, saves FAISS vector stores locally, and uses Ollama `llama3.1` for match analysis.

## Prerequisites

- Windows
- Python 3.12
- Node.js LTS
- MongoDB running locally or a MongoDB Atlas connection string
- Ollama installed and running
- Git

## Required Ollama Models

Install the two models used by the backend:

```powershell
ollama pull nomic-embed-text
ollama pull llama3.1
```

Check that Ollama is running:

```powershell
ollama list
```

## Backend Setup

Open a terminal at the project root:

```powershell
cd D:\vedant-coding\coding\ai-resume
cd backend
```

Create a Conda environment:

```powershell
conda create -n ai-resume python=3.12
conda activate ai-resume
```

Install backend dependencies:

```powershell
pip install -r requirements.txt
```

Create `backend\.env`:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=ai_resume
FRONTEND_URL=http://localhost:5173
```

If you use MongoDB Atlas, replace `MONGODB_URI` with your Atlas connection string. Do not commit `.env`.

Start FastAPI from the `backend` folder:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend URLs:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

## Frontend Setup

Open a second terminal at the project root:

```powershell
cd D:\vedant-coding\coding\ai-resume
cd frontend
```

Install frontend dependencies:

```powershell
npm install
```

Create `frontend\.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start React/Vite:

```powershell
npm run dev
```

Frontend URL:

- `http://localhost:5173`

## How To Use

1. Keep MongoDB running.
2. Keep Ollama running.
3. Start the backend with `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`.
4. Start the frontend with `npm run dev`.
5. Open `http://localhost:5173`.
6. Upload a PDF resume.
7. Enter a job title and job description.
8. Click `Add Job Description`.
9. Click `Analyze Match`.
10. View the real match score, summary, matched skills, missing skills, and weak skills.

## Testing The API

Use Swagger at:

```text
http://127.0.0.1:8000/docs
```

Important endpoints:

- `POST /api/resumes/upload`
- `POST /api/jobs/`
- `POST /api/matches`
- `GET /api/matches/{match_id}`

## Troubleshooting

If you get `WinError 10013` (Socket Permission / Port Conflict):

- Port 8000 is already in use by another instance or process.
- Run `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`.
- If port 8000 is occupied by another app, kill the existing process using port 8000 (`Get-NetTCPConnection -LocalPort 8000`).

If the frontend says it cannot connect to the backend:

- Make sure FastAPI is running on `http://127.0.0.1:8000`.
- Check `frontend\.env` has `VITE_API_URL=http://127.0.0.1:8000`.
- Restart `npm run dev` after changing `.env`.

If resume upload fails:

- Upload a real `.pdf` file.
- Make sure MongoDB is running.
- Make sure Ollama is running.
- Make sure `nomic-embed-text` is installed.

If matching fails:

- Make sure `llama3.1` is installed.
- Make sure the resume upload and job creation both succeeded first.
- Check the FastAPI terminal for the exact backend error.

If CORS fails:

- Use `http://localhost:5173` or `http://127.0.0.1:5173` for the frontend.
- Set `FRONTEND_URL` in `backend\.env` if you use another frontend URL.
- Restart the backend after changing `backend\.env`.

If FAISS files are missing:

- Upload the resume again.
- Create the job again.
- The backend stores FAISS files under `backend\data\vectorstore`.
