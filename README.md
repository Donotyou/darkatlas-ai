# DarkAtlas AI Asset Management

AI-powered Attack Surface Management system built with FastAPI, PostgreSQL, and LangChain.

---

## Overview

This system ingests, stores, and analyzes internet-facing assets (domains, subdomains, IPs, services, certificates, technologies) using AI-powered analysis via LangChain + Groq (Llama 3).

---

## Tech Stack

- **FastAPI** — REST API framework
- **PostgreSQL** — Asset storage
- **SQLAlchemy** — ORM
- **LangChain + Groq** — AI analysis layer (Llama 3.1 8b)
- **Docker** — Containerization

---

## Setup & Run

### Prerequisites
- Docker Desktop installed and running

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/darkatlas-ai.git
cd darkatlas-ai
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Start everything
```bash
docker-compose up --build
```

### 4. Access the API
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@db:5432/darkatlas` |
| `GROQ_API_KEY` | Groq API key (get from console.groq.com) | `gsk_...` |
| `API_KEY` | Simple API key for auth | `secret123` |

---

## API Endpoints

### Import
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/import/` | Bulk import assets with deduplication |

### AI Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze/query` | Natural language asset search |
| POST | `/analyze/risk` | Risk scoring & summarization |
| POST | `/analyze/enrich` | Asset enrichment & categorization |
| POST | `/analyze/report` | Natural language report generation |

---

## Example Prompts & Outputs

### 1. Natural Language Query
**Request:**
```json
POST /analyze/query
{
  "question": "show me all expired certificates"
}
```
**Output:**
```json
{
  "reasoning": "Looked for certificate assets with expires date prior to today",
  "count": 3,
  "assets": [
    {
      "id": "a17",
      "type": "certificate",
      "value": "CN=api.example.com",
      "metadata": { "expires": "2024-01-02" }
    }
  ]
}
```

### 2. Risk Scoring
**Request:**
```json
POST /analyze/risk
{
  "asset_ids": ["a13", "a15", "a17", "a21"]
}
```
**Output:**
```json
{
  "risk_score": 80,
  "risk_level": "high",
  "findings": [
    "OpenSSH 7.4p1 is outdated and vulnerable",
    "MySQL 5.7.32 is end-of-life",
    "Certificate CN=api.example.com expired in 2024"
  ],
  "summary": "High risk due to outdated services and expired certificates"
}
```

### 3. Asset Enrichment
**Request:**
```json
POST /analyze/enrich
{
  "asset_id": "a6"
}
```
**Output:**
```json
{
  "asset_id": "a6",
  "enrichment": {
    "environment": "production",
    "category": "Network Asset",
    "criticality": "high",
    "suggested_tags": ["prod", "sensitive", "subdomain"],
    "notes": "Highly sensitive subdomain, potential attack target"
  }
}
```

### 4. Report Generation
**Request:**
```json
POST /analyze/report
{
  "filters": {}
}
```
**Output:** Full markdown security report with executive summary, asset breakdown, risk highlights, and recommendations.

---

## Design Decisions & Assumptions

### Deduplication Strategy
Assets are deduplicated by `type + value` combination. Re-importing the same asset updates `last_seen`, merges tags, and resets status to `active` if it was `stale`.

### Merge Strategy for Conflicting Data
When the same asset appears from two sources with different metadata, we merge both metadata objects with the newer source taking precedence.

### Re-appearing Assets
A `stale` asset that appears again in an import is automatically set back to `active`.

### Malformed Records
Invalid records (missing `type` or `value`) are skipped gracefully without crashing the entire batch. Errors are reported in the response.

### AI Grounding
All AI responses are grounded in actual database data. The full asset list is passed to the LLM with explicit instructions not to invent assets.

### LLM Choice
Used **Groq + Llama 3.1 8b** for speed and cost efficiency during development. Can be swapped to `llama3-70b-8192` for higher accuracy in production by changing one line in each chain file.

---

## How to Run Tests

```bash
# Coming soon
docker-compose exec app pytest
```

---

## What I Would Do Next

- Add authentication middleware (JWT)
- Add pagination to list endpoints
- Add relationship graph endpoints
- Upgrade to llama3-70b-8192 for production
- Add CI/CD with GitHub Actions
- Add caching with Redis