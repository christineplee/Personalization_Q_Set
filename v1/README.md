# Minimal Personalization Study

An online study platform investigating the minimal set of user information needed
for an LLM to produce better-adapted responses.

## Architecture

```
study/
├── backend/                  # FastAPI (Python)
│   ├── main.py              # API routes & LLM integration
│   ├── questions.py         # Profiling items, tasks, evaluation scales
│   ├── schedules.py         # Balanced assignment schedule generator
│   ├── requirements.txt
│   └── data/
│       ├── schedules.json   # Pre-generated assignment schedules
│       └── study.db         # SQLite database (created at runtime)
│
└── frontend/                # React
    ├── public/index.html
    └── src/
        ├── App.js           # All study phases (welcome → profiling → buffer → evaluation → post-study → done)
        ├── App.css          # Styles
        └── index.js         # Entry point
```

## Study Design

**Research Question:** What is the minimal set of user information that allows an
LLM to produce better-adapted responses?

**Method:**
1. Participants complete a 50-item profiling questionnaire spanning:
   - Validated psychological instruments (Big Five/TIPI, Primals, Need for Cognition, Regulatory Focus, MBTI-style)
   - Lifestyle & identity proxies (morning routine, desk organization, media preferences, etc.)
   - Perceptual & projective tasks (email style preference, scenario choices)
   - Behavioral micro-tasks (free-text writing sample, topic ranking)
   - Values & trade-off questions (honest vs kind, speed vs accuracy)
   - Identity signal questions (political orientation, trust, worldview)

2. For each of 8 tasks, a **random subset of 10 items** from the 50 is injected
   into the LLM's system prompt (naturalistic adaptation). Different random subsets
   per task, pre-assigned via balanced incomplete block design.

3. Participants evaluate each response on 5 Likert scales:
   - Content fit
   - Tone fit
   - Amount of information fit
   - Agency fit
   - Overall personalization fit
   Plus one open-ended question.

4. Post-study reflection questionnaire.

**Analysis:** LASSO regression, Shapley values, and random forest feature importance
on the binary item-inclusion indicators → identify which profile items predict
satisfaction improvement.

## Setup

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Azure OpenAI
cp .env.example .env
# Edit .env with your Azure credentials

# Generate assignment schedules (run once)
python schedules.py

# Start the API server
uvicorn main:app --reload --port 8000
```

To deactivate the virtual environment when done: `deactivate`

**Demo mode:** If `AZURE_OPENAI_API_KEY` is left as the default placeholder in `.env`,
the backend returns placeholder responses so you can test the full flow without API access.

### Frontend

```bash
cd frontend
npm install
npm start
```

The React dev server runs on port 3000 and proxies API requests to port 8000.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/questions` | Return all profiling questions |
| GET | `/api/evaluation-items` | Return evaluation scale items |
| POST | `/api/session/create` | Create session, claim schedule |
| POST | `/api/profiling/submit` | Store answers, generate 8 LLM responses |
| POST | `/api/evaluation/submit` | Store one task evaluation |
| POST | `/api/post-study/submit` | Store post-study data |
| GET | `/api/admin/export` | Export all data (for analysis) |

## Data Export

Hit `/api/admin/export` to get a JSON dump of all sessions, responses, and
evaluations. Each response record includes:
- `item_ids`: which profile items were in the prompt for that trial
- `system_prompt`: the exact prompt sent to the LLM
- `llm_response`: the LLM's output

This is the data needed for the LASSO / Shapley / random forest analysis.

## Key Design Decisions

- **Random subset injection**: Each trial includes a random 10-item subset from
  the 50-item profile. Across participants and tasks, this creates the variance
  needed to isolate each item's contribution via feature importance methods.

- **Balanced incomplete block design**: Schedules are pre-generated to ensure
  marginal balance (each item appears ~equally often) and pairwise balance
  (each pair co-occurs ~equally often).

- **Naturalistic LLM adaptation**: The LLM receives raw profile answers in its
  system prompt and adapts freely — no intermediate translation layer.

- **Pre-generated responses**: All 8 responses are generated during a brief
  buffer after profiling, ensuring consistent participant experience.
