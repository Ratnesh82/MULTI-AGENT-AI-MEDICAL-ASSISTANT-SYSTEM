import React, { useState } from 'react';
import { wellnessAPI } from '../services/api';

export default function NLPAnalyzer() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const SAMPLES = [
    { label: 'EN - Appointment', text: 'I need an urgent appointment for chest pain tomorrow morning' },
    { label: 'HI - Diet', text: 'Mujhe diabetes ke liye kya khana chahiye' },
    { label: 'EN - Yoga', text: 'Yoga poses for back pain rehabilitation' },
    { label: 'HI - Cancel', text: 'Meri appointment cancel karo please' },
    { label: 'EN - Meditation', text: 'I need help with stress relief meditation' },
    { label: 'HI - Emergency', text: 'Bahut tez seene mein dard hai, emergency hai' },
  ];

  const analyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const res = await wellnessAPI.analyzeText(text);
      setResult(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const INTENT_COLORS = {
    book_appointment: 'badge-green',
    cancel_appointment: 'badge-rose',
    diet_plan: 'badge-amber',
    yoga: 'badge-blue',
    meditation: 'badge-blue',
    general_info: 'badge-amber',
  };

  return (
    <div className="main-content">
      <h1 className="page-title">🧬 NLP Analyzer</h1>
      <p className="page-subtitle">Live multilingual intent classifier — test English and Hindi/Hinglish inputs</p>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <div className="card-icon icon-blue">🧬</div>
            <div>
              <div className="card-title">NLP Pipeline</div>
              <div className="card-subtitle">langdetect + keyword intent classifier</div>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Input Text (English / Hindi / Hinglish)</label>
            <textarea
              id="nlp-input"
              className="form-textarea"
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Type anything in English or Hindi..."
              style={{ minHeight: '100px' }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <div className="form-label" style={{ marginBottom: '0.5rem' }}>Quick samples:</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {SAMPLES.map((s, i) => (
                <button key={i} className="badge badge-blue"
                  style={{ cursor: 'pointer', fontSize: '0.7rem' }}
                  onClick={() => setText(s.text)}>
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          <button id="btn-analyze" className="btn-primary" onClick={analyze} disabled={loading || !text.trim()}>
            {loading && <span className="loader" />}
            {loading ? 'Analyzing...' : '🔍 Analyze Text'}
          </button>
        </div>

        {result && (
          <div className="card">
            <div className="result-label">🧬 NLP Analysis Results</div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {/* Language */}
              <div style={{ padding: '0.75rem', background: 'rgba(14,165,233,0.06)', borderRadius: 'var(--radius-xs)', border: '1px solid rgba(14,165,233,0.2)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.3rem' }}>DETECTED LANGUAGE</div>
                <div style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--accent-secondary)' }}>
                  {result.language_name} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>({result.language_code})</span>
                </div>
              </div>

              {/* Intent */}
              <div style={{ padding: '0.75rem', background: 'rgba(0,201,167,0.06)', borderRadius: 'var(--radius-xs)', border: '1px solid rgba(0,201,167,0.2)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.3rem' }}>INTENT CLASSIFIED</div>
                <span className={`badge ${INTENT_COLORS[result.intent] || 'badge-blue'}`}
                  style={{ fontSize: '0.9rem', padding: '0.4rem 0.9rem' }}>
                  {result.intent?.replace(/_/g, ' ').toUpperCase()}
                </span>
              </div>

              {/* Entities */}
              {result.entities && (
                <div style={{ padding: '0.75rem', background: 'rgba(139,92,246,0.06)', borderRadius: 'var(--radius-xs)', border: '1px solid rgba(139,92,246,0.2)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>EXTRACTED ENTITIES</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {result.entities.specialty_hint && (
                      <span className="badge badge-blue">🏥 {result.entities.specialty_hint}</span>
                    )}
                    {result.entities.time_hint && (
                      <span className="badge badge-amber">📅 {result.entities.time_hint}</span>
                    )}
                    {result.entities.conditions?.map((c, i) => (
                      <span key={i} className="badge badge-green">🩺 {c}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Original text */}
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic', borderTop: '1px solid var(--border)', paddingTop: '0.75rem' }}>
                "{result.original_text}"
              </div>
            </div>
          </div>
        )}

        {/* Pipeline explanation card */}
        {!result && (
          <div className="card">
            <div className="card-header">
              <div className="card-icon icon-purple">⚙️</div>
              <div>
                <div className="card-title">How It Works</div>
                <div className="card-subtitle">3-stage NLP pipeline</div>
              </div>
            </div>
            <ol className="step-list">
              {[
                { n: 1, text: 'Language Detection — langdetect identifies English, Hindi, Hinglish, and 50+ languages' },
                { n: 2, text: 'Intent Classification — keyword-based matcher routes to book/cancel/diet/yoga/meditation intents' },
                { n: 3, text: 'Entity Extraction — extracts specialty, urgency indicators, time hints, and health conditions' },
              ].map(s => (
                <li key={s.n} className="step-item">
                  <div className="step-num">{s.n}</div>
                  <span>{s.text}</span>
                </li>
              ))}
            </ol>
            <div className="pro-tip" style={{ marginTop: '1rem' }}>
              <strong>🚀 Upgrade Path:</strong> Replace with fine-tuned IndicBERT for state-of-the-art Hindi NLU.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
