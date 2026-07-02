import React, { useState, useEffect } from 'react';
import { profileAPI, wellnessAPI } from '../services/api';

export default function Profile() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reportLoading, setReportLoading] = useState(false);
  const [tab, setTab] = useState('overview');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const res = await profileAPI.me();
      setData(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const downloadReport = async () => {
    setReportLoading(true);
    try {
      const res = await profileAPI.reportPdf();
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'health_report.pdf';
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) { console.error(e); }
    finally { setReportLoading(false); }
  };

  const formatDate = (iso) => iso
    ? new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
    : '—';

  if (loading) return (
    <div className="main-content">
      <div className="empty-state"><span className="loader" /> Loading your profile...</div>
    </div>
  );

  const score = data?.health_score;
  const scoreAngle = score ? (score.score / 100) * 180 : 0;

  return (
    <div className="main-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <div>
          <h1 className="page-title" style={{ marginBottom: '0.2rem' }}>👤 My Profile</h1>
          <p className="page-subtitle">{data?.email}</p>
        </div>
        <button id="btn-download-report" className="btn-primary" onClick={downloadReport} disabled={reportLoading}
          style={{ whiteSpace: 'nowrap' }}>
          {reportLoading && <span className="loader" />}
          {reportLoading ? 'Generating...' : '📋 Download Health Report'}
        </button>
      </div>

      {/* ── Tabs ────────────────────────────────────────────────────────── */}
      <div className="tab-group">
        {[
          { id: 'overview', label: '🏥 Overview' },
          { id: 'appointments', label: '📅 Appointments' },
          { id: 'wellness', label: '💚 Wellness' },
        ].map(t => (
          <button key={t.id} className={`tab-btn ${tab === t.id ? 'active' : ''}`}
            onClick={() => setTab(t.id)}>{t.label}</button>
        ))}
      </div>

      {/* ── Overview Tab ─────────────────────────────────────────────────── */}
      {tab === 'overview' && (
        <>
          <div className="grid-2">
            {/* Health Score Gauge */}
            <div className="card" style={{ textAlign: 'center' }}>
              <div className="card-title" style={{ marginBottom: '1rem' }}>🤖 AI Health Score</div>
              {score && (
                <>
                  {/* Semi-circle gauge */}
                  <div style={{ position: 'relative', width: '180px', margin: '0 auto 1rem' }}>
                    <svg viewBox="0 0 200 110" width="180">
                      {/* Background arc */}
                      <path d="M 10 100 A 90 90 0 0 1 190 100"
                        fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="18" strokeLinecap="round" />
                      {/* Score arc */}
                      <path d="M 10 100 A 90 90 0 0 1 190 100"
                        fill="none"
                        stroke={score.risk_color}
                        strokeWidth="18"
                        strokeLinecap="round"
                        strokeDasharray={`${(score.score / 100) * 282} 282`}
                        style={{ transition: 'stroke-dasharray 1s ease' }}
                      />
                      {/* Score text */}
                      <text x="100" y="90" textAnchor="middle"
                        style={{ fill: score.risk_color, fontSize: '28px', fontWeight: 'bold' }}>
                        {score.score}
                      </text>
                      <text x="100" y="105" textAnchor="middle"
                        style={{ fill: '#8b949e', fontSize: '10px' }}>out of 100</text>
                    </svg>
                  </div>

                  <div style={{
                    display: 'inline-block', padding: '0.4rem 1.2rem',
                    background: score.risk_color + '22',
                    border: `1px solid ${score.risk_color}44`,
                    borderRadius: 'var(--radius-sm)',
                    color: score.risk_color, fontWeight: 700, marginBottom: '1rem'
                  }}>
                    {score.risk_level}
                  </div>

                  {/* Breakdown */}
                  <div style={{ textAlign: 'left', fontSize: '0.8rem' }}>
                    {Object.entries(score.breakdown).filter(([k]) => k !== 'base').map(([k, v]) => {
                      const label = k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                      const positive = v >= 0;
                      return (
                        <div key={k} style={{ display: 'flex', justifyContent: 'space-between',
                          padding: '0.3rem 0', borderBottom: '1px solid var(--border)' }}>
                          <span style={{ color: 'var(--text-muted)' }}>{label}</span>
                          <span style={{ color: positive ? '#22c55e' : '#f43f5e', fontWeight: 600 }}>
                            {positive ? '+' : ''}{v}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </div>

            {/* Recommendations */}
            <div className="card">
              <div className="card-header">
                <div className="card-icon icon-amber">💡</div>
                <div>
                  <div className="card-title">Personalised Recommendations</div>
                  <div className="card-subtitle">AI-generated based on your history</div>
                </div>
              </div>
              <ol className="step-list">
                {score?.recommendations?.map((rec, i) => (
                  <li key={i} className="step-item">
                    <div className="step-num">{i + 1}</div>
                    <span>{rec}</span>
                  </li>
                ))}
              </ol>

              {/* Quick stats */}
              <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem' }}>
                <div style={{ textAlign: 'center', flex: 1 }}>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-primary)' }}>
                    {data?.appointment_count || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Appointments</div>
                </div>
                <div style={{ textAlign: 'center', flex: 1 }}>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-secondary)' }}>
                    {data?.wellness_feedback_count || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Wellness Feedbacks</div>
                </div>
                <div style={{ textAlign: 'center', flex: 1 }}>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#a78bfa' }}>
                    {data?.conditions?.length || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Conditions</div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* ── Appointments Tab ──────────────────────────────────────────────── */}
      {tab === 'appointments' && (
        <div className="card">
          {!data?.recent_appointments?.length
            ? <div className="empty-state"><div className="empty-icon">📭</div>No appointments yet.</div>
            : <div className="apt-list">
                {data.recent_appointments.map((a, i) => (
                  <div key={i} className="apt-card">
                    <div className="apt-info">
                      <div className="apt-doctor">👨‍⚕️ {a.doctor_name}
                        <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          ({a.specialty})
                        </span>
                      </div>
                      <div className="apt-meta">
                        🗓 {formatDate(a.slot_time)} &nbsp;·&nbsp;
                        ⚡ Urgency {a.urgency}/5
                      </div>
                    </div>
                    <span className={`badge ${a.status === 'confirmed' ? 'badge-green' : 'badge-rose'}`}>
                      {a.status}
                    </span>
                  </div>
                ))}
              </div>
          }
        </div>
      )}

      {/* ── Wellness Personalization Tab ──────────────────────────────────── */}
      {tab === 'wellness' && (
        <div className="grid-2">
          {Object.entries(data?.wellness_personalization || {}).map(([mod, p]) => {
            const icons = { diet: '🥗', yoga: '🧘', meditation: '🧠' };
            return (
              <div key={mod} className="card">
                <div className="card-header">
                  <div className="card-icon icon-teal">{icons[mod] || '💚'}</div>
                  <div>
                    <div className="card-title">{mod.charAt(0).toUpperCase() + mod.slice(1)} Plan</div>
                    <div className="card-subtitle">
                      {p.adapted ? `${p.total_feedbacks} feedbacks · Avg ${p.avg_rating}/5` : 'No feedback yet'}
                    </div>
                  </div>
                </div>
                {p.adapted && p.hints?.length > 0
                  ? <ul style={{ padding: '0 0 0 1rem', margin: 0 }}>
                      {p.hints.map((h, i) => (
                        <li key={i} style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                          {h}
                        </li>
                      ))}
                    </ul>
                  : <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      Rate your {mod} plans to get personalised adaptations.
                    </p>
                }
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
