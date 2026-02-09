# Tasks: Phase IV-A – Agentic Containerization

**Input**: plan.md `/plans/4a-plan.md`  
**Prerequisites**: spec.md `/specs/4a-agentic-containerization/spec.md`  

**Tests**: Validate container images, reproducibility, logs  

**Organization**: Tasks are grouped by goal to allow independent implementation and testing  

**Format**: `[ID] [P?] [Story] Description`  
- **[P]**: Can run in parallel  
- **[Story]**: User story / goal mapping  
- **[x]** = not started / placeholder  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize containerization structure and environment  

- [x] T001 [x] Create `docker_agent/` directory with subfolders: `frontend/`, `backend/`, `logs/`  
- [x] T002 [x] Install Gordon AI Agent in local dev environment for container builds  
- [x] T003 [x] [P] Create `.env.example` with variables: `DOCKER_REGISTRY`, `IMAGE_TAG`, `DEBUG`  
- [x] T004 [x] [P] Add `.gitignore` for Docker cache, environment files, IDE settings  

---

## Phase 2: Containerization Tasks

**Goal**: Build frontend and backend containers using Gordon with reproducible setup  

### Frontend Container

- [x] T005 [x] [US1] Create `docker_agent/frontend/Dockerfile` using Gordon  
  - Build Docker image for frontend  
  - Tag image with version/date  
  - Validate container starts and serves static content locally  
- [x] T006 [x] [US1] Create build script `docker_agent/frontend/build.sh`  
  - Logs build output to `docker_agent/logs/frontend_build.log`  
  - Validate exit codes for error handling  
- [x] T007 [x] [US1] Test frontend container locally with `docker run`  
  - Ensure container serves static content  
  - Log results in `docker_agent/logs/frontend_test.log`  

### Backend Container

- [x] T008 [x] [US1] Create `docker_agent/backend/Dockerfile` using Gordon  
  - Build Docker image for backend  
  - Tag image with version/date  
  - Validate container starts and responds to `/health` endpoint  
- [x] T009 [x] [US1] Create build script `docker_agent/backend/build.sh`  
  - Logs output to `docker_agent/logs/backend_build.log`  
  - Validate exit codes and reproducibility  
- [x] T010 [x] [US1] Test backend container locally with `docker run`  
  - Validate API endpoints work correctly  
  - Log results in `docker_agent/logs/backend_test.log`  

### Integration & Automation

- [x] T011 [x] [US2] Create combined build script `docker_agent/build_all.sh`  
  - Sequentially build frontend & backend images  
  - Validate both images after build  
  - Store build info and logs in `docker_agent/logs/`  
- [x] T012 [x] [US2] Add health check scripts:  
  - Frontend: validate static content served  
  - Backend: validate `/health` endpoint returns 200  
  - Logs in `docker_agent/logs/health_checks.log`  
- [x] T013 [x] [US2] Validate images with multiple rebuilds produce same hash  
- [x] T014 [x] [US2] Add cleanup scripts for dangling containers/images  

---

## Phase 3: Polish & Cross-Cutting Concerns

**Purpose**: Ensure observability, documentation, and reproducibility  

- [x] T015 [x] [P] Document full containerization setup in `docker_agent/README.md`  
- [x] T016 [x] [ ] Add logging to all build scripts with timestamps and exit codes  
- [x] T017 [x] [ ] Validate reproducible builds: repeated build produces same image hash  
- [x] T018 [x] [ ] Validate error handling: missing env variables or failed builds properly logged  
- [x] T019 [x] [ ] Update `.env.example` and README to reflect required variables  

---

## Dependencies & Execution Order

- **Phase 1 Setup** → required for all tasks  
- **Phase 2 Containerization** → depends on Phase 1  
- **Phase 3 Polish** → depends on Phase 2  

**Parallel Opportunities**:  
- Phase 1: T003 & T004 can run in parallel  
- Phase 2: T005 & T008 (frontend/backend builds) can run in parallel  
- Phase 3: T015–T019 can run in parallel after Phase 2
