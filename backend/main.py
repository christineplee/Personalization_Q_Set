"""
FastAPI backend for the Minimal Personalization Study.
Handles: session management, profiling storage, LLM prompt construction,
response generation, and evaluation data collection.
"""

import json
import os
import random
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AzureOpenAI

from questions import PROFILING_QUESTIONS, TASKS, EVALUATION_ITEMS, ATTENTION_CHECKS, get_profiling_questions_with_attention_checks

# ── Config ────────────────────────────────────────────────────────────────────

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://YOUR-RESOURCE.openai.azure.com/")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
DB_PATH = os.getenv("DB_PATH", "data/study.db")
SCHEDULES_PATH = os.getenv("SCHEDULES_PATH", "data/schedules.json")
PROLIFIC_REDIRECT_URL = os.getenv("PROLIFIC_REDIRECT_URL", "")

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="Minimal Personalization Study")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Database ──────────────────────────────────────────────────────────────────

def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                schedule_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'profiling',
                task_order TEXT,
                profiling_data TEXT,
                post_study_data TEXT,
                prolific_pid TEXT
            );

            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                task_index INTEGER NOT NULL,
                item_ids TEXT NOT NULL,
                system_prompt TEXT NOT NULL,
                llm_response TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );

            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                eval_tone INTEGER,
                eval_verbosity INTEGER,
                eval_structure INTEGER,
                eval_initiative INTEGER,
                eval_overall INTEGER,
                eval_relevance INTEGER,
                open_ended TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );

            CREATE TABLE IF NOT EXISTS schedule_claims (
                schedule_id INTEGER PRIMARY KEY,
                claimed INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS attention_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                check_id TEXT NOT NULL,
                expected INTEGER NOT NULL,
                actual INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
        """)


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ── Load schedules ────────────────────────────────────────────────────────────

def load_schedules():
    with open(SCHEDULES_PATH) as f:
        return json.load(f)


def claim_next_schedule():
    """Atomically claim the next available schedule."""
    schedules = load_schedules()
    with get_db() as conn:
        # Ensure all schedules are in the claims table
        for s in schedules:
            conn.execute(
                "INSERT OR IGNORE INTO schedule_claims (schedule_id, claimed) VALUES (?, 0)",
                (s["schedule_id"],),
            )
        # Claim the next unclaimed one
        row = conn.execute(
            "SELECT schedule_id FROM schedule_claims WHERE claimed = 0 ORDER BY schedule_id LIMIT 1"
        ).fetchone()
        if not row:
            raise HTTPException(status_code=503, detail="No schedules available")
        sid = row["schedule_id"]
        conn.execute("UPDATE schedule_claims SET claimed = 1 WHERE schedule_id = ?", (sid,))
        return sid, schedules[sid]


# ── LLM ───────────────────────────────────────────────────────────────────────

def get_llm_client():
    if not AZURE_API_KEY or AZURE_API_KEY == "your-api-key-here":
        return None
    return AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
    )


def build_system_prompt(profile_answers: dict, item_ids: list[str]) -> str:
    """
    Construct a system prompt that includes the user's answers to the
    specified subset of profiling items.
    """
    # Build the profile description from the subset
    question_lookup = {q["id"]: q for q in PROFILING_QUESTIONS}
    profile_lines = []

    for item_id in item_ids:
        q = question_lookup[item_id]
        answer = profile_answers.get(item_id)
        if answer is None:
            continue

        if q["type"] == "bipolar7":
            left = q.get("left_anchor", "")
            right = q.get("right_anchor", "")
            profile_lines.append(
                f"- Scenario: {q['text']} — On a scale from \"{left}\" (1) to \"{right}\" (7), "
                f"this user chose: {answer}/7"
            )
        elif q["type"] == "likert7":
            anchors = q.get("anchors", ["1", "7"])
            profile_lines.append(f"- {q['text']} — Response: {answer}/7 ({anchors[0]} to {anchors[1]})")
        elif q["type"] == "likert6":
            anchors = q.get("anchors", ["1", "6"])
            profile_lines.append(f"- {q['text']} — Response: {answer}/6 ({anchors[0]} to {anchors[1]})")
        elif q["type"] == "likert5":
            anchors = q.get("anchors", ["1", "5"])
            stem = q.get("stem", "")
            display_text = f"{stem} {q['text']}" if stem else q["text"]
            profile_lines.append(f"- \"{display_text}\" — Response: {answer}/5 ({anchors[0]} to {anchors[1]})")
        elif q["type"] == "forced_choice":
            if isinstance(answer, int) and "options" in q:
                answer_text = q["options"][answer] if answer < len(q["options"]) else str(answer)
            else:
                answer_text = str(answer)
            profile_lines.append(f"- {q['text']} — Chose: \"{answer_text}\"")
        elif q["type"] == "free_text":
            profile_lines.append(f"- {q['text']} — Their response: \"{answer}\"")
        elif q["type"] == "ranking":
            if isinstance(answer, list):
                ranking_str = " > ".join(str(a) for a in answer)
                profile_lines.append(f"- {q['text']} — Ranking (most to least interesting): {ranking_str}")
            else:
                profile_lines.append(f"- {q['text']} — Response: {answer}")

    profile_section = "\n".join(profile_lines)

    system_prompt = f"""You are a helpful AI assistant. You have been given information 
about the user you are about to interact with. Use this information to strongly 
adapt your response along four dimensions:

1. TONE: How warm/cold, formal/casual, supportive/direct should you be? Pay 
   attention to their preferences about emotional acknowledgment, formality, 
   and communication style.

2. VERBOSITY: How much detail should you provide? Some users want concise key 
   points, others want comprehensive explanations. Adjust the length and depth 
   of your response accordingly.

3. STRUCTURE: How should you organize your response? Some users prefer bullet 
   points, headers, and structured layouts. Others prefer flowing conversational 
   prose. Match their preference.

4. INITIATIVE: How proactive should you be? Some users want you to anticipate 
   needs, suggest next steps, and flag things they haven't asked about. Others 
   want you to answer exactly what was asked and nothing more.

USER PROFILE:
{profile_section}

IMPORTANT: Make strong, clear adaptations based on this profile. Two users with 
different profiles should receive noticeably different responses to the same 
question. Do not default to a generic middle-ground style. Do not mention that 
you have this profile information or refer to it explicitly.
"""
    return system_prompt


def generate_llm_response(system_prompt: str, user_message: str) -> str:
    """Call Azure OpenAI to generate a response."""
    client = get_llm_client()
    if client is None:
        # Demo mode: return a placeholder
        return f"[DEMO MODE] This is a placeholder response to: '{user_message}'. In production, this would be a personalized LLM response generated using the participant's profile subset. The system prompt contains {system_prompt.count(chr(10))} lines of profile information."

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content


# ── Pydantic Models ───────────────────────────────────────────────────────────

class ProfilingSubmission(BaseModel):
    session_id: str
    answers: dict  # {item_id: answer_value}


class EvaluationSubmission(BaseModel):
    session_id: str
    task_id: str
    eval_tone: int
    eval_verbosity: int
    eval_structure: int
    eval_initiative: int
    eval_overall: int
    eval_relevance: int
    open_ended: str = ""


class PostStudySubmission(BaseModel):
    session_id: str
    data: dict


class AttentionCheckSubmission(BaseModel):
    session_id: str
    check_id: str
    expected: int
    actual: int


class CreateSessionRequest(BaseModel):
    prolific_pid: Optional[str] = None


# ── API Routes ────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    init_db()
    if not Path(SCHEDULES_PATH).exists():
        from schedules import generate_schedules, save_schedules
        schedules = generate_schedules()
        save_schedules(schedules, SCHEDULES_PATH)
    # Log config status
    if AZURE_API_KEY and AZURE_API_KEY != "your-api-key-here":
        print(f"✓ Azure OpenAI configured: {AZURE_ENDPOINT} (deployment: {AZURE_DEPLOYMENT})")
    else:
        print("⚠ Running in DEMO MODE — set AZURE_OPENAI_API_KEY in .env for real LLM responses")


@app.get("/api/questions")
def get_questions():
    """Return profiling questions with attention checks inserted."""
    eval_attn_checks = {str(ac["in_task"]): ac for ac in ATTENTION_CHECKS if ac.get("in_task") is not None}
    return {
        "questions": get_profiling_questions_with_attention_checks(),
        "eval_attention_checks": eval_attn_checks,
    }


@app.get("/api/evaluation-items")
def get_evaluation_items():
    """Return the evaluation scale items."""
    return {"items": EVALUATION_ITEMS}


@app.post("/api/session/create")
def create_session(request: CreateSessionRequest = CreateSessionRequest()):
    """Create a new participant session and claim a schedule."""
    schedule_id, schedule = claim_next_schedule()
    session_id = f"s_{int(time.time()*1000)}_{random.randint(1000,9999)}"

    # Randomize task order for this participant
    task_order = list(range(len(TASKS)))
    random.shuffle(task_order)

    with get_db() as conn:
        conn.execute(
            "INSERT INTO sessions (session_id, schedule_id, created_at, task_order, prolific_pid) VALUES (?, ?, ?, ?, ?)",
            (session_id, schedule_id, datetime.utcnow().isoformat(), json.dumps(task_order), request.prolific_pid),
        )

    return {
        "session_id": session_id,
        "schedule_id": schedule_id,
        "num_questions": len(PROFILING_QUESTIONS),
        "num_tasks": len(TASKS),
        "prolific_redirect_url": PROLIFIC_REDIRECT_URL,
    }


@app.post("/api/profiling/submit")
def submit_profiling(submission: ProfilingSubmission):
    """
    Store profiling answers and generate all 8 LLM responses.
    Returns the tasks with their personalized responses.
    """
    session_id = submission.session_id

    with get_db() as conn:
        session = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Store profiling data
        conn.execute(
            "UPDATE sessions SET profiling_data = ?, status = 'generating' WHERE session_id = ?",
            (json.dumps(submission.answers), session_id),
        )

        # Check and store profiling attention check results
        for ac in ATTENTION_CHECKS:
            if ac.get("insert_after") and ac["id"] in submission.answers:
                actual = submission.answers[ac["id"]]
                expected = ac["expected_answer"]
                passed = 1 if actual == expected else 0
                conn.execute(
                    """INSERT INTO attention_checks
                       (session_id, check_id, expected, actual, passed, created_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (session_id, ac["id"], expected, actual, passed, datetime.utcnow().isoformat()),
                )

    # Load this session's schedule
    schedules = load_schedules()
    schedule = schedules[session["schedule_id"]]
    task_order = json.loads(session["task_order"])

    # Generate responses for each task
    generated_tasks = []
    for task_assignment in schedule["tasks"]:
        task_idx = task_assignment["task_index"]
        item_ids = task_assignment["item_ids"]
        task = TASKS[task_idx]

        # Build prompt with this subset
        system_prompt = build_system_prompt(submission.answers, item_ids)

        # Generate response
        llm_response = generate_llm_response(system_prompt, task["prompt"])

        # Store in database
        with get_db() as conn:
            conn.execute(
                """INSERT INTO responses
                   (session_id, task_id, task_index, item_ids, system_prompt, llm_response, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    task["id"],
                    task_idx,
                    json.dumps(item_ids),
                    system_prompt,
                    llm_response,
                    datetime.utcnow().isoformat(),
                ),
            )

        generated_tasks.append({
            "task_id": task["id"],
            "task_index": task_idx,
            "category": task["category"],
            "prompt": task["prompt"],
            "response": llm_response,
            "item_ids": item_ids,  # included for transparency / debugging
        })

    # Reorder tasks according to randomized order
    ordered_tasks = [generated_tasks[i] for i in task_order]

    with get_db() as conn:
        conn.execute(
            "UPDATE sessions SET status = 'evaluating' WHERE session_id = ?",
            (session_id,),
        )

    return {"tasks": ordered_tasks}


@app.post("/api/evaluation/submit")
def submit_evaluation(submission: EvaluationSubmission):
    """Store evaluation for one task."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO evaluations
               (session_id, task_id, eval_tone, eval_verbosity, eval_structure, eval_initiative, eval_overall, eval_relevance, open_ended, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                submission.session_id,
                submission.task_id,
                submission.eval_tone,
                submission.eval_verbosity,
                submission.eval_structure,
                submission.eval_initiative,
                submission.eval_overall,
                submission.eval_relevance,
                submission.open_ended,
                datetime.utcnow().isoformat(),
            ),
        )
    return {"status": "ok"}


@app.post("/api/post-study/submit")
def submit_post_study(submission: PostStudySubmission):
    """Store post-study questionnaire data."""
    with get_db() as conn:
        conn.execute(
            "UPDATE sessions SET post_study_data = ?, status = 'complete' WHERE session_id = ?",
            (json.dumps(submission.data), submission.session_id),
        )
    return {"status": "ok"}


@app.post("/api/attention-check/submit")
def submit_attention_check(submission: AttentionCheckSubmission):
    """Store an evaluation-phase attention check result."""
    passed = 1 if submission.actual == submission.expected else 0
    with get_db() as conn:
        conn.execute(
            """INSERT INTO attention_checks
               (session_id, check_id, expected, actual, passed, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (submission.session_id, submission.check_id, submission.expected, submission.actual, passed, datetime.utcnow().isoformat()),
        )
    return {"status": "ok", "passed": bool(passed)}


@app.get("/api/admin/export")
def export_data():
    """Export all study data for analysis (admin endpoint)."""
    with get_db() as conn:
        sessions = [dict(r) for r in conn.execute("SELECT * FROM sessions").fetchall()]
        responses = [dict(r) for r in conn.execute("SELECT * FROM responses").fetchall()]
        evaluations = [dict(r) for r in conn.execute("SELECT * FROM evaluations").fetchall()]
        attention_checks = [dict(r) for r in conn.execute("SELECT * FROM attention_checks").fetchall()]

    return {
        "sessions": sessions,
        "responses": responses,
        "evaluations": evaluations,
        "attention_checks": attention_checks,
        "questions": PROFILING_QUESTIONS,
        "tasks": TASKS,
    }


@app.get("/api/admin/status")
def study_status():
    """Quick status check for monitoring data collection."""
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        complete = conn.execute("SELECT COUNT(*) FROM sessions WHERE status='complete'").fetchone()[0]
        claimed = conn.execute("SELECT COUNT(*) FROM schedule_claims WHERE claimed=1").fetchone()[0]
    return {
        "total_sessions": total,
        "complete": complete,
        "schedules_claimed": claimed,
        "schedules_remaining": 200 - claimed,
    }

#@app.post("/api/admin/free-incomplete")
#def free_incomplete():
#    """Free schedules claimed by incomplete sessions."""
#    with get_db() as conn:
#        incomplete = conn.execute(
#            "SELECT session_id, schedule_id, status FROM sessions WHERE status != 'complete'"
#        ).fetchall()
#        freed = 0
#        for s in incomplete:
#            conn.execute("UPDATE schedule_claims SET claimed = 0 WHERE schedule_id = ?", (s['schedule_id'],))
#            freed += 1
#    return {"freed": freed, "schedule_ids": [s['schedule_id'] for s in incomplete]}