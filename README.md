# Pulse — Uptime Monitoring Platform

Pulse is a containerized uptime monitoring platform that checks website availability, records response metrics, and exposes monitoring results through a REST API.

This project demonstrates a complete cloud deployment workflow using **Docker, Kubernetes (K3s), Terraform, AWS EC2, and PostgreSQL**.

---

## Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Database Schema](#database-schema)
- [Prerequisites](#prerequisites)
- [Quickstart](#quickstart)
- [Local Development](#local-development)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Terraform Infrastructure](#terraform-infrastructure)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Security](#security)
- [Future Improvements](#future-improvements)
- [Project Goals](#project-goals)
- [License](#license)

---

## Architecture

```
                    Internet
                       |
                       v
              EC2 Public IP:30000
                       |
                       v
              Kubernetes NodePort
                       |
                       v
                 API Service
                       |
          +------------+------------+
          |                         |
          v                         v
     FastAPI Pod              PostgreSQL Service
          |                         |
          |                         v
          |                  PostgreSQL Pod
          |
          v
     Worker Pod
     (health checks)
          |
          v
     Notifs Service
     (Notifs Pod :8001)
          |
          v
     SendGrid API
     (email alerts)
```

### API Request Flow

```
External Traffic
      |
      v
NodePort :30000
      |
      v
Service :8000
      |
      v
FastAPI Container :8000
```

---

## Tech Stack

| Layer                  | Technology                          |
| ---------------------- | ----------------------------------- |
| Backend                | FastAPI (Python)                    |
| Database               | PostgreSQL                          |
| Notifications          | Notifs service (FastAPI) + SendGrid |
| Containerization       | Docker                              |
| Orchestration          | Kubernetes (K3s)                    |
| Infrastructure as Code | Terraform                           |
| Cloud Provider         | AWS EC2                             |

---

## Features

- REST API for managing monitored websites
- Background worker that performs uptime checks every 5 minutes
- Tracks website availability status, HTTP response codes, response times, and check timestamps
- Email notifications (via a dedicated Notifs service + SendGrid) sent when a monitored site goes down or recovers
- PostgreSQL persistent storage
- Kubernetes Deployments and Services for API, worker, and database
- Kubernetes Secrets for sensitive configuration
- External API access through a Kubernetes NodePort

---

## Database Schema

### `sites`

Stores websites being monitored.

| Column     | Description                   |
| ---------- | ----------------------------- |
| id         | Site ID                       |
| url        | Website URL                   |
| name       | Website name                  |
| is_active  | Whether monitoring is enabled |
| created_at | Creation timestamp            |

### `site_checks`

Stores uptime check results.

| Column           | Description                   |
| ---------------- | ----------------------------- |
| id               | Check ID                      |
| site_id          | Related website (FK → sites)  |
| is_up            | Whether the site responded    |
| response_time_ms | Response time in milliseconds |
| status_code      | HTTP response status          |
| checked_at       | Time of check                 |

Example data:

```
id | site_id | is_up | response_time_ms | status_code
---|---------|-------|-------------------|------------
1  | 1       | true  | 58                | 200
2  | 1       | true  | 60                | 200
```

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (includes Docker Compose)
- [K3s](https://k3s.io/) (or another Kubernetes distribution)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Terraform](https://developer.hashicorp.com/terraform/install)
- An AWS account with credentials configured (`aws configure`)

---

## Quickstart

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/pulse.git
cd pulse

# 2. Set up your environment variables
cp .env.example .env

# 3. Build and start everything (api, worker, notifs, postgres)
docker compose up --build

# 4. Check it's alive
curl http://localhost:8000/health
```

---

## Local Development

Pulse is made up of four services defined in `docker-compose.yml`: the **API**, the **worker**, the **notifs** service, and **PostgreSQL**.

### Start Everything

This builds and starts all services together, wired up with the networking and environment variables they need.

```bash
docker compose up --build -d
```

To stop everything:

```bash
docker compose down
```

To view logs for a specific service:

```bash
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f notifs
```

The API will be available at:

```
http://localhost:8000
```

The notifs service will be available internally (and locally, if port-mapped in `docker-compose.yml`) at:

```
http://localhost:8001
```

---

## Kubernetes Deployment

Apply the Kubernetes manifests:

```bash
kubectl apply -f k8s/
```

Check deployment status:

```bash
kubectl get pods
kubectl get services
```

View logs:

```bash
kubectl logs deployment/api
kubectl logs deployment/worker
kubectl logs deployment/notifs
```

---

## Terraform Infrastructure

Terraform provisions the AWS infrastructure (EC2 instance, networking, security groups).

```bash
# Initialize providers and modules
terraform init

# Preview changes
terraform plan

# Apply infrastructure
terraform apply

# Tear down infrastructure
terraform destroy
```

---

## Environment Variables

Sensitive configuration is managed using Kubernetes Secrets and excluded from source control.

| Variable            | Description                                                                         |
| ------------------- | ----------------------------------------------------------------------------------- |
| `POSTGRES_USER`     | PostgreSQL username                                                                 |
| `POSTGRES_PASSWORD` | PostgreSQL password                                                                 |
| `POSTGRES_DB`       | PostgreSQL database name                                                            |
| `DB_HOST`           | Database host (internal DNS)                                                        |
| `DB_PORT`           | Database port                                                                       |
| `SENDGRID_API_KEY`  | API key used by the notifs service to send email via SendGrid                       |
| `ALERT_FROM_EMAIL`  | Sender address for down/up alerts                                                   |
| `ALERT_TO_EMAIL`    | Recipient address for down/up alerts                                                |
| `NOTIFS_URL`        | Internal URL the worker calls to trigger a notification (e.g. `http://notifs:8001`) |

Example (as used in Kubernetes Secrets/ConfigMap):

```yaml
POSTGRES_USER: postgres
POSTGRES_PASSWORD: postgres
POSTGRES_DB: pulse
DB_HOST: host
DB_PORT: "5432"
SENDGRID_API_KEY: api-key-here
ALERT_FROM_EMAIL: email@gmail.com
ALERT_TO_EMAIL: email@gmail.com
NOTIFS_URL: http://notifs:8001
```

---

## API Endpoints

### Health Check

```
GET /health
```

```bash
curl http://<EC2_PUBLIC_IP>:30000/health
```

### Get Monitored Sites

```
GET /sites
```

```bash
curl http://<EC2_PUBLIC_IP>:30000/sites
```

---

## Security

- Secrets are stored using Kubernetes Secrets, never committed to source control
- The database is only reachable internally through Kubernetes networking (not exposed externally)
- Infrastructure is provisioned and versioned through Terraform
- `.gitignore` excludes sensitive files (`.tfstate`, `.env`, credentials)

---

## Future Improvements

- [ ] Add GitLab CI/CD for automated deployments
- [ ] Add a frontend dashboard
- [ ] Add user authentication
- [ ] Add monitoring/alerting dashboards (e.g., Grafana)
- [ ] Add database backups
- [ ] Replace NodePort with an Ingress controller or Load Balancer

---

## Project Goals

This project demonstrates:

- Cloud infrastructure automation
- Containerization with Docker
- Kubernetes deployment and networking
- Backend API development
- Database integration
- End-to-end DevOps workflows
