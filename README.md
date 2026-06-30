# BoardroomIQ

**Autonomous Multi-Agent Business Intelligence Platform for Evidence-Based Executive Decision Making**

BoardroomIQ turns business spreadsheets into an AI-powered board meeting. Instead of producing a single generic chatbot answer, it profiles the uploaded data, routes the question to specialized agents, verifies claims with computed evidence, ranks the strongest causes, and produces an executive decision brief.

## Why This Project

Most CSV chatbots answer from one general model perspective.

BoardroomIQ works more like a structured decision-intelligence system:

```text
Business Question
        |
Uploaded CSV / Excel Data
        |
Data Profiler Agent
        |
Planner + Specialist Agents
        |
Debate + Verification
        |
Judge + Forecast
        |
CEO Decision Brief
```

Example question:

> Why did revenue drop this quarter and what should we do?

BoardroomIQ can analyze sales, customer, inventory, marketing, or onboarding data and return:

- ranked business causes
- supporting evidence
- confidence scores
- risk labels
- forecast/trend signals
- recommended next actions

## Key Features

- **Flexible CSV/Excel Uploads**  
  Supports `.csv`, `.xlsx`, `.xls`, single-sheet files, and multi-sheet Excel workbooks.

- **Data Profiler Agent**  
  Detects rows, columns, date fields, revenue fields, spend fields, conversion fields, source fields, and status fields.

- **Specialized Business Agents**  
  Finance, Marketing, Operations, Risk, Customer/Onboarding, Trend, Forecast, Debate, Verification, Judge, and CEO agents.

- **Evidence-Based Claims**  
  Agents use Pandas/NumPy calculations instead of relying only on LLM-style assumptions.

- **Debate and Verification Layer**  
  Agent claims are challenged, checked against available metrics, and ranked by confidence.

- **Decision Timeline**  
  Shows how the system moved from planning to analysis, debate, verification, ranking, forecast, and final summary.

- **Executive Decision Brief**  
  Presents the primary cause, next recommended move, watch signal, risk, and optional full summary.

## Example Use Cases

### Revenue Drop Analysis

Upload:

- `sales.csv`
- `customers.csv`
- `inventory.csv`
- `marketing.csv`

Ask:

> Why did revenue drop this quarter?

BoardroomIQ identifies whether the decline is mainly driven by revenue/margin pressure, conversion drop, stockouts, churn, or product dependency.

### Customer Onboarding / Conversion Analysis

Upload one sheet such as `onboarding.csv`.

Ask:

> How many booked customers did not convert, and can we estimate CAC?

BoardroomIQ can detect:

- total booked records
- booked but not converted count
- conversion rate
- status breakdown
- source/channel distribution
- CAC when spend and conversion columns exist
- timeline dips when a date column exists

## Agent Architecture

| Agent | Role |
|---|---|
| Data Profiler Agent | Detects available fields and determines what analysis is possible |
| Planner Agent | Breaks the business question into analysis tasks |
| Finance Agent | Analyzes revenue, cost, margin, and payment signals |
| Marketing Agent | Analyzes spend, conversions, source/channel performance, and CAC |
| Operations Agent | Analyzes inventory, stockouts, demand gaps, and fulfillment risk |
| Risk Agent | Analyzes churn, repeat customers, concentration, and dependency risks |
| Customer / Onboarding Agent | Analyzes bookings, conversion status, and customer funnel movement |
| Flexible Trend Agent | Detects dips or growth across time-based records |
| Debate Agent | Challenges each agent's claim |
| Verification Agent | Checks whether claims are supported by computed evidence |
| Judge Agent | Ranks strongest explanations by confidence |
| Forecast Agent | Projects near-term revenue or volume trends |
| CEO Agent | Converts findings into an executive recommendation |

## Tech Stack

**AI / Agent Logic**

- Python
- Multi-agent workflow design
- Evidence-based reasoning

**Analytics**

- Pandas
- NumPy
- Scikit-learn

**Backend**

- FastAPI
- Uvicorn

**Frontend**

- React
- Vite
- Recharts
- Lucide React

**Prototype UI**

- Streamlit

## Project Structure

```text
BoardroomIQ/
├── boardroomiq/
│   ├── agents/
│   ├── analytics/
│   ├── core/
│   ├── utils/
│   └── api.py
├── data/
│   └── sample/
├── frontend/
│   └── src/
├── app.py
├── requirements.txt
└── README.md
```

## How To Run

### 1. Backend

From the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn boardroomiq.api:app --port 8000
```

Backend runs at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

### 2. Frontend

Open a second terminal:

```powershell
cd frontend
& "C:\Program Files\nodejs\npm.cmd" run build
& "C:\Program Files\nodejs\npm.cmd" run preview -- --port 5173
```

Frontend runs at:

```text
http://127.0.0.1:5173
```

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Backend health check |
| `/api/analyze/sample` | POST | Run analysis on bundled sample datasets |
| `/api/analyze/upload` | POST | Upload CSV/Excel files and run flexible analysis |

## Sample Data

Sample files are included in `data/sample`:

- `sales.csv`
- `customers.csv`
- `inventory.csv`
- `marketing.csv`
- `onboarding.csv`

The onboarding sample is useful for testing customer booking, conversion, CAC, and funnel-drop questions.

## How This Is Different From Uploading CSVs To ChatGPT/Claude

Uploading a CSV to a general chatbot usually produces one conversational answer.

BoardroomIQ creates a repeatable decision workflow:

- profiles the data first
- chooses relevant agents based on available columns
- computes real metrics
- challenges claims through debate
- verifies evidence
- ranks causes
- exposes the decision timeline
- produces an executive recommendation

The goal is not just to answer a question. The goal is to show **how the decision was reached**.

## Current Status

**Version:** MVP / Product Prototype

Completed:

- multi-agent analytics pipeline
- flexible CSV/Excel uploads
- sample and custom-data analysis modes
- FastAPI backend
- React dashboard frontend
- Streamlit prototype
- evidence, confidence, debate, verification, forecast, and CEO summary layers

Planned:

- OpenAI/LangChain explanation layer
- LangGraph orchestration
- exportable PDF report
- automated tests
- Docker setup
- deployment
- screenshots and demo video

## Resume Summary

**BoardroomIQ: Autonomous Multi-Agent Business Intelligence Platform**

Built an agentic AI business intelligence platform that analyzes CSV/Excel business data through specialized agents for finance, marketing, operations, risk, customer onboarding, debate, verification, forecasting, judging, and executive summarization. The system computes evidence-backed metrics, ranks likely causes with confidence scores, and produces explainable recommendations through a React + FastAPI product interface.
