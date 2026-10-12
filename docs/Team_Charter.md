# Pet Adoption & Management System  DevOps Team Charter

## 1. Project Purpose & System Overview
The **Pet Adoption & Management System** is a production-grade web application and DevOps automation laboratory designed to manage pet registrations and adoption workflows. The system features:
- **Persistent Data Layer**: Backed by SQLite via SQLAlchemy 2.0 ORM (`database.py`, `models.py`), ensuring reliable ACID transactions and data persistence across server restarts.
- **Frontend Architecture Separation**:
  - **Public Adoption Portal (`static/index.html`)**: Dedicated catalog interface for adopters to browse available pets, filter by species/status, and submit adoption requests. Strictly sanitized of all administrative controls.
  - **Administrative Operations Dashboard (`static/admin.html`)**: Secure, isolated operations dashboard providing real-time KPI metrics, application review queues (approving/rejecting with automatic pet status cascade), and pet inventory management (create, delete, toggle availability).
- **Automated Verification**: End-to-end Pytest suite verifying healthchecks, CRUD operations, cascade mechanics, error handling, and lifecycle transitions.
- **DevOps CI/CD & Cloud Orchestration**: Fully automated delivery pipeline using Git, Docker, Jenkins, and Kubernetes.

---

## 2. Team Member Roles & File Assignments (10 Members / 20 Files)

| Role ID | Member Name | Role Title | Key Responsibilities | Assigned File(s) | Technologies |
|---|---|---|---|---|---|
| **S1** | Sagar | Product Owner / Team Lead | Project architecture, charter, team coordination, system specifications | `docs/Team_Charter.md`<br>`docs/Project_Architecture.md` | Markdown, Mermaid |
| **S2** | Neal | Developer 1 (Data Layer & Pets) | SQLAlchemy engine, session management, ORM models, pet registration & query router | `database.py`<br>`models.py`<br>`routers/__init__.py`<br>`routers/pets.py` | Python, FastAPI, SQLAlchemy 2.0 |
| **S3** | Yash | Developer 2 (Adoptions & Public UI) | Adoption request workflow router, public adoption web portal | `routers/adoptions.py`<br>`static/index.html` | Python, FastAPI, HTML5, CSS3, JavaScript |
| **S4** | Harshwardhan | Developer 3 (Admin API & Admin UI) | Application entrypoint, admin router, dedicated admin operations dashboard | `main.py`<br>`routers/admin.py`<br>`static/admin.html` | Python, FastAPI, HTML5, CSS3, JavaScript |
| **S5** | Jyotiraditya | QA Engineer | Dependency management, automated test suite with isolated SQLite fixtures | `requirements.txt`<br>`test_main.py` | Pytest, HTTPX, Python |
| **S6** | Atharv | Git Engineer | Version control hygiene, repository ignore rules (excluding runtime DBs) | `.gitignore` | Git, GitHub |
| **S7** | Omkar | Jenkins Engineer | Multi-stage CI/CD pipeline automation (build, test, containerize, deploy) | `Jenkinsfile` | Jenkins, Declarative Pipeline |
| **S8** | Siddhik | Docker Engineer | Container image packaging, build optimization, container ignore rules | `Dockerfile`<br>`.dockerignore` | Docker, Alpine Linux |
| **S9** | Tanishq | Kubernetes Engineer | Production deployment manifests, replica management, LoadBalancer networking | `k8s/deployment.yaml`<br>`k8s/service.yaml` | Kubernetes, YAML |
| **S10** | Rushikesh | DevOps/SRE Engineer | Production system documentation, operational guides, API catalogs, deployment runbooks | `README.md` | Markdown |

---

## 3. Architecture & Separation Guidelines
1. **Database Persistence**:
   - `database.py` defines the SQLite engine with `check_same_thread=False` and `SessionLocal`.
   - All router endpoints access the database via FastAPI `Depends(get_db)`.
   - Runtime databases (`*.db`, `*.sqlite`, `*.sqlite3`) are strictly excluded from source control and container images via `.gitignore` and `.dockerignore`.
2. **Frontend UI Separation**:
   - `static/index.html` must remain strictly client-facing. No administrative API calls (`/admin/*`), status mutations, or management controls are permitted.
   - `static/admin.html` serves as the centralized back-office dashboard, interacting with `/admin/dashboard`, `/admin/adoptions/{id}`, and pet management endpoints.
3. **Distribution Integrity**:
   - Each team member folder in `team_distribution_v2/` must contain only that member's designated files.
   - Zero file overlap, zero omissions, and zero runtime artifact leakage (`__pycache__`, `.pytest_cache`, `.db`).
