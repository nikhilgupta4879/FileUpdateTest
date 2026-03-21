# CanUDartMe — Windows Step-by-Step: Option A (Docker)

> **Start here after Docker Desktop is installed and verified running**
> (Whale icon in system tray shows "Engine running")

---

## Step 1 — Open PowerShell

Press `Win + X` → click **"Windows PowerShell"** or **"Terminal"**

Verify Docker is working:

```powershell
docker --version
docker compose version
```

Expected output (versions may differ):
```
Docker version 26.x.x
Docker Compose version v2.x.x
```

If either command fails, Docker Desktop is not fully started — wait 30 seconds and try again.

---

## Step 2 — Connect GitHub and Clone the Repository

> **Important:** GitHub no longer accepts your account password for Git.
> You must create a **Personal Access Token (PAT)** and use it in place of your password.

### 2a — Create a Personal Access Token (PAT)

1. Open your browser and go to: https://github.com/settings/tokens/new
   *(or: GitHub → Profile photo → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token)*

2. Fill in the form:
   - **Note:** `CanUDartMe clone` (any label you like)
   - **Expiration:** 90 days (or No expiration for personal machines)
   - **Scopes:** tick **`repo`** (this covers read/write to all your repositories)

3. Scroll down and click **"Generate token"**

4. **Copy the token immediately** — GitHub shows it only once.
   It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

> Store it somewhere safe (e.g. Notepad, password manager) — you'll need it below.

---

### 2b — Tell Git who you are (first-time setup only)

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

---

### 2c — Clone using your username and token

```powershell
git clone https://YOUR_GITHUB_USERNAME:YOUR_TOKEN@github.com/nikhilgupta4879/CanUDartMe.git
```

**Example** (replace with your real username and token):

```powershell
git clone https://john:ghp_abc123xyz456@github.com/nikhilgupta4879/CanUDartMe.git
```

> The token goes where the password would normally go.

---

### 2d — Alternative: Windows Credential Manager (enter token once, saved automatically)

If you prefer not to put the token in the URL, use the standard clone URL and let Windows save it:

```powershell
git clone https://github.com/nikhilgupta4879/CanUDartMe.git
```

Git will open a login popup:
- **Username:** your GitHub username
- **Password:** paste your PAT (not your GitHub password)

Windows Credential Manager saves this — you won't be asked again on this machine.

---

### 2e — Move into the project folder

```powershell
cd CanUDartMe
```

Confirm you're in the right place:

```powershell
dir
```

You should see: `docker-compose.yml`, `backend`, `frontend`, `README.md`

---

## Step 3 — Create the Backend Environment File

```powershell
copy backend\.env.example backend\.env
```

Open the file in Notepad to review it:

```powershell
notepad backend\.env
```

The file will look like this:

```
SECRET_KEY=supersecretkey-change-in-production
DATABASE_URL=postgresql+asyncpg://canudart:canudart@db:5432/canudartme
REDIS_URL=redis://redis:6379/0
DEBUG=true
DART_TRAVEL_TIME_SECONDS=2.0
```

**Change only this line** — replace the placeholder with any long random string:

```
SECRET_KEY=my-own-secret-key-abc123xyz789
```

> The `DATABASE_URL` and `REDIS_URL` are pre-configured for Docker — **do not change them**.

Save and close Notepad.

---

## Step 4 — Build and Start All Services

```powershell
docker compose up --build
```

**What happens during first run (~3–5 minutes):**

1. Docker downloads `postgres:16-alpine` image
2. Docker downloads `redis:7-alpine` image
3. Docker builds the backend image (installs Python packages)
4. Docker builds the frontend image (installs Flet)
5. PostgreSQL starts, runs health checks
6. Redis starts, runs health checks
7. Backend starts, runs database migrations
8. Frontend starts

**You'll know it's ready when you see lines like:**

```
backend-1   | INFO:     Application startup complete.
frontend-1  | INFO:     Started server process
```

> The terminal stays open and shows live logs — this is normal. Do not close it.

---

## Step 5 — Open the App

Open your browser and go to:

| What | URL |
|------|-----|
| **App (play the game)** | http://localhost:8080 |
| **API docs / Swagger** | http://localhost:8000/docs |
| **Health check** | http://localhost:8000/health |

If `localhost:8080` shows a loading screen for a few seconds, wait — the frontend
container may still be warming up.

---

## Step 6 — Stopping the App

Go back to the PowerShell window running Docker and press:

```
Ctrl + C
```

Then choose one of these depending on your need:

```powershell
# Keep your game data (scores, users) — resume later
docker compose stop

# Remove containers but keep database data on disk
docker compose down

# Remove everything including the database (fresh start)
docker compose down -v
```

---

## Day-to-Day Usage (After First Setup)

Every time you want to run the app again:

```powershell
cd CanUDartMe
docker compose up
```

> No `--build` needed unless you change code or dependencies.

---

## Checking Service Status

In a **second PowerShell window** while the app is running:

```powershell
# Show running containers and their status
docker compose ps

# View logs from a specific service
docker compose logs backend
docker compose logs frontend
docker compose logs db
```

---

## Troubleshooting

### "Port is already allocated"
Something else is using port 8000 or 8080.

```powershell
# Find what is using port 8000
netstat -ano | findstr :8000
# Kill the process (replace 1234 with the PID from above)
taskkill /PID 1234 /F
```

Then run `docker compose up` again.

### "Cannot connect to Docker daemon"
Docker Desktop is not running. Open Docker Desktop from the Start Menu and wait
until the system tray icon shows "Engine running", then retry.

### Backend keeps restarting
Check the logs:
```powershell
docker compose logs backend
```
Most common cause: `backend\.env` file is missing or has a typo. Re-run Step 3.

### Blank page at localhost:8080
Wait 30 seconds — the frontend takes longer to start than the backend.
If still blank, check:
```powershell
docker compose logs frontend
```

### Changes to code not reflected
If you edited source files, rebuild:
```powershell
docker compose up --build
```
