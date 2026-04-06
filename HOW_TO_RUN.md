# How to Run the App (Complete Guide)

This guide gets your Medical Fact-Check Platform running locally in minutes. Ensure you have **Docker** and **Node.js** installed on your Windows machine.

---

## 🚀 Step 1: Set up the Environment
First, ensure you have the configuration file ready. Run this in your project root terminal:
```powershell
Copy-Item .env.development .env -Force
```

## 🐳 Step 2: Start Backend & ML Services
Use Docker Compose to spin up the database, cache, and FastAPI backend. We highly recommend using the `--build` flag to ensure that any new backend dependencies (like `yt-dlp` for video scraping) are correctly installed:
```powershell
docker-compose up -d --build
```
> **Note:** The first time you run this, it may take 5-10 minutes to download dependencies like PyTorch. Wait about 30 seconds after it finishes building for the ML models to load fully.

## 💻 Step 3: Start the Frontend UI
Open a **new terminal**, navigate to the frontend directory, and start the Next.js development server. We include an Execution Policy fix so Windows PowerShell doesn't block `npm`.
```powershell
cd frontend
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
npm install
npm run dev
```

## 🌐 Step 4: Access the App
- **Frontend Dashboard**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/api/docs

---

## 🛑 Stopping the App
When you are done developing, here is how to close everything cleanly:

**1. Stop the Frontend:**
Click inside the terminal window where the frontend (`npm run dev`) is running and press `Ctrl + C`. Press `Y` and Enter if it asks to terminate the batch job.

**2. Stop the Backend & Database:**
Run the following command in your project root terminal to cleanly shut down and remove the Docker containers:
```powershell
docker-compose down
```
*(Note: If you only want to pause them without removing containers, you can use `docker-compose stop` instead).*

---

## 💡 Troubleshooting Common Windows Issues

### 1. "EADDRINUSE: address already in use :::3000" during `npm run dev`
This means an old hidden frontend process is still listening on port 3000. Cleanly stop it by running this in PowerShell, then try starting your server again:
```powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue).OwningProcess -Force -ErrorAction SilentlyContinue
npm run dev
```

### 2. "No module named X" in Backend
If you get missing Python module errors (like `yt_dlp`) when trying to analyze a link, it means your Docker container is using an outdated image. Rebuild explicitly:
```powershell
docker-compose up -d --build backend
```
