@echo off
REM Windows batch script to start Docker containers

echo ========================================
echo Todo App - Docker Setup
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo [OK] Docker is installed and running
echo.

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo Please edit .env file with your actual values before continuing
    echo Press any key when ready to continue...
    pause >nul
)

echo Building and starting containers...
echo.

REM Build and start containers
docker-compose up --build -d

REM Wait for services to start
echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

REM Check if containers are running
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo.
    echo Error: Containers failed to start
    echo Check logs with: docker-compose logs
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo [OK] Application is running!
    echo ========================================
    echo.
    echo Frontend: http://localhost:3000
    echo Backend API: http://localhost:8000
    echo API Docs: http://localhost:8000/docs
    echo.
    echo To view logs: docker-compose logs -f
    echo To stop: docker-compose down
    echo.
    pause
)
