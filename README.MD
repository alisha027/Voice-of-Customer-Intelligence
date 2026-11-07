# VOC Intelligence 360
### Agentic Voice of Customer Intelligence Platform

An AI-powered full-stack application that transforms customer feedback into actionable business insights using OpenAI, LangGraph, PostgreSQL, and React.

---

## 1. Overview

VOC Intelligence 360 enables business stakeholders to analyze customer feedback using natural language instead of writing SQL queries manually.

The platform processes feedback from multiple channels, identifies customer sentiment and recurring issues, retrieves relevant customer comments, and generates executive-level insights.

### Key Features

- Natural Language to SQL generation.
- Greeting and analytical query classification.
- Agentic workflow orchestration using LangGraph.
- SQL validation and error-repair mechanism.
- Customer verbatim extraction.
- Feedback source distribution analysis.
- Executive summaries and actionable recommendations.
- Interactive analytics dashboard.
- Dockerized deployment using Docker Compose.

---

## 2. Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Agent Framework | LangGraph, LangChain |
| LLM Provider | OpenAI GPT-4o-mini |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy |
| API Communication | Axios |
| Deployment | Docker, Docker Compose, Nginx |

---

## 3. System Architecture

The application follows a modular agentic architecture.

```text
              USER QUERY
                  |
                  v
             REACT UI
                  |
                  v
             FASTAPI API
                  |
                  v
           LANGGRAPH WORKFLOW
                  |
                  v
             INTENT ROUTER
                  |
          +-------+-------+
          |               |
          v               v
       GREETING         ANALYSIS
          |               |
          v               v
    DIRECT RESPONSE   SQL GENERATION
                          |
                          v
                     SQL VALIDATION
                          |
                          v
                     SQL EXECUTION
                          |
                          v
                      POSTGRESQL
                          |
                 +--------+--------+
                 |                 |
                 v                 v
             VERBATIM         SOURCE
             EXTRACTION     DISTRIBUTION
                 |                 |
                 +--------+--------+
                          |
                          v
                   EXECUTIVE
                    SYNTHESIS
                          |
                          v
                  STRUCTURED OUTPUT
                          |
                          v
                    REACT UI
```

### Workflow Components

| Component | Responsibility |
|---|---|
| Intent Router | Identifies greeting or analytical intent. |
| SQL Generator | Converts natural language into SQL. |
| SQL Safety | Validates generated queries before execution. |
| SQL Executor | Executes validated queries against PostgreSQL. |
| SQL Repair | Attempts to correct SQL errors and retry. |
| Verbatim Agent | Retrieves relevant customer feedback. |
| Source Distribution Agent | Calculates feedback distribution by channel. |
| Executive Synthesis | Generates summaries and recommendations. |

LangGraph manages workflow state and coordinates the different processing stages.

---

## 4. Database and Dataset

The application uses PostgreSQL with the primary table:

`enriched_unified_data`

Important dataset columns include:

- `uuid`
- `customer_voice`
- `customer_voice_id`
- `data_source_type`
- `engagement_date`
- `product_name`
- `product_family`
- `brand_name`
- `retailer_name`
- `country`
- `maintheme`
- `subtheme`
- `sentiment`
- `sentiment_score`
- `customer_rating`

### Important: Two-Level Data Grain

A single customer interaction can contain multiple topic-level records sharing the same UUID.

Therefore, two different counting rules are important:

**Unique reviews or interactions:**

```sql
COUNT(DISTINCT uuid)
```

**Topic-level mentions:**

```sql
COUNT(*)
```

These metrics represent different business concepts and should not be interchanged.

### Dataset Used

The current development dataset is:

`data/customer_feedback.csv`

Dataset statistics:

- 1,998 rows.
- 1,514 unique feedback UUIDs.
- 29 columns.
- Multiple brands, retailers, and feedback channels.

*Note: The assignment describes an original 5,000-row Excel dataset. The application currently uses the 1,998-row CSV dataset tested during development.*

---

## 5. Project Structure

```text
VOC-Intelligence-360/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── intent_router.py
│   │   │   ├── sql_generator.py
│   │   │   ├── sql_executor_agent.py
│   │   │   ├── sql_repair.py
│   │   │   ├── verbatim_agent.py
│   │   │   ├── source_distribution_agent.py
│   │   │   └── executive_synthesis_agent.py
│   │   │
│   │   ├── core/
│   │   │   └── llm_factory.py
│   │   ├── database/
│   │   │   └── connection.py
│   │   ├── prompts/
│   │   │   └── sql_generation_prompt.py
│   │   ├── services/
│   │   │   ├── sql_safety.py
│   │   │   └── sql_executor.py
│   │   ├── workflows/
│   │   │   ├── state.py
│   │   │   └── graph.py
│   │   └── main.py
│   │
│   ├── ingest_data.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── .dockerignore
│
├── database/
├── data/
│   └── customer_feedback.csv
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 6. API Documentation

The backend is built using FastAPI.

**Base URL:** `http://localhost:8000`

**Swagger Documentation:** `http://localhost:8000/docs`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root endpoint |
| GET | `/health` | Backend health check |
| GET | `/health/database` | Database connectivity |
| GET | `/api/analytics/overview` | Dashboard overview metrics |
| POST | `/api/analysis` | Submit analytical question |

### Example Analytical Request

**Endpoint:**

`POST /api/analysis`

**Request Body:**

```json
{
  "query": "Why are customers complaining about Microsoft Surface battery life?"
}
```

The backend processes the question through the LangGraph workflow and returns the analytical response.

---

## 7. Environment Configuration

Create a `.env` file in the project root.

Copy the example configuration:

```powershell
Copy-Item .env.example .env
```

Configure the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

POSTGRES_DB=voc_db
POSTGRES_USER=voc_admin
POSTGRES_PASSWORD=your_database_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

**Security:**
- Never hardcode API keys.
- Do not commit `.env` to GitHub.
- Keep `.env.example` free of actual credentials.
- Load secrets through environment variables.

---

## 8. Docker Deployment

The application consists of three Docker services:

| Service | Purpose | Port |
|---|---|---|
| db | PostgreSQL | 5432 |
| backend | FastAPI and AI workflow | 8000 |
| frontend | React application with Nginx | 5173 |

### Prerequisites

- Docker Desktop installed.
- Docker Compose available.
- Valid OpenAI API key.

### Step 1: Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd VOC-Intelligence-360
```

### Step 2: Configure Environment

```powershell
Copy-Item .env.example .env
```

Add your OpenAI API key to `.env`.

### Step 3: Build and Start

```bash
docker compose up --build
```

To run in detached mode:

```bash
docker compose up --build -d
```

### Step 4: Verify Containers

```bash
docker compose ps
```

Expected containers:

- `voc_postgres`
- `voc_backend`
- `voc_frontend`

### Step 5: Access the Application

| Component | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Database Health | http://localhost:8000/health/database |

### Step 6: View Logs

```bash
docker compose logs -f
```

For individual services:

```bash
docker compose logs backend
docker compose logs frontend
docker compose logs db
```

### Step 7: Stop Containers

```bash
docker compose down
```

This stops the containers while preserving the named database volume.

**Note:** Avoid `docker compose down -v` unless you intentionally want to delete the database volume and its stored data.

### Fresh Database Setup

If the database is empty, run the ingestion script:

```bash
docker compose exec backend python ingest_data.py
```

Verify database connectivity and record availability before running analytical queries.

---

## 9. Testing

The backend includes individual test scripts for validating the application components.

Run from the backend directory:

```bash
cd backend
python test_workflow.py
```

Other available test scripts include:

```text
test_llm.py
test_sql_layer.py
test_business_queries.py
test_execution_agent.py
test_verbatim.py
test_source_types.py
test_review_candidates.py
test_source_distribution.py
```

### Recommended Business Queries

| Scenario | Example Query |
|---|---|
| Greeting | Hi, what can this platform do? |
| Product Analysis | Why are Surface customers complaining about battery life? |
| Retailer Comparison | Compare Amazon, Best Buy, and Currys UK. |
| AI Feature Analysis | What do customers think about Copilot? |
| Sentiment Analysis | What are the major negative feedback themes? |
| Source Analysis | Which channel contributes the most feedback? |

### SQL Safety

The analytical workflow should reject destructive SQL operations such as:

```sql
DROP TABLE enriched_unified_data;
DELETE FROM enriched_unified_data;
UPDATE enriched_unified_data SET sentiment = 'Positive';
```

Only validated read-only analytical queries should be executed.

---

## 10. Design Decisions

**Why LangGraph?**

It provides state-based workflow orchestration, conditional routing, and support for multi-step AI processes.

**Why PostgreSQL?**

It provides reliable relational storage and supports analytical operations such as filtering, grouping, and aggregation.

**Why GPT-4o-mini?**

It offers a cost-efficient model option for natural language understanding, SQL generation, and response synthesis.

**Why a Modular Agent Architecture?**

Separating responsibilities makes the system easier to maintain, debug, test, and extend.

**Why Docker Compose?**

It simplifies deployment by running the frontend, backend, and database together through a single command.

---

## 11. Scope and Future Enhancements

### Current Scope

- Customer feedback analysis.
- Sentiment and theme analysis.
- Retailer and product comparisons.
- Customer verbatim retrieval.
- Source channel distribution.
- Executive-level insight generation.

The assignment explicitly excludes external macroeconomic indicator enrichment. This implementation focuses on customer voice data only.

### Potential Future Enhancements

- User authentication and role-based access.
- Advanced query planning.
- Query caching.
- Automated testing and monitoring.
- Exportable analytical reports.
- Conversation history.
- Improved database indexing for larger datasets.

---

## 12. Conclusion

VOC Intelligence 360 demonstrates how Large Language Models, agentic orchestration, relational databases, and modern frontend technologies can simplify enterprise customer feedback analysis.

By enabling natural language interaction with customer feedback data, the platform helps business stakeholders identify customer pain points, understand sentiment, compare products and retailers, and make data-driven decisions.

**Project:** VOC Intelligence 360  
**Architecture:** Full Stack + Agentic AI  
**Backend:** FastAPI + LangGraph  
**Frontend:** React + Vite  
**Database:** PostgreSQL  
**LLM Provider:** OpenAI  
**Deployment:** Docker Compose