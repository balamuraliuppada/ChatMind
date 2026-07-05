# ChatMinds: Implementation Overview

## 1. Goal Accomplished
Successfully scaffolded **ChatMinds**, a production-ready, anonymous, and temporary real-time chat platform.

## 2. Architecture Implemented
The solution relies on a robust **Modular Architecture** and modern cloud-native patterns.

### Frontend
- **Framework:** React 19 + TypeScript + Vite.
- **Styling:** Tailwind CSS with a stunning dark-mode glassmorphism aesthetic (`index.css` overrides).
- **State Management:** Zustand for lightweight, scalable chat state (`useChatStore.ts`).
- **Real-Time Connectivity:** Socket.IO client, robust handling for `connect`, `new_message`, and typing indicators.
- **Key Views:**
  - `Landing.tsx`: Unified create/join screen with Framer Motion animations.
  - `Room.tsx`: Main chat layout featuring responsive sidebars, smooth scrolling, and dynamic chat bubbles.

### Backend
- **Framework:** FastAPI for high-performance Async HTTP endpoints.
- **Database:** SQLAlchemy 2.0 with asyncpg (PostgreSQL) storing Rooms, Participants, and Messages.
- **Real-Time Server:** Python Socket.IO connected with Redis Pub/Sub for horizontal scaling and multi-worker setups.
- **Authentication:** Tokenless session management using HTTPOnly cookies (JWTs) tied to ephemeral `Participant` UUIDs.
- **Scheduled Tasks:** Integrated `apscheduler` inside FastAPI lifecycle events to automatically clean up expired and inactive rooms.

### Infrastructure & Deployment
- **Dockerized Environment:** 
  - FastAPI Backend Dockerfile (Uvicorn + Gunicorn).
  - React Frontend Dockerfile (Multi-stage build + Nginx).
- **Nginx Reverse Proxy:** `nginx.conf` routing `/api` to the backend, `/socket.io` to WebSocket processes, and `/` to the frontend static server.
- **Docker Compose:** Seamlessly spins up Postgres, Redis, Backend, Frontend, and the Proxy simultaneously.
- **CI/CD:** `deploy.yml` GitHub Actions pipeline covering dependency checking, linting, and build steps.

## 3. How to Run Locally
The entire stack is configured via `docker-compose.yml`. From the project root (`E:\CodeBase\CoolProjects\ChatMinds`), simply execute:
```bash
docker-compose up -d --build
```
Then navigate to:
- **Frontend:** [http://localhost:8080](http://localhost:8080)
- **API Docs:** [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)
