# Docker Deployment Guide

This guide explains how to run the Todo Full-Stack Application using Docker containers.

## 📋 Prerequisites

- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- Docker Compose (included with Docker Desktop)

## 🏗️ Architecture

The application consists of two separate Docker containers:

1. **Backend Container** (FastAPI)
   - Port: 8000 (maps to internal port 7860)
   - Database: SQLite with persistent volume
   - Health checks enabled

2. **Frontend Container** (Next.js)
   - Port: 3000
   - Optimized multi-stage build
   - Standalone output mode

## 🚀 Quick Start

### 1. Set Up Environment Variables

Copy the example environment file and configure your values:

```bash
cp .env.example .env
```

Edit `.env` and add your actual values:
- `SECRET_KEY`: Your JWT secret key
- `BETTER_AUTH_SECRET`: Your Better Auth secret
- `GEMINI_API_KEY`: Your Google Gemini API key (for AI features)
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: (Optional) For Google OAuth

### 2. Build and Run with Docker Compose

Build and start both containers:

```bash
docker-compose up --build
```

Or run in detached mode (background):

```bash
docker-compose up -d --build
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Stop the Application

```bash
docker-compose down
```

To also remove volumes (database data):

```bash
docker-compose down -v
```

## 🔧 Individual Container Commands

### Backend Only

Build:
```bash
docker build -t todo-backend ./backend
```

Run:
```bash
docker run -p 8000:7860 \
  -e SECRET_KEY=your-secret-key \
  -e GEMINI_API_KEY=your-api-key \
  -v backend-data:/app/data \
  todo-backend
```

### Frontend Only

Build:
```bash
docker build -t todo-frontend ./frontend
```

Run:
```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  todo-frontend
```

## 📊 Useful Docker Commands

### View Running Containers
```bash
docker ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### Execute Commands in Container
```bash
# Backend shell
docker-compose exec backend /bin/bash

# Frontend shell
docker-compose exec frontend /bin/sh
```

### Check Container Health
```bash
docker-compose ps
```

## 🗄️ Database Management

The backend uses SQLite with a persistent volume. The database file is stored in the `backend-data` volume.

### Access Database
```bash
docker-compose exec backend sqlite3 /app/data/todo.db
```

### Backup Database
```bash
docker cp todo-backend:/app/data/todo.db ./backup-$(date +%Y%m%d).db
```

### Run Migrations
```bash
docker-compose exec backend alembic upgrade head
```

## 🔍 Troubleshooting

### Port Already in Use
If ports 3000 or 8000 are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # Frontend on port 3001
  - "8001:7860"  # Backend on port 8001
```

### Container Won't Start
Check logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Database Issues
Reset the database volume:
```bash
docker-compose down -v
docker-compose up --build
```

### Frontend Can't Connect to Backend
Ensure the `NEXT_PUBLIC_API_URL` environment variable is set correctly in `docker-compose.yml`.

## 🛠️ Development Mode

For development with hot-reload, uncomment the volume mount in `docker-compose.yml`:

```yaml
volumes:
  - ./backend:/app  # Uncomment this line
```

Then rebuild:
```bash
docker-compose up --build
```

## 🚢 Production Deployment

For production:

1. Update environment variables in `.env`
2. Remove development volume mounts
3. Use production-ready secrets
4. Consider using a production database (PostgreSQL)
5. Set up reverse proxy (nginx)
6. Enable HTTPS

### Production Build
```bash
docker-compose -f docker-compose.yml up -d --build
```

## 📝 Environment Variables Reference

### Backend
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `CORS_ORIGINS`: Allowed CORS origins
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
- `GEMINI_API_KEY`: Google Gemini API key

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `BETTER_AUTH_SECRET`: Better Auth secret key
- `BETTER_AUTH_URL`: Better Auth URL
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID`: Google OAuth client ID

## 🎯 Next Steps

1. Configure your environment variables
2. Run `docker-compose up --build`
3. Access the application at http://localhost:3000
4. Create an account and start managing your todos!

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Next.js Docker Documentation](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Documentation](https://fastapi.tiangolo.com/deployment/docker/)
