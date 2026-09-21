# EP Tracker - Multi-Agent Personal Finance System

A multi-agent expense and personal finance tracker built with **FastAPI** (backend) and **React + Vite** (frontend), powered by **Groq LLM** (llama-3.3-70b-versatile). Users interact through both a UI dashboard and an AI chat interface. A coordinator agent routes each chat message to the appropriate specialist agent.

---

## Architecture

```
User (React Frontend)
        |
        v
   FastAPI Backend
        |
        v
+----------------------+
|  Coordinator Agent   |  <-- Classifies user intent
+----------+-----------+
           | routes to one of:
           v
+----------------+------------------+-----------------+
| Expense Agent  | Budget Agent     | Insights Agent  |
|                |                  |                 |
| Tool calling:  | Tool calling:    | RAG-based:      |
| add_expense    | set_budget       | ChromaDB +      |
| get_recent     | get_budgets      | SentenceTransf. |
| get_by_cat     | check_budget     | (finance tips)  |
| get_summary    | _status          |                 |
+----------------+------------------+-----------------+
        |                |                  |
        v                v                  v
  MySQL Database   MySQL Database    ChromaDB (vector)
  (expenses)       (budgets)         (finance_tips)
```

---

## Project Structure

```
EP tracker/
|-- app/
|   |-- main.py                          # FastAPI entry point, CORS, router registration
|   |
|   |-- agents/
|   |   |-- coordinator_agent.py         # Routes messages -> EXPENSE | BUDGET | INSIGHTS
|   |   |-- expense_agent.py             # Handles expense queries via tool calling
|   |   |-- budget_agent.py              # Handles budget queries via tool calling
|   |   |-- insights_agent.py            # Answers finance questions using RAG
|   |
|   |-- tools/
|   |   |-- expense_tools.py             # DB: add, list, filter, summarize expenses
|   |   |-- budget_tools.py              # DB: set, list, check budget status
|   |   |-- memory_tools.py              # Save/retrieve conversation memory
|   |   |-- audit_tools.py               # Write audit logs for every action
|   |   |-- input_tools.py               # Input validation (empty, length)
|   |   |-- pii_tools.py                 # PII redaction using Microsoft Presidio
|   |
|   |-- rag/
|   |   |-- documents/
|   |   |   |-- finance_tips.txt         # Source document: personal finance tips
|   |   |-- ingest.py                    # Chunk + embed tips into ChromaDB
|   |   |-- retriever.py                 # Semantic search over ChromaDB
|   |
|   |-- auth/
|   |   |-- __init__.py
|   |   |-- routes.py                    # POST /auth/register, POST /auth/login
|   |   |-- password.py                  # bcrypt hash/verify
|   |   |-- jwt_handler.py              # JWT creation (HS256, 60min expiry)
|   |   |-- dependencies.py             # get_current_user (Bearer token)
|   |
|   |-- chat/
|   |   |-- routes.py                    # POST /chat -- main agent orchestration
|   |
|   |-- expenses/
|   |   |-- routes.py                    # CRUD REST endpoints for expenses
|   |
|   |-- budgets/
|   |   |-- routes.py                    # CRUD REST endpoints for budgets
|   |
|   |-- database/
|       |-- connection.py                # SQLAlchemy engine + SessionLocal (MySQL)
|       |-- schema.sql                   # Full database schema (run this first)
|
|-- chroma_db/                           # Persisted ChromaDB vector store (auto-created)
|
|-- frontend/
|   |-- src/
|   |   |-- main.jsx                     # React entry point
|   |   |-- App.jsx                      # Auth routing: Login/Register/Dashboard
|   |   |-- index.css                    # Full dark theme stylesheet
|   |   |-- pages/
|   |   |   |-- Login.jsx                # Login form
|   |   |   |-- Register.jsx             # Registration form
|   |   |   |-- Dashboard.jsx            # Tabs: Expenses | Budgets | AI Assistant
|   |   |-- components/
|   |   |   |-- ExpenseForm.jsx          # Add expense form
|   |   |   |-- ExpenseList.jsx          # Expense table
|   |   |   |-- BudgetOverview.jsx       # Set budgets + status with progress bars
|   |   |   |-- Chat.jsx                 # AI chat interface
|   |   |-- services/
|   |       |-- api.js                   # All API calls
|   |-- index.html
|   |-- package.json                     # React 19, Vite 8
|   |-- vite.config.js
|
|-- tests/
|   |-- test_pii.py                      # PII redaction test
|   |-- test_agents.py                   # Coordinator agent routing test
|
|-- requirements.txt                     # Python dependencies
|-- .env.example                         # Environment variable template
|-- .env                                 # Actual environment variables
|-- README.md                            # This file
```

---

## Agent Details

### 1. Coordinator Agent
- **Role**: Intent classifier. Returns exactly one label: `EXPENSE`, `BUDGET`, or `INSIGHTS`.
- **LLM**: Groq (llama-3.3-70b-versatile)
- **No tools** -- pure prompt-based classification.
- Includes prompt injection guardrails.

### 2. Expense Agent
- **Role**: Add expenses, view recent expenses, filter by category, get monthly summaries.
- **LLM**: Groq with **tool calling** (`tool_choice: auto`).
- **Tools**:
  - `add_expense` -- insert a new expense
  - `get_recent_expenses` -- last N expenses
  - `get_expenses_by_category` -- filter by category
  - `get_monthly_summary` -- spending grouped by category for a month
- Two-pass LLM pattern: first call decides tools, second generates natural language response.

### 3. Budget Agent
- **Role**: Set budgets, view budgets, check spending vs budget with alerts.
- **LLM**: Groq with **tool calling**.
- **Tools**:
  - `set_budget` -- create or update a monthly budget per category
  - `get_budgets` -- list all budgets for a month
  - `check_budget_status` -- spending vs limit with ON_TRACK / WARNING / OVER_BUDGET alerts
- Same two-pass pattern.

### 4. Insights Agent
- **Role**: Answer general personal finance questions.
- **LLM**: Groq (no tool calling).
- **RAG pipeline**: query -> SentenceTransformer embedding -> ChromaDB top-3 retrieval -> context injected into prompt.
- Will not invent answers -- says "not available" if knowledge base lacks info.

---

## Chat Request Flow (POST /chat)

```
1. Validate input         -> input_tools.validate_message()
2. Redact PII             -> pii_tools.redact_pii() (Presidio)
3. Save user message      -> memory_tools.save_memory()
4. Load conversation      -> memory_tools.get_memory()
5. Classify intent        -> coordinator_agent() -> EXPENSE | BUDGET | INSIGHTS
6. Dispatch to agent      -> expense_agent() / budget_agent() / insights_agent()
7. Save assistant reply   -> memory_tools.save_memory()
8. Write audit log        -> audit_tools.save_audit_log()
9. Return JSON response   -> { agent, response, memory_messages }
```

---

## Database Schema (MySQL)

| Table                 | Key Columns                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `users`               | user_id, name, email, password_hash, role, status                           |
| `expenses`            | expense_id, user_id, amount, category, description, expense_date            |
| `budgets`             | budget_id, user_id, category, monthly_limit, month, year                    |
| `conversation_memory` | memory_id, user_id, session_id, role, message, created_at                   |
| `audit_logs`          | log_id, user_id, agent_name, action, resource_type, resource_id, status     |

---

## API Endpoints

### Auth
| Method | Endpoint         | Description         |
|--------|------------------|---------------------|
| POST   | /auth/register   | Register new user   |
| POST   | /auth/login      | Login, get JWT      |

### Expenses (JWT required)
| Method | Endpoint                        | Description                    |
|--------|---------------------------------|--------------------------------|
| POST   | /expenses                       | Add a new expense              |
| GET    | /expenses                       | List recent expenses           |
| GET    | /expenses/category/{category}   | Filter expenses by category    |
| GET    | /expenses/summary/{month}/{year}| Monthly spending summary       |

### Budgets (JWT required)
| Method | Endpoint                        | Description                    |
|--------|---------------------------------|--------------------------------|
| POST   | /budgets                        | Set/update a budget            |
| GET    | /budgets/{month}/{year}         | List budgets for a month       |
| GET    | /budgets/status/{month}/{year}  | Budget vs spending status      |

### Chat (JWT required)
| Method | Endpoint | Description                              |
|--------|----------|------------------------------------------|
| POST   | /chat    | Send message to multi-agent system       |

---

## How to Run

### Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase account (free at supabase.com)
- Groq API key (free at console.groq.com)

### 1. Set up Supabase database

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Once created, go to **SQL Editor** in the sidebar
3. Copy the contents of `app/database/schema.sql` and run it
4. Go to **Project Settings → Database** and copy the connection string
5. The connection string format is:
   ```
   postgresql+psycopg2://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

### 2. Set up the backend

```bash
cd "EP tracker"

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your Supabase DATABASE_URL, JWT_SECRET, GROQ_API_KEY
```

### 3. Ingest RAG documents

```bash
python -m app.rag.ingest
# Output: "Documents successfully stored in ChromaDB."
```

### 4. Start the backend

```bash
uvicorn app.main:app --reload
# Server runs at http://127.0.0.1:8000
# Docs at http://127.0.0.1:8000/docs
```

### 5. Set up and start the frontend

```bash
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:5173
```

---

## How to Test the Agents

### Test Coordinator Routing

```bash
python -m tests.test_agents
```

This sends test messages to the coordinator agent and checks if they route to the correct specialized agent.

### Test PII Redaction

```bash
python -m tests.test_pii
```

### Test via Chat (after server is running)

Open the app in browser at `http://localhost:5173`, register/login, then try:

| Message                                        | Expected Agent |
|------------------------------------------------|----------------|
| "I spent 200 on lunch today"                   | EXPENSE        |
| "Show my recent expenses"                      | EXPENSE        |
| "What did I spend on food this month?"         | EXPENSE        |
| "Set a budget of 5000 for food"                | BUDGET         |
| "Am I over budget this month?"                 | BUDGET         |
| "How can I save money on groceries?"           | INSIGHTS       |
| "What is the 50/30/20 rule?"                   | INSIGHTS       |

### Test via API (curl)

```bash
# Register
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@test.com","password":"test123"}'

# Login (save the token)
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# Chat with the agent (replace YOUR_TOKEN)
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message":"I spent 500 on groceries today","session_id":"test-1"}'

# Add expense directly
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"amount":500,"category":"food","description":"Groceries","expense_date":"2026-09-20"}'

# Check budget status
curl http://127.0.0.1:8000/budgets/status/9/2026 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Security Features

- **JWT authentication** (HS256, 60-min expiry) on all protected endpoints
- **bcrypt** password hashing
- **PII redaction** (Microsoft Presidio) on all chat input before processing/storage
- **Input validation** (empty/length checks)
- **Audit logging** for every agent action and API call
- **Authorization**: all queries scoped to the authenticated user_id
- **Prompt injection guards**: all agent system prompts forbid revealing internals

---

## Tech Stack

| Layer      | Technology                                    |
|------------|-----------------------------------------------|
| Backend    | FastAPI, SQLAlchemy (raw SQL), Supabase (PostgreSQL) |
| LLM        | Groq API (llama-3.3-70b-versatile)            |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2)       |
| Vector DB  | ChromaDB (persistent)                          |
| PII        | Microsoft Presidio (analyzer + anonymizer)     |
| Auth       | JWT (PyJWT), bcrypt                            |
| Frontend   | React 19, Vite 8                               |
