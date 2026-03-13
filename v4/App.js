import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

const API = process.env.REACT_APP_API_URL || '';

// ── Utility ──────────────────────────────────────────────────────────────────

async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// Simple markdown to HTML renderer
function renderMarkdown(text) {
  if (!text) return '';
  let html = text
    .replace(/^### \*?\*?(.*?)\*?\*?\s*$/gm, '<h3>$1</h3>')
    .replace(/^## \*?\*?(.*?)\*?\*?\s*$/gm, '<h2>$1</h2>')
    .replace(/^# \*?\*?(.*?)\*?\*?\s*$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^- (.*$)/gm, '<li>$1</li>')
    .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>');
  html = html.replace(/((?:<li>.*?<\/li>\s*(?:<br\/>)?)+)/g, '<ul>$1</ul>');
  html = html.replace(/<ul>(.*?)<\/ul>/gs, (match, inner) =>
    '<ul>' + inner.replace(/<br\/>/g, '') + '</ul>'
  );
  return '<p>' + html + '</p>';
}

// ── Phase: Welcome ───────────────────────────────────────────────────────────

function Welcome({ onStart }) {
  return (
    <div className="phase welcome">
      <div className="card wide">
        <h1>Communication Preferences Study</h1>
        <p className="subtitle">
          How should an AI assistant adapt to <em>you</em>?
        </p>
        <div className="welcome-body">
          <p>
            In this study, you'll answer questions about yourself, then interact
            with an AI assistant that uses your answers to personalize its
            responses. You'll evaluate how well each response fits your preferences.
          </p>
          <div className="info-box">
            <strong>What to expect:</strong>
            <ul>
              <li>Part 1: Answer questions about your preferences and personality </li>
              <li>Part 2: Read and evaluate 8 AI-generated responses </li>
              <li>Part 3: Answer a few final reflection questions </li>
            </ul>
          </div>
          <p className="note">
            Your responses are stored with an anonymous ID. No personally
            identifiable information is collected.
          </p>
        </div>
        <button className="btn primary" onClick={onStart}>
          Begin Study
        </button>
      </div>
    </div>
  );
}

// ── Phase: Profiling ─────────────────────────────────────────────────────────

const TIER_LABELS = {
  dimension_tone: 'Tone Preferences',
  dimension_verbosity: 'Detail Preferences',
  dimension_structure: 'Structure Preferences',
  dimension_initiative: 'Initiative Preferences',
  projective: 'Scenarios & Choices',
  primals: 'World Beliefs',
  bigfive: 'Personality',
};

const TIER_ORDER = ['dimension_tone', 'dimension_verbosity', 'dimension_structure', 'dimension_initiative', 'projective', 'primals', 'bigfive'];

const TIER_INSTRUCTIONS = {
  dimension_tone: 'For each scenario, imagine you are interacting with an AI assistant. The two descriptions represent different styles the AI could use. Choose where your preference falls on the scale.',
  dimension_verbosity: 'For each scenario, the two sides represent different levels of detail the AI could provide. Choose where your preference falls.',
  dimension_structure: 'For each scenario, the two sides represent different ways the AI could organize its response. Choose where your preference falls.',
  dimension_initiative: 'For each scenario, the two sides represent different levels of initiative the AI could take. Choose where your preference falls.',
  projective: 'For each question, choose the option that feels more like you. There are no right or wrong answers \u2014 go with your gut.',
  primals: 'Rate how much you agree or disagree with each statement about the world.',
  bigfive: 'Rate how well each statement describes you as a person.',
};

function QuestionRenderer({ question, value, onChange }) {
  const { id, type, text, options, anchors } = question;

  if (type === 'bipolar7') {
    return (
      <div className="question">
        <p className="q-text q-scenario">{text}</p>
        <div className="bipolar-poles">
          <div className={`pole pole-left ${value && value <= 3 ? 'pole-active' : ''}`}>
            <span className="pole-arrow">←</span>
            <span className="pole-label">{question.left_anchor}</span>
          </div>
          <div className={`pole pole-right ${value && value >= 5 ? 'pole-active' : ''}`}>
            <span className="pole-label">{question.right_anchor}</span>
            <span className="pole-arrow">→</span>
          </div>
        </div>
        <div className="bipolar-scale">
          <div className="likert-buttons">
            {[1, 2, 3, 4, 5, 6, 7].map((v) => (
              <button
                key={v}
                className={`likert-btn ${value === v ? 'selected' : ''}`}
                onClick={() => onChange(id, v)}
              >
                {v}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (type === 'likert5') {
    return (
      <div className="question">
        {question.stem && <p className="q-stem">{question.stem}</p>}
        <p className="q-text">{text}</p>
        <div className="likert-row">
          <span className="anchor left">{anchors?.[0]}</span>
          <div className="likert-buttons">
            {[1, 2, 3, 4, 5].map((v) => (
              <button
                key={v}
                className={`likert-btn ${value === v ? 'selected' : ''}`}
                onClick={() => onChange(id, v)}
              >
                {v}
              </button>
            ))}
          </div>
          <span className="anchor right">{anchors?.[1]}</span>
        </div>
      </div>
    );
  }

  if (type === 'likert7' || type === 'likert6') {
    const max = type === 'likert7' ? 7 : 6;
    return (
      <div className="question">
        <p className="q-text">{text}</p>
        <div className="likert-row">
          <span className="anchor left">{anchors?.[0]}</span>
          <div className="likert-buttons">
            {Array.from({ length: max }, (_, i) => (
              <button
                key={i + 1}
                className={`likert-btn ${value === i + 1 ? 'selected' : ''}`}
                onClick={() => onChange(id, i + 1)}
              >
                {i + 1}
              </button>
            ))}
          </div>
          <span className="anchor right">{anchors?.[1]}</span>
        </div>
      </div>
    );
  }

  if (type === 'forced_choice') {
    const isTwoOptions = options.length === 2;
    if (isTwoOptions) {
      return (
        <div className="question">
          <p className="q-text">{text}</p>
          <div className="choice-versus">
            <button
              className={`choice-card ${value === 0 ? 'selected' : ''}`}
              onClick={() => onChange(id, 0)}
            >
              {options[0]}
            </button>
            <div className="choice-or">or</div>
            <button
              className={`choice-card ${value === 1 ? 'selected' : ''}`}
              onClick={() => onChange(id, 1)}
            >
              {options[1]}
            </button>
          </div>
        </div>
      );
    }
    return (
      <div className="question">
        <p className="q-text">{text}</p>
        <div className="choice-list">
          {options.map((opt, i) => (
            <button
              key={i}
              className={`choice-btn ${value === i ? 'selected' : ''}`}
              onClick={() => onChange(id, i)}
            >
              {typeof opt === 'string' && opt.length > 80 ? (
                <span className="choice-long">{opt}</span>
              ) : (
                opt
              )}
            </button>
          ))}
        </div>
      </div>
    );
  }

  if (type === 'free_text') {
    return (
      <div className="question">
        <p className="q-text">{text}</p>
        <textarea
          className="free-text"
          rows={3}
          placeholder="Type your response here..."
          value={value || ''}
          onChange={(e) => onChange(id, e.target.value)}
        />
      </div>
    );
  }

  if (type === 'ranking') {
    const items = options || [];
    const ranked = value || [];
    const unranked = items.filter((item) => !ranked.includes(item));

    const addToRank = (item) => {
      onChange(id, [...ranked, item]);
    };
    const removeFromRank = (idx) => {
      const next = [...ranked];
      next.splice(idx, 1);
      onChange(id, next);
    };

    return (
      <div className="question">
        <p className="q-text">{text}</p>
        <p className="q-hint">Click topics in order from most to least interesting:</p>
        <div className="ranking-container">
          <div className="ranking-pool">
            {unranked.map((item) => (
              <button key={item} className="rank-chip" onClick={() => addToRank(item)}>
                {item}
              </button>
            ))}
          </div>
          {ranked.length > 0 && (
            <div className="ranking-result">
              {ranked.map((item, i) => (
                <div key={item} className="rank-item" onClick={() => removeFromRank(i)}>
                  <span className="rank-num">{i + 1}</span>
                  <span>{item}</span>
                  <span className="rank-remove">✕</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  return <p>Unknown question type: {type}</p>;
}

function Profiling({ questions, onSubmit }) {
  const [answers, setAnswers] = useState({});
  const [currentTier, setCurrentTier] = useState(0);

  const tiers = TIER_ORDER.filter((t) =>
    questions.some((q) => q.tier === t)
  );
  const currentTierQuestions = questions.filter((q) => q.tier === tiers[currentTier]);
  const tierComplete = currentTierQuestions.every((q) => {
    const val = answers[q.id];
    if (q.type === 'ranking') return val && val.length === q.options.length;
    if (q.type === 'forced_choice') return val !== undefined;
    return val !== undefined && val !== '';
  });

  const handleChange = (id, value) => {
    setAnswers((prev) => ({ ...prev, [id]: value }));
  };

  const totalAnswered = questions.filter((q) => {
    const v = answers[q.id];
    if (q.type === 'ranking') return v && v.length === q.options?.length;
    if (q.type === 'forced_choice') return v !== undefined;
    return v !== undefined && v !== '';
  }).length;

  return (
    <div className="phase profiling">
      <div className="card wide">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${(totalAnswered / questions.length) * 100}%` }} />
        </div>
        <div className="tier-nav">
          {tiers.map((t, i) => (
            <button
              key={t}
              className={`tier-tab ${i === currentTier ? 'active' : ''} ${i < currentTier ? 'done' : ''}`}
              onClick={() => i <= currentTier && setCurrentTier(i)}
            >
              {TIER_LABELS[t] || t}
            </button>
          ))}
        </div>

        <h2>{TIER_LABELS[tiers[currentTier]]}</h2>
        {TIER_INSTRUCTIONS[tiers[currentTier]] && (
          <p className="tier-instructions">{TIER_INSTRUCTIONS[tiers[currentTier]]}</p>
        )}
        <p className="tier-progress">
          {totalAnswered} of {questions.length} questions answered
        </p>

        <div className="questions-list">
          {currentTierQuestions.map((q) => (
            <QuestionRenderer
              key={q.id}
              question={q}
              value={answers[q.id]}
              onChange={handleChange}
            />
          ))}
        </div>

        <div className="nav-buttons">
          {currentTier > 0 && (
            <button className="btn secondary" onClick={() => setCurrentTier((p) => p - 1)}>
              ← Previous Section
            </button>
          )}
          {currentTier < tiers.length - 1 ? (
            <button
              className="btn primary"
              disabled={!tierComplete}
              onClick={() => setCurrentTier((p) => p + 1)}
            >
              Next Section →
            </button>
          ) : (
            <button
              className="btn primary"
              disabled={totalAnswered < questions.length}
              onClick={() => onSubmit(answers)}
            >
              Submit & Continue
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Phase: Buffer ────────────────────────────────────────────────────────────

function Buffer({ message }) {
  return (
    <div className="phase buffer">
      <div className="card">
        <div className="spinner" />
        <h2>Preparing Your Session</h2>
        <p>{message || 'Generating personalized responses based on your profile...'}</p>
        <p className="note">This usually takes 2–3 minutes.</p>
      </div>
    </div>
  );
}

// ── Phase: Task Evaluation ───────────────────────────────────────────────────

function TaskEvaluation({ tasks, sessionId, evalAttentionChecks, onSubmitEval, onAttnCheckFailed, onComplete }) {
  const [currentTask, setCurrentTask] = useState(0);
  const [ratings, setRatings] = useState({});
  const [relevance, setRelevance] = useState(null);
  const [openEnded, setOpenEnded] = useState('');
  const [submitted, setSubmitted] = useState(new Set());

  const task = tasks[currentTask];
  const currentAttnCheck = evalAttentionChecks?.[String(currentTask)] || null;

  const evalDims = ['tone', 'verbosity', 'structure', 'initiative', 'overall'];
  const allRated = evalDims.every((d) => ratings[d] !== undefined) &&
    relevance !== null &&
    (!currentAttnCheck || ratings['_attn'] !== undefined);

  const handleRate = (dim, val) => {
    setRatings((prev) => ({ ...prev, [dim]: val }));
  };

  const handleSubmit = async () => {
    await onSubmitEval({
      task_id: task.task_id,
      eval_tone: ratings.tone,
      eval_verbosity: ratings.verbosity,
      eval_structure: ratings.structure,
      eval_initiative: ratings.initiative,
      eval_overall: ratings.overall,
      eval_relevance: relevance,
      open_ended: openEnded,
    });

    // Submit attention check if this task had one
    if (currentAttnCheck && ratings['_attn'] !== undefined) {
      try {
        await api('/api/attention-check/submit', {
          method: 'POST',
          body: JSON.stringify({
            session_id: sessionId,
            check_id: currentAttnCheck.id,
            expected: currentAttnCheck.expected_answer,
            actual: ratings['_attn'],
          }),
        });
      } catch (err) {
        console.error('Failed to submit attention check:', err);
      }
      // Notify parent if check was failed (parent terminates at 3 failures)
      if (ratings['_attn'] !== currentAttnCheck.expected_answer) {
        onAttnCheckFailed();
      }
    }

    setSubmitted((prev) => new Set(prev).add(currentTask));

    if (currentTask < tasks.length - 1) {
      setCurrentTask((p) => p + 1);
      setRatings({});
      setRelevance(null);
      setOpenEnded('');
      window.scrollTo(0, 0);
    } else {
      onComplete();
    }
  };

  const evalLabels = {
    tone: 'The tone of this response felt right for me \u2014 not too casual, not too formal, not too warm or too cold.',
    verbosity: 'The amount of detail was right for me \u2014 not too brief, not too lengthy.',
    structure: 'The way the response was organized worked for me \u2014 whether it used lists, paragraphs, sections, or flowing prose.',
    initiative: 'The assistant took the right level of initiative \u2014 it didn\'t overreach, but it also didn\'t hold back when I would have wanted more.',
    overall: 'Overall, this response felt like it was written for someone like me.',
  };

  // Build eval items, inserting attention check after the 2nd item if applicable
  const evalEntries = Object.entries(evalLabels);
  const evalItems = [];
  evalEntries.forEach(([dim, label], idx) => {
    evalItems.push({ key: dim, label, isAttn: false });
    if (idx === 1 && currentAttnCheck) {
      evalItems.push({ key: '_attn', label: currentAttnCheck.text, isAttn: true });
    }
  });

  return (
    <div className="phase evaluation">
      <div className="card wide">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${((currentTask) / tasks.length) * 100}%` }} />
        </div>
        <p className="task-counter">Task {currentTask + 1} of {tasks.length}</p>

        <div className="task-section">
          <div className="task-prompt">
            <span className="label">Your question to the AI:</span>
            <p>{task.prompt}</p>
          </div>

          <div className="task-response">
            <span className="label">AI Response:</span>
            <div className="response-text" dangerouslySetInnerHTML={{ __html: renderMarkdown(task.response) }} />
          </div>
        </div>

        <div className="eval-section">
          <div className="eval-item relevance-item">
            <p className="eval-label">How relevant is this topic to you personally?</p>
            <div className="likert-row compact">
              <span className="anchor left">Not at all</span>
              <div className="likert-buttons">
                {[1, 2, 3, 4, 5, 6, 7].map((v) => (
                  <button
                    key={v}
                    className={`likert-btn ${relevance === v ? 'selected' : ''}`}
                    onClick={() => setRelevance(v)}
                  >
                    {v}
                  </button>
                ))}
              </div>
              <span className="anchor right">Very relevant</span>
            </div>
          </div>

          <h3>How well did this response fit you?</h3>
          <p className="eval-instructions">Rate each statement from 1 (Strongly Disagree) to 7 (Strongly Agree)</p>

          {evalItems.map(({ key, label }) => (
            <div key={key} className="eval-item">
              <p className="eval-label">{label}</p>
              <div className="likert-row compact">
                <span className="anchor left">Disagree</span>
                <div className="likert-buttons">
                  {[1, 2, 3, 4, 5, 6, 7].map((v) => (
                    <button
                      key={v}
                      className={`likert-btn ${ratings[key] === v ? 'selected' : ''}`}
                      onClick={() => handleRate(key, v)}
                    >
                      {v}
                    </button>
                  ))}
                </div>
                <span className="anchor right">Agree</span>
              </div>
            </div>
          ))}

          <div className="open-ended-section">
            <label className="eval-label">
              In one sentence, what would you change about this response?
            </label>
            <textarea
              className="free-text"
              rows={2}
              placeholder="Optional — but very helpful for our research"
              value={openEnded}
              onChange={(e) => setOpenEnded(e.target.value)}
            />
          </div>

          <button
            className="btn primary"
            disabled={!allRated}
            onClick={handleSubmit}
          >
            {currentTask < tasks.length - 1 ? 'Next Task \u2192' : 'Finish Evaluation'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Phase: Post-Study ────────────────────────────────────────────────────────

function PostStudy({ onSubmit }) {
  const [data, setData] = useState({
    overall_quality: null,
    prefer_personalized: null,
    dimension_rank: [],
    what_understood: '',
    what_wrong: '',
  });

  const dims = ['Tone (warmth, formality, directness)', 'Verbosity (level of detail)', 'Structure (how it was organized)', 'Initiative (how proactive it was)'];
  const unranked = dims.filter((d) => !data.dimension_rank.includes(d));

  const complete = data.overall_quality !== null && data.prefer_personalized !== null && data.dimension_rank.length === 4;

  return (
    <div className="phase post-study">
      <div className="card wide">
        <h2>Final Reflections</h2>
        <p>Almost done — a few last questions about your overall experience.</p>

        <div className="question">
          <p className="q-text">Overall, how would you rate the quality of the personalized responses?</p>
          <div className="likert-row">
            <span className="anchor left">Very poor</span>
            <div className="likert-buttons">
              {[1, 2, 3, 4, 5, 6, 7].map((v) => (
                <button
                  key={v}
                  className={`likert-btn ${data.overall_quality === v ? 'selected' : ''}`}
                  onClick={() => setData((p) => ({ ...p, overall_quality: v }))}
                >
                  {v}
                </button>
              ))}
            </div>
            <span className="anchor right">Excellent</span>
          </div>
        </div>

        <div className="question">
          <p className="q-text">Would you prefer an AI that adapts to you like this over a generic AI assistant?</p>
          <div className="choice-list">
            {['Strongly prefer personalized', 'Slightly prefer personalized', 'No preference', 'Slightly prefer generic', 'Strongly prefer generic'].map((opt, i) => (
              <button
                key={i}
                className={`choice-btn ${data.prefer_personalized === i ? 'selected' : ''}`}
                onClick={() => setData((p) => ({ ...p, prefer_personalized: i }))}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>

        <div className="question">
          <p className="q-text">
            Which aspect of personalization did you notice most? Rank from most to least noticeable:
          </p>
          <div className="ranking-container">
            <div className="ranking-pool">
              {unranked.map((d) => (
                <button key={d} className="rank-chip" onClick={() => setData((p) => ({ ...p, dimension_rank: [...p.dimension_rank, d] }))}>
                  {d}
                </button>
              ))}
            </div>
            {data.dimension_rank.length > 0 && (
              <div className="ranking-result">
                {data.dimension_rank.map((d, i) => (
                  <div key={d} className="rank-item" onClick={() => {
                    const next = [...data.dimension_rank];
                    next.splice(i, 1);
                    setData((p) => ({ ...p, dimension_rank: next }));
                  }}>
                    <span className="rank-num">{i + 1}</span>
                    <span>{d}</span>
                    <span className="rank-remove">✕</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="question">
          <p className="q-text">What did the AI seem to understand about you?</p>
          <textarea
            className="free-text"
            rows={2}
            value={data.what_understood}
            onChange={(e) => setData((p) => ({ ...p, what_understood: e.target.value }))}
            placeholder="e.g., It picked up on my preference for direct answers..."
          />
        </div>

        <div className="question">
          <p className="q-text">What did the AI get wrong about you?</p>
          <textarea
            className="free-text"
            rows={2}
            value={data.what_wrong}
            onChange={(e) => setData((p) => ({ ...p, what_wrong: e.target.value }))}
            placeholder="e.g., It was too formal when I prefer casual conversation..."
          />
        </div>

        <button className="btn primary" disabled={!complete} onClick={() => onSubmit(data)}>
          Submit & Finish
        </button>
      </div>
    </div>
  );
}

// ── Phase: Thank You ─────────────────────────────────────────────────────────

function ThankYou({ sessionId }) {
  return (
    <div className="phase thank-you">
      <div className="card">
        <h1>Thank You!</h1>
        <p>Your responses have been recorded.</p>
        <div className="info-box">
          <p><strong>Session ID:</strong> {sessionId}</p>
          <p>Please save this ID in case you need to reference your participation.</p>
        </div>
        <p className="note">
          This study investigates how minimal user information can improve AI
          communication. Your data will help us understand what an AI needs to
          know about a person to communicate more effectively.
        </p>
      </div>
    </div>
  );
}

// ── Main App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [phase, setPhase] = useState('welcome'); // welcome | profiling | buffer | evaluation | post_study | done | terminated
  const [sessionId, setSessionId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [evalAttentionChecks, setEvalAttentionChecks] = useState({});
  const [failedAttnCount, setFailedAttnCount] = useState(0);
  const [error, setError] = useState(null);
  const [bufferMessage, setBufferMessage] = useState('');

  // Load questions on mount
  useEffect(() => {
    api('/api/questions').then((data) => {
      setQuestions(data.questions);
      if (data.eval_attention_checks) setEvalAttentionChecks(data.eval_attention_checks);
    }).catch(console.error);
  }, []);

  const handleStart = async () => {
    try {
      const session = await api('/api/session/create', { method: 'POST' });
      setSessionId(session.session_id);
      setPhase('profiling');
    } catch (err) {
      setError('Failed to create session. Please try again.');
    }
  };

  const handleProfilingSubmit = async (answers) => {
    // Check profiling attention checks before proceeding
    const profilingAttnChecks = questions.filter((q) => q.is_attention_check && q.insert_after);
    let failures = 0;
    profilingAttnChecks.forEach((ac) => {
      const actual = answers[ac.id];
      if (actual !== ac.expected_answer) failures++;
    });

    setFailedAttnCount(failures);
    if (failures >= 3) {
      setPhase('terminated');
      return;
    }

    setPhase('buffer');
    setBufferMessage('Generating personalized responses based on your profile...');
    try {
      const result = await api('/api/profiling/submit', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, answers }),
      });
      setTasks(result.tasks);
      setPhase('evaluation');
    } catch (err) {
      setError('Failed to generate responses. Please try again.');
      setPhase('profiling');
    }
  };

  const handleAttnCheckFailed = () => {
    setFailedAttnCount((prev) => {
      const newCount = prev + 1;
      if (newCount >= 3) {
        setPhase('terminated');
      }
      return newCount;
    });
  };

  const handleEvalSubmit = async (evalData) => {
    try {
      await api('/api/evaluation/submit', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, ...evalData }),
      });
    } catch (err) {
      console.error('Failed to submit evaluation:', err);
    }
  };

  const handleEvalComplete = () => {
    setPhase('post_study');
  };

  const handlePostStudy = async (data) => {
    try {
      await api('/api/post-study/submit', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, data }),
      });
      setPhase('done');
    } catch (err) {
      setError('Failed to submit. Please try again.');
    }
  };

  if (error) {
    return (
      <div className="phase">
        <div className="card">
          <h2>Something went wrong</h2>
          <p>{error}</p>
          <button className="btn primary" onClick={() => { setError(null); setPhase('welcome'); }}>
            Start Over
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      {phase === 'welcome' && <Welcome onStart={handleStart} />}
      {phase === 'profiling' && questions.length > 0 && (
        <Profiling questions={questions} onSubmit={handleProfilingSubmit} />
      )}
      {phase === 'buffer' && <Buffer message={bufferMessage} />}
      {phase === 'evaluation' && tasks.length > 0 && (
        <TaskEvaluation
          tasks={tasks}
          sessionId={sessionId}
          evalAttentionChecks={evalAttentionChecks}
          onSubmitEval={handleEvalSubmit}
          onAttnCheckFailed={handleAttnCheckFailed}
          onComplete={handleEvalComplete}
        />
      )}
      {phase === 'post_study' && <PostStudy onSubmit={handlePostStudy} />}
      {phase === 'done' && <ThankYou sessionId={sessionId} />}
      {phase === 'terminated' && (
        <div className="phase thank-you">
          <div className="card">
            <h1>Study Ended</h1>
            <p>
              Unfortunately, we were unable to verify that responses were being
              provided attentively, so the study has been ended. We appreciate
              your time.
            </p>
            {sessionId && (
              <div className="info-box">
                <p><strong>Session ID:</strong> {sessionId}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
