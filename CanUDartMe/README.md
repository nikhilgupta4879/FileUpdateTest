# CanUDartMe 🎯

A real-time multiplayer dart game playable on **Web, iOS, and Android** from a single Python codebase.

---

## Tech Stack

| Layer        | Technology                           |
|--------------|--------------------------------------|
| Backend      | Python 3.12 + FastAPI                |
| Real-time    | WebSockets (FastAPI) + Redis Pub/Sub |
| Database     | PostgreSQL 16 + SQLAlchemy 2 (async) |
| Migrations   | Alembic                              |
| Auth         | JWT (python-jose + bcrypt)           |
| Frontend     | **Flet** (Python → Flutter → Web / iOS / Android) |
| Infra        | Docker Compose                       |

---

## Project Structure

```
CanUDartMe/
├── backend/                   # FastAPI app
│   ├── app/
│   │   ├── core/              # Config, DB, Security
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── api/
│   │   │   ├── v1/            # REST: auth, users, groups, sessions
│   │   │   └── websocket.py   # Real-time game WebSocket handler
│   │   ├── services/
│   │   │   ├── game_engine.py # Core game logic (stateless)
│   │   │   ├── group_service.py
│   │   │   └── session_service.py
│   │   └── redis/             # Pub/Sub helpers
│   ├── alembic/               # DB migrations
│   └── tests/                 # Pytest unit tests
│
├── frontend/                  # Flet cross-platform app
│   ├── app/
│   │   ├── main.py            # Entry point + routing
│   │   ├── pages/
│   │   │   ├── auth/          # Login / Register
│   │   │   ├── lobby/         # Sessions list, Groups, Friends
│   │   │   └── game/          # In-game screen (throw + catch)
│   │   ├── components/        # DartBoard, Scoreboard widgets
│   │   ├── services/          # HTTP + WebSocket clients
│   │   └── utils/             # Constants, animations
│   └── assets/                # Images, sounds
│
└── docker-compose.yml
```

---

## Game Rules

| Scenario            | Outcome                                                         |
|---------------------|-----------------------------------------------------------------|
| Dart **caught**     | Catcher gets points (Inner 30 / Middle 20 / Outer 10); Thrower gets 1 strike |
| Dart **missed**     | Thrower gets 10 pts; Catcher gets 1 strike                      |
| 3 strikes           | Player eliminated                                               |
| 3 rounds completed  | Highest score among survivors wins                              |
| Travel time         | Configurable per session (0.5 s – 2.0 s)                       |
| Max players         | 6 per session                                                   |

---

## Quick Start

### 1. Clone & configure

```bash
cp .env.example backend/.env
# Edit backend/.env with your secrets
```

### 2. Run with Docker Compose

```bash
docker compose up --build
```

| Service      | URL                          |
|--------------|------------------------------|
| Backend API  | http://localhost:8000/docs   |
| Frontend Web | http://localhost:8080        |
| Health check | http://localhost:8000/health |

### 3. Run frontend locally (without Docker)

```bash
cd frontend
pip install -r requirements.txt
flet run --web app/main.py          # web browser
flet run app/main.py                # desktop
```

### 4. Build mobile apps

```bash
cd frontend
flet build apk     # Android
flet build ipa     # iOS (requires macOS + Xcode)
```

### 5. Run backend tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/
```

---

## WebSocket Events

### Client → Server
| Event        | Payload                                       |
|--------------|-----------------------------------------------|
| `throw_dart` | `{ target_user_id, dart_type }`               |
| `catch_dart` | `{ region: "inner" \| "middle" \| "outer" }` |

### Server → All Clients (broadcast)
| Event           | Description                                     |
|-----------------|-------------------------------------------------|
| `player_joined` | New player entered the session                  |
| `player_left`   | Player disconnected                             |
| `dart_thrown`   | Dart is in flight → starts countdown on target  |
| `dart_caught`   | Target caught the dart + updated scoreboard     |
| `dart_missed`   | Timer expired + updated scoreboard              |
| `game_over`     | Game finished with winner + final scores        |

---

## REST API Summary

| Method | Path                              | Description                        |
|--------|-----------------------------------|------------------------------------|
| POST   | `/api/v1/auth/register`           | Register new player                |
| POST   | `/api/v1/auth/token`              | Login → JWT                        |
| GET    | `/api/v1/users/me`                | Get current player profile         |
| GET    | `/api/v1/users/search`            | Find friend by profile name        |
| POST   | `/api/v1/groups/`                 | Create a group                     |
| GET    | `/api/v1/groups/search`           | Search public groups               |
| POST   | `/api/v1/groups/join`             | Join a group (max 6 members)       |
| POST   | `/api/v1/groups/{id}/favorite`    | Toggle favorite group              |
| GET    | `/api/v1/sessions/`               | List active sessions (favorites first) |
| POST   | `/api/v1/sessions/`               | Create a new game session          |
| WS     | `/ws/session/{id}?token=JWT`      | Join game WebSocket                |

---

## Roadmap

- [ ] Animated dart throw (Flet Lottie / custom Canvas)
- [ ] Push notifications (FCM for mobile)
- [ ] Friend list & private group invites
- [ ] Leaderboard (global + group)
- [ ] Sound effects on catch/miss
- [ ] Configurable dart skins
- [ ] Spectator mode
