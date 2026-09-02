# Deployment Guide

This project can be pushed to GitHub and deployed with Render plus MongoDB Atlas, but there is one important limitation: the current AI stack depends on a running Ollama server with local models. Do not assume a basic Render Python service will automatically have Ollama, `llama3.1`, or `nomic-embed-text`.

Useful references:

- Render FastAPI guide: https://render.com/docs/deploy-fastapi
- Render environment variables: https://render.com/docs/configure-environment-variables
- Render persistent disks: https://render.com/docs/disks
- Render Docker support: https://render.com/docs/docker
- Vite Render static deployment: https://vite.dev/guide/static-deploy
- Ollama Docker image: https://hub.docker.com/r/ollama/ollama

## 1. Prepare GitHub

From the project root:

```powershell
cd D:\vedant-coding\coding\ai-resume
git init
git status
git add .
git status
git commit -m "Integrate frontend with backend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-resume.git
git push -u origin main
```

Before pushing, confirm these are not committed:

- `.env`
- `backend/venv/`
- `frontend/node_modules/`
- `frontend/dist/`
- `backend/data/vectorstore/`
- `backend/uploads/`
- `__pycache__/`

## 2. Create MongoDB Atlas Database

1. Create a MongoDB Atlas account.
2. Create a cluster.
3. Create a database user.
4. Add your Render outbound access policy. For a student/demo project, you may temporarily allow access from anywhere, but restrict it later.
5. Copy the connection string.

Backend environment variables:

```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>/<database-name>?retryWrites=true&w=majority
MONGODB_DATABASE=ai_resume
```

Do not commit the real connection string.

## 3. Backend On Render

Create a Render Web Service connected to the GitHub repo.

Use these settings:

- Root Directory: `backend`
- Runtime: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Set environment variables:

```env
MONGODB_URI=<your MongoDB Atlas connection string>
MONGODB_DATABASE=ai_resume
FRONTEND_URL=https://<your-frontend-name>.onrender.com
```

The backend uses `FRONTEND_URL` for CORS, plus local Vite origins for development.

## 4. Ollama Deployment Reality

Local development is fully supported because Ollama runs on your machine.

On Render, the current backend will not complete resume upload or match analysis unless it can reach an Ollama server that has:

- `nomic-embed-text`
- `llama3.1`

Realistic options:

1. Keep the backend local for full AI demos.
   This is the simplest and most reliable for interviews.

2. Run Ollama on a separate machine/VPS with enough CPU/RAM or GPU.
   Then configure the backend to point LangChain/Ollama to that server. This project currently uses LangChain defaults, so this would need a small backend config change later.

3. Use a Docker-based Render service that starts Ollama and FastAPI together.
   Render supports Docker, and Ollama publishes a Docker image, but this is heavier than the current beginner-friendly setup. It also needs enough RAM/disk for the models and careful startup scripts to pull models before requests.

For this project, the honest recommendation is:

- Use Render for frontend.
- Use MongoDB Atlas for database.
- Use local backend plus local Ollama for the complete AI demo.
- Only deploy the backend AI flow to Render if you are ready to handle Ollama runtime, model storage, memory, and disk requirements.

## 5. FAISS Persistence On Render

The backend currently saves FAISS files locally under:

```text
backend/data/vectorstore/
```

Render services have an ephemeral filesystem by default. Without a persistent disk, generated FAISS files can be lost on redeploy or restart.

If you deploy the backend and want FAISS files to survive:

1. Use a paid Render Web Service with a persistent disk.
2. Mount it under the backend source path, for example:

```text
/opt/render/project/src/backend/data
```

3. Keep the current code writing to `data/vectorstore` from the `backend` root.

Limitations:

- A Render persistent disk is attached to one service instance.
- Scaling to multiple backend instances is not suitable with this local FAISS layout.
- Uploads and generated vector stores are runtime data, not GitHub files.

## 6. Frontend On Render Static Site

Create a Render Static Site connected to the same GitHub repo.

Use these settings:

- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`

Set environment variable:

```env
VITE_API_URL=https://<your-backend-name>.onrender.com
```

Important: Vite reads `VITE_API_URL` at build time. If you change it, redeploy the frontend.

## 7. CORS

The backend allows:

- `http://localhost:5173`
- `http://127.0.0.1:5173`
- the value of `FRONTEND_URL`, if set

For deployment, set:

```env
FRONTEND_URL=https://<your-frontend-name>.onrender.com
```

Then redeploy the backend.

## 8. Test Deployment

1. Open the deployed backend root URL.
2. Open deployed Swagger at `/docs`.
3. Open the deployed frontend.
4. Try uploading a PDF.
5. If upload fails during embedding, check whether Ollama is actually available to the backend.
6. Create a job description.
7. Run match analysis.
8. Check Render backend logs for errors.

## 9. Common Problems

Backend deploys but upload fails:

- Ollama is probably not running in the deployed backend environment.
- `nomic-embed-text` may not be available.

Match fails:

- `llama3.1` may not be available.
- The resume or job FAISS vector store may be missing.

Results disappear after redeploy:

- FAISS files were saved to Render's ephemeral filesystem.
- Add a persistent disk or recreate the resume/job records.

Frontend cannot call backend:

- Check `VITE_API_URL` on the Render Static Site.
- Check `FRONTEND_URL` on the Render backend.
- Redeploy both services after changing env vars.

MongoDB connection fails:

- Check `MONGODB_URI`.
- Check Atlas database user credentials.
- Check Atlas network access.

## Final Deployment Summary

Recommended student/demo setup:

```text
GitHub repo
  -> Render Static Site for frontend
  -> MongoDB Atlas for database
  -> Local FastAPI + local Ollama for full AI functionality
```

Possible advanced setup:

```text
GitHub repo
  -> Render Static Site for frontend
  -> Render backend with persistent disk
  -> MongoDB Atlas
  -> Ollama available through Docker or a separate Ollama server
```

The advanced setup is realistic, but it is no longer as simple as the current local learning project.
