# CanUDartMe — Windows Deployment & Runtime Guide

Two ways to run on Windows:
- **Option A (Recommended):** Docker Desktop — one command, everything containerized
- **Option B:** Manual setup — run each service natively on Windows

---

## Prerequisites

### Common (both options)
| Tool | Version | Download |
|------|---------|----------|
| Git | Latest | https://git-scm.com/download/win |
| Python | 3.12+ | https://www.python.org/downloads/ |

> During Python install, check **"Add Python to PATH"**

---

## Option A — Docker Desktop (Recommended)

### 1. Install Docker Desktop

1. Download from https://www.docker.com/products/docker-desktop/
2. Run the installer (requires Windows 10/11 with WSL 2)
3. During install, enable **"Use WSL 2 instead of Hyper-V"**
4. Restart your PC when prompted
5. Open Docker Desktop and wait until the whale icon in the taskbar shows **"Running"**

### 2. Enable WSL 2 (if not already enabled)

Open **PowerShell as Administrator** and run:

```powershell
wsl --install
wsl --set-default-version 2
```

Restart if prompted.

### 3. Clone the repository

```powershell
git clone https://github.com/nikhilgupta4879/CanUDartMe.git
cd CanUDartMe
```

### 4. Configure environment

```powershell
copy .env.example backend\.env
```

Edit `backend\.env` and set a strong `SECRET_KEY`:

```
SECRET_KEY=my-strong-random-secret-key-here
```

### 5. Start all services

```powershell
docker compose up --build
```

First run downloads images and builds containers (~3–5 minutes). Subsequent starts are fast.

### 6. Access the app

| Service | URL |
|---------|-----|
| **Web App (Frontend)** | http://localhost:8080 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |

### 7. Stop the app

```powershell
# Stop (keep data)
docker compose stop

# Stop and remove containers
docker compose down

# Stop and wipe database
docker compose down -v
```

---

## Option B — Manual Setup (No Docker)

### Step 1 — Install PostgreSQL

1. Download from https://www.postgresql.org/download/windows/
2. Run the installer (default port **5432**)
3. Set a password for the `postgres` superuser
4. After install, open **pgAdmin** or **psql** and run:

```sql
CREATE USER canudart WITH PASSWORD 'canudart';
CREATE DATABASE canudartme OWNER canudart;
```

### Step 2 — Install Redis

Redis does not have an official Windows build. Use one of these:

**Option 2a — Redis via WSL (easiest):**
```powershell
# In PowerShell (requires WSL already installed)
wsl --install -d Ubuntu
wsl
# Inside WSL:
sudo apt update && sudo apt install -y redis-server
redis-server --daemonize yes
```

**Option 2b — Memurai (Windows-native Redis compatible):**
1. Download from https://www.memurai.com/
2. Install and start — it runs as a Windows Service on port 6379

### Step 3 — Set up the Backend

Open a new **PowerShell** window:

```powershell
cd CanUDartMe\backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# If you get an execution policy error, run first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

pip install -r requirements.txt
```

Configure environment:

```powershell
copy .env.example .env
```

Edit `.env` — update these values for your local setup:

```env
SECRET_KEY=my-strong-random-secret-key-here
DATABASE_URL=postgresql+asyncpg://canudart:canudart@localhost:5432/canudartme
REDIS_URL=redis://localhost:6379/0
DEBUG=true
```

Run database migrations:

```powershell
alembic upgrade head
```

Start the backend server:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend is now running at http://localhost:8000

### Step 4 — Set up the Frontend

Open a **second PowerShell** window:

```powershell
cd CanUDartMe\frontend

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Set environment variables (PowerShell):

```powershell
$env:API_BASE_URL = "http://localhost:8000"
$env:WS_BASE_URL  = "ws://localhost:8000"
```

**Run as Web app (browser):**

```powershell
flet run --web --port 8080 app/main.py
```

Open http://localhost:8080 in your browser.

**Run as Desktop app (native window):**

```powershell
flet run app/main.py
```

---

## Build Mobile Apps (Android / iOS)

### Android APK (from Windows)

```powershell
# Install Android requirements
# 1. Install Flutter SDK: https://docs.flutter.dev/get-started/install/windows
# 2. Install Android Studio: https://developer.android.com/studio
# 3. Run: flutter doctor   (fix any issues shown)

cd CanUDartMe\frontend

# Build APK
flet build apk

# Output: build\apk\app-release.apk
# Transfer to Android device and install
```

### iOS IPA (requires a Mac)

iOS builds cannot be done on Windows — you need macOS + Xcode.
Options:
- Use a Mac, run `flet build ipa`
- Use a Mac cloud build service (e.g. MacStadium, GitHub Actions with `macos-latest`)

---

## Running Tests

```powershell
cd CanUDartMe\backend
.venv\Scripts\Activate.ps1
pytest tests\ -v
```

---

## Troubleshooting

### Docker: "WSL 2 installation is incomplete"
```powershell
# Run as Administrator
wsl --update
wsl --set-default-version 2
```
Then restart Docker Desktop.

### Docker: Port already in use
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000
# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### Python: `flet` command not found
```powershell
# Make sure venv is activated (you should see (.venv) in prompt)
.venv\Scripts\Activate.ps1
# Then retry
```

### PowerShell: Execution policy error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### PostgreSQL: Connection refused
- Ensure PostgreSQL service is running:
  ```powershell
  Get-Service postgresql*
  Start-Service postgresql-x64-16   # adjust version
  ```

### Redis: Connection refused
- If using WSL Redis, ensure it's running:
  ```powershell
  wsl redis-cli ping   # should return PONG
  wsl redis-server --daemonize yes   # start if not running
  ```

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | *(change this)* | JWT signing key — use a long random string in production |
| `DATABASE_URL` | `postgresql+asyncpg://canudart:canudart@db:5432/canudartme` | PostgreSQL connection |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection |
| `DEBUG` | `false` | Enable verbose logging |
| `DART_TRAVEL_TIME_SECONDS` | `2.0` | Default dart travel time (0.5–2.0) |
| `API_BASE_URL` | `http://localhost:8000` | Frontend → Backend HTTP base URL |
| `WS_BASE_URL` | `ws://localhost:8000` | Frontend → Backend WebSocket base URL |

---

## Quick Reference Card

```
# Docker (easiest)
docker compose up --build        → start everything
docker compose stop              → stop
docker compose down -v           → stop + wipe data

# Manual — start order matters:
1. Start PostgreSQL (Windows Service)
2. Start Redis (WSL or Memurai)
3. cd backend  → uvicorn app.main:app --reload --port 8000
4. cd frontend → flet run --web --port 8080 app/main.py

# Tests
cd backend && pytest tests\ -v

# Mobile
cd frontend && flet build apk    → Android
cd frontend && flet build ipa    → iOS (Mac only)
```
