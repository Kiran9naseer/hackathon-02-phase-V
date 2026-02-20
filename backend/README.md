---
title: Todo Backend
emoji: 📋
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Todo Backend API

This is a FastAPI-based todo application backend deployed on Hugging Face Spaces.

## Configuration

- Port: 7860 (default for Hugging Face Spaces)
- Framework: FastAPI with SQLModel and Neon Database (PostgreSQL-compatible)
- Authentication: JWT-based

## Features

- **User Management**: Secure registration and authentication using JWT.
- **Task Management**: Advanced CRUD operations with priorities, categories, and tags.
- **Recurring Tasks**: Automated task generation for daily, weekly, and monthly routines.
- **Due Date Reminders**: Intelligent scheduling via Dapr with fallback background polling.
- **Event-Driven Architecture**: High-performance event streaming using Kafka (`aiokafka`).
- **Real-Time Updates**: Live notification broadcasting through Server-Sent Events (SSE).
- **Background Maintenance**: Automated overdue task detection and system health checks.

## Tech Stack

- **API**: FastAPI
- **ORM**: SQLModel / SQLAlchemy
- **Database**: Neon (PostgreSQL)
- **Messaging**: Kafka
- **Orchestration**: Dapr (for workflows and reminders)
- **Deployment**: Docker / Hugging Face Spaces

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
