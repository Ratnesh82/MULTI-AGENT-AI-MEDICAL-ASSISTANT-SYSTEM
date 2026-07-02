import React, { useState } from 'react';
import { wellnessAPI } from '../services/api';

/* ── Diet Planner ─────────────────────────────────────────────────────────── */
function DietPlanner() {
  const [form, setForm] = useState({ condition: 'diabetes', preferences: 'vegetarian', region: 'North Indian' });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);

  const CONDITIONS = [
    'diabetes', 'hypertension', 'thyroid', 'obesity',
    'pcos', 'arthritis', 'heart_disease', 'general'
  ];

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await wellnessAPI.diet(form.condition, form.preferences, form.region);
      setResult(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const downloadPdf = async () => {
    setPdfLoading(true);
    try {
      const res = await wellnessAPI.dietPdf(form.condition, form.preferences, form.region);
      const blob = new Blob([res.data], { type: res.headers['content-type'] || 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `diet_plan_${form.condition}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) { console.error(err); }
    finally { setPdfLoading(false); }
  };

  return (
    <div className="grid-2">
      <div className="card">
        <div className="card-header">
          <div className="card-icon icon-teal">🥗</div>
          <div>
            <div className="card-title">Diet Planner</div>
            <div className="card-subtitle">7-day Indian diet plan by condition</div>
          </div>
        </div>
        <form onSubmit={submit}>
          <div className="form-group">
            <label className="form-label">Health Condition</label>
            <select id="diet-condition" className="form-select" value={form.condition}
              onChange={e => setForm(f => ({ ...f, condition: e.target.value }))}>
              {CONDITIONS.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Dietary Preference</label>
            <select className="form-select" value={form.preferences}
              onChange={e => setForm(f => ({ ...f, preferences: e.target.value }))}>
              <option>vegetarian</option>
              <option>vegan</option>
              <option>non-vegetarian</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Region</label>
            <input className="form-input" value={form.region}
              onChange={e => setForm(f => ({ ...f, region: e.target.value }))} placeholder="North Indian" />
          </div>
          <button id="btn-diet" className="btn-primary" disabled={loading}>
            {loading && <span className="loader" />}
            {loading ? 'Generating...' : '🥗 Generate Diet Plan'}
          </button>
        </form>
      </div>

      {result && (
        <div className="card" style={{ gridColumn: 'span 1' }}>
          <div className="result-label">7-Day Plan for {result.condition}</div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>{result.guidelines}</p>
          <div style={{ overflowX: 'auto' }}>
            <table className="diet-table">
              <thead>
                <tr>
                  <th>Day</th><th>Breakfast</th><th>Lunch</th><th>Dinner</th><th>Snacks</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(result.plan).map(([day, meals]) => (
                  <tr key={day}>
                    <td className="diet-day">{day}</td>
                    <td>{meals.breakfast}</td>
                    <td>{meals.lunch}</td>
                    <td>{meals.dinner}</td>
                    <td>{meals.snacks}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ marginTop: '1rem' }}>
            <div className="result-label">🚫 Avoid</div>
            <div className="nlp-chips">
              {result.avoid?.map((item, i) => (
                <span key={i} className="badge badge-rose">{item}</span>
              ))}
            </div>
          </div>
          <div className="disclaimer">⚕️ {result.disclaimer}</div>
          <button id="btn-diet-pdf" className="btn-secondary"
            style={{ marginTop: '1rem', width: '100%' }}
            onClick={downloadPdf} disabled={pdfLoading}>
            {pdfLoading && <span className="loader" />}
            {pdfLoading ? 'Generating PDF...' : '📄 Download Diet Plan (PDF)'}
          </button>
        </div>
      )}
    </div>
  );
}

/* ── Yoga Recommender ─────────────────────────────────────────────────────── */
function YogaRecommender() {
  const [form, setForm] = useState({ condition: 'back_pain', severity: 'mild' });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const CONDITIONS = ['back_pain', 'hypertension', 'diabetes', 'anxiety', 'general'];

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await wellnessAPI.yoga(form.condition, form.severity);
      setResult(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  return (
    <div className="grid-2">
      <div className="card">
        <div className="card-header">
          <div className="card-icon icon-purple">🧘</div>
          <div>
            <div className="card-title">Yoga Recommender</div>
            <div className="card-subtitle">Safe poses tailored to your condition</div>
          </div>
        </div>
        <form onSubmit={submit}>
          <div className="form-group">
            <label className="form-label">Health Condition</label>
            <select id="yoga-condition" className="form-select" value={form.condition}
              onChange={e => setForm(f => ({ ...f, condition: e.target.value }))}>
              {CONDITIONS.map(c => <option key={c}>{c.replace('_', ' ')}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Severity</label>
            <select className="form-select" value={form.severity}
              onChange={e => setForm(f => ({ ...f, severity: e.target.value }))}>
              <option>mild</option>
              <option>moderate</option>
              <option>severe</option>
            </select>
          </div>
          <button id="btn-yoga" className="btn-primary" disabled={loading}>
            {loading && <span className="loader" />}
            {loading ? 'Finding Poses...' : '🧘 Get Yoga Plan'}
          </button>
        </form>
      </div>

      {result && (
        <div className="card">
          <div className="result-label">Yoga for {result.condition?.replace('_', ' ')}</div>
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
              ✅ Recommended Poses
            </div>
            <ul className="pose-list">
              {result.recommended_poses?.map((p, i) => (
                <li key={i} className="pose-item"><div className="pose-dot" />{p}</li>
              ))}
            </ul>
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--accent-rose)', marginBottom: '0.5rem' }}>
              🚫 Avoid These Poses
            </div>
            <ul className="pose-list">
              {result.avoid_poses?.map((p, i) => (
                <li key={i} className="pose-item avoid-item"><div className="pose-dot" />{p}</li>
              ))}
            </ul>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span className="badge badge-green">⏱ {result.session_duration}</span>
          </div>
          <div className="disclaimer">⚕️ {result.safety_note}</div>
        </div>
      )}
    </div>
  );
}

/* ── Meditation System ────────────────────────────────────────────────────── */
function Meditation() {
  const [form, setForm] = useState({ goal: 'stress', feedback: '' });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fbSent, setFbSent] = useState(false);

  const GOALS = ['stress', 'sleep', 'focus', 'general'];

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await wellnessAPI.meditation(form.goal, form.feedback || null);
      setResult(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const sendFeedback = async (rating) => {
    try {
      await wellnessAPI.feedback('meditation', rating, `Goal: ${form.goal}`);
      setFbSent(true);
    } catch (e) { console.error(e); }
  };

  return (
    <div className="grid-2">
      <div className="card">
        <div className="card-header">
          <div className="card-icon icon-amber">🧠</div>
          <div>
            <div className="card-title">Meditation System</div>
            <div className="card-subtitle">Daily practice, adaptive to your feedback</div>
          </div>
        </div>
        <form onSubmit={submit}>
          <div className="form-group">
            <label className="form-label">Goal</label>
            <select id="meditation-goal" className="form-select" value={form.goal}
              onChange={e => setForm(f => ({ ...f, goal: e.target.value }))}>
              {GOALS.map(g => <option key={g}>{g}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Previous Feedback (optional)</label>
            <input className="form-input" placeholder="e.g. 'too long', 'still stressed'..."
              value={form.feedback} onChange={e => setForm(f => ({ ...f, feedback: e.target.value }))} />
          </div>
          <button id="btn-meditate" className="btn-primary" disabled={loading}>
            {loading && <span className="loader" />}
            {loading ? 'Planning...' : '🧠 Get Meditation Plan'}
          </button>
        </form>
      </div>

      {result && (
        <div className="card">
          <div className="result-label">{result.technique}</div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
            <span className="badge badge-purple" style={{ background: 'rgba(139,92,246,0.12)', color: '#a78bfa', border: '1px solid rgba(139,92,246,0.3)' }}>
              ⏱ {result.duration}
            </span>
            <span className="badge badge-blue">{result.frequency}</span>
            {result.adapted_from_feedback && <span className="badge badge-amber">✨ Adapted from feedback</span>}
          </div>
          <div className="section-title" style={{ fontSize: '0.85rem', marginBottom: '0.75rem' }}>Daily Steps</div>
          <ol className="step-list">
            {result.daily_steps?.map((step, i) => (
              <li key={i} className="step-item">
                <div className="step-num">{i + 1}</div>
                <span>{step}</span>
              </li>
            ))}
          </ol>
          <div className="pro-tip"><strong>💡 Pro Tip:</strong> {result.pro_tip}</div>

          {/* Feedback */}
          {!fbSent ? (
            <div style={{ marginTop: '1.25rem' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Rate this plan:</div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {[1, 2, 3, 4, 5].map(r => (
                  <button key={r} className="badge badge-green" style={{ cursor: 'pointer' }}
                    onClick={() => sendFeedback(r)}>{'⭐'.repeat(r)}</button>
                ))}
              </div>
            </div>
          ) : (
            <div className="success-msg" style={{ marginTop: '1rem', marginBottom: 0 }}>✅ Feedback recorded! Plan will adapt next time.</div>
          )}
        </div>
      )}
    </div>
  );
}

/* ── Wellness Hub (tab container) ─────────────────────────────────────────── */
export default function Wellness() {
  const [tab, setTab] = useState('diet');
  const TABS = [
    { id: 'diet', label: '🥗 Diet Planner' },
    { id: 'yoga', label: '🧘 Yoga' },
    { id: 'meditation', label: '🧠 Meditation' },
  ];

  return (
    <div className="main-content">
      <h1 className="page-title">💚 Wellness Engine</h1>
      <p className="page-subtitle">Personalized diet plans, yoga recommendations, and adaptive meditation — all India-centric</p>

      <div className="tab-group">
        {TABS.map(t => (
          <button key={t.id} id={`tab-${t.id}`} className={`tab-btn ${tab === t.id ? 'active' : ''}`}
            onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'diet' && <DietPlanner />}
      {tab === 'yoga' && <YogaRecommender />}
      {tab === 'meditation' && <Meditation />}
    </div>
  );
}
