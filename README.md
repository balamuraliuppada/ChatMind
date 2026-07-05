# ChatMinds 💬

**Anonymous, temporary, secure.** ChatMinds is a full-stack, production-ready real-time chat platform where users create temporary private chat rooms and share a room code with others.

## Features
- **No Signup/Login**: Instant access without accounts.
- **Temporary Sessions**: Secure HttpOnly cookies for session management.
- **Real-Time Communication**: Powered by WebSockets (Socket.IO).
- **Auto-Deletion**: Rooms and messages are automatically purged after 24 hours or 30 minutes of inactivity.
- **Modern UI**: Stunning glassmorphism design with Tailwind CSS and Framer Motion.
- **Production Ready**: Fully Dockerized, Redis pub/sub, Nginx load balancing, and Async PostgreSQL.

## Architecture

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Zustand, TanStack Query, Socket.IO Client.
- **Backend**: FastAPI, Python Socket.IO, SQLAlchemy 2.0 (asyncpg), PostgreSQL, Redis, Uvicorn, Gunicorn.
- **Infrastructure**: Docker Compose, Nginx, GitHub Actions CI/CD.

## Quickstart

1. **Clone the repository** (or navigate to the project directory)
2. **Start the environment with Docker Compose**:
   ```bash
   docker-compose up -d --build
   ```
3. **Access the application**:
   - Frontend: http://localhost:8080 (Served via Nginx)
   - Backend API Docs: http://localhost:8000/api/v1/openapi.json

## Deployment

The application is fully containerized and deployable to services like Render, Railway, AWS ECS, or DigitalOcean Droplets.
A GitHub Actions CI/CD workflow is included in `.github/workflows/deploy.yml`.

### Environment Variables
Production deployments require configuring the `.env` file (passed into Docker):
- `DATABASE_URL`: Your PostgreSQL connection string.
- `REDIS_URL`: Your Redis connection string.
- `SECRET_KEY`: A highly secure random string for JWT signing.
- `CORS_ORIGINS`: Allowed origins (e.g., `https://yourdomain.com`).

## Documentation
- ER Diagram / Models: Rooms (1) -> (M) Participants, Rooms (1) -> (M) Messages.
- Clean Architecture: Backend split into `api/`, `core/`, `models/`, `schemas/`, `services/`, and `socket/`.
