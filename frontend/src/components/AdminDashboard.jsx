import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [fairness, setFairness] = useState([]);
  const [tab, setTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [s, d, f] = await Promise.all([
        adminAPI.stats(),
        adminAPI.doctors(),
        adminAPI.fairnessAnalytics(),
      ]);
      setStats(s.data);
      setDoctors(d.data.doctors || []);
      setFairness(f.data.fairness_over_time || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const loadAppointments = async (status = null) => {
    try {
      const res = await adminAPI.appointments(status);
      setAppointments(res.data.appointments || []);
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    loadAll();
    loadAppointments();
  }, []);

  const formatDate = (iso) => iso ? new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
  }) : '—';

  const fairnessColor = (f) => f >= 0.8 ? 'badge-green' : f >= 0.6 ? 'badge-amber' : 'badge-rose';

  return (
    <div className="main-content">
      <h1 className="page-title">🛡️ Admin Dashboard</h1>
      <p className="page-subtitle">System-wide analytics, appointments, and doctor management</p>

      {/* ── Tabs ──────────────────────────────────────────────────────── */}
      <div className="tab-group">
        {[
          { id: 'overview', label: '📊 Overview' },
          { id: 'appointments', label: '📋 Appointments' },
          { id: 'doctors', label: '👨‍⚕️ Doctors' },
          { id: 'fairness', label: '⚖️ Fairness' },
        ].map(t => (
          <button key={t.id} className={`tab-btn ${tab === t.id ? 'active' : ''}`}
            onClick={() => setTab(t.id)}>{t.label}</button>
        ))}
      </div>

      {loading && <div className="empty-state"><span className="loader" /> Loading dashboard...</div>}

      {/* ── Overview Tab ─────────────────────────────────────────────── */}
      {!loading && tab === 'overview' && stats && (
        <>
          <div className="stats-row">
            <div className="stat-card">
              <div className="stat-value">{stats.patients}</div>
              <div className="stat-label">Total Patients</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.appointments?.confirmed}</div>
              <div className="stat-label">Confirmed Appointments</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.appointments?.cancelled}</div>
              <div className="stat-label">Cancelled</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: stats.fairness_index >= 0.7 ? 'var(--accent-primary)' : 'var(--accent-amber)' }}>
                {stats.fairness_index?.toFixed(2)}
              </div>
              <div className="stat-label">Fairness Index</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.wellness_feedbacks}</div>
              <div className="stat-label">Wellness Feedbacks</div>
            </div>
          </div>

          {/* Urgency Distribution */}
          <div className="card">
            <div className="card-header">
              <div className="card-icon icon-amber">⚡</div>
              <div>
                <div className="card-title">Urgency Distribution</div>
                <div className="card-subtitle">Last 50 appointments</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              {Object.entries(stats.urgency_distribution || {}).map(([level, count]) => {
                const colors = { '1': '#22c55e', '2': '#84cc16', '3': '#f59e0b', '4': '#f97316', '5': '#f43f5e' };
                return (
                  <div key={level} style={{ textAlign: 'center', flex: 1, minWidth: 80 }}>
                    <div style={{
                      height: `${Math.max(20, (count / Math.max(...Object.values(stats.urgency_distribution))) * 100)}px`,
                      background: colors[level],
                      borderRadius: '6px 6px 0 0',
                      transition: 'height 0.5s ease',
                      minHeight: 20,
                    }} />
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>L{level}</div>
                    <div style={{ fontSize: '1rem', fontWeight: 700, color: colors[level] }}>{count}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}

      {/* ── Appointments Tab ──────────────────────────────────────────── */}
      {!loading && tab === 'appointments' && (
        <div className="card">
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
            {[null, 'confirmed', 'cancelled'].map(s => (
              <button key={String(s)} className="btn-secondary"
                style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
                onClick={() => loadAppointments(s)}>
                {s === null ? 'All' : s.charAt(0).toUpperCase() + s.slice(1)}
              </button>
            ))}
          </div>
          {appointments.length === 0
            ? <div className="empty-state"><div className="empty-icon">📭</div>No appointments found.</div>
            : <div className="apt-list">
                {appointments.map(a => (
                  <div key={a._id} className="apt-card">
                    <div className="apt-info">
                      <div className="apt-doctor">👨‍⚕️ {a.doctor_name}
                        <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>({a.specialty})</span>
                      </div>
                      <div className="apt-meta">
                        Patient ID: {a.patient_id?.slice(-6)} &nbsp;·&nbsp;
                        🗓 {formatDate(a.slot_time)} &nbsp;·&nbsp;
                        Urgency {a.urgency}/5
                      </div>
                    </div>
                    <div>
                      <span className={`badge ${a.status === 'confirmed' ? 'badge-green' : 'badge-rose'}`}>
                        {a.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
          }
        </div>
      )}

      {/* ── Doctors Tab ───────────────────────────────────────────────── */}
      {!loading && tab === 'doctors' && (
        <div className="card">
          <div className="grid-3" style={{ gap: '1rem' }}>
            {doctors.map(d => (
              <div key={d.id} style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-sm)',
                padding: '1rem'
              }}>
                <div style={{ fontWeight: 600, marginBottom: '0.4rem' }}>👨‍⚕️ {d.name}</div>
                <div className="apt-meta">{d.specialty}</div>
                <div style={{ marginTop: '0.5rem' }}>
                  <span className="badge badge-green">
                    {d.available_slots_count} slots available
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Fairness Tab ──────────────────────────────────────────────── */}
      {!loading && tab === 'fairness' && (
        <div className="card">
          <div className="card-header">
            <div className="card-icon icon-teal">⚖️</div>
            <div>
              <div className="card-title">Fairness Index — Last 7 Days</div>
              <div className="card-subtitle">Jain's Fairness Index (0–1, higher is fairer)</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '1rem', height: '180px', padding: '1rem 0' }}>
            {fairness.map((d, i) => {
              const h = Math.max(20, d.fairness_index * 150);
              const col = d.fairness_index >= 0.8 ? '#00c9a7' : d.fairness_index >= 0.6 ? '#f59e0b' : '#f43f5e';
              return (
                <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{d.fairness_index?.toFixed(2)}</span>
                  <div style={{ width: '100%', height: `${h}px`, background: col, borderRadius: '6px 6px 0 0', transition: 'height 0.5s' }} />
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                    {new Date(d.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}
                  </span>
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{d.appointments} apts</span>
                </div>
              );
            })}
          </div>
          <div style={{ marginTop: '1rem', display: 'flex', gap: '0.75rem' }}>
            <span className="badge badge-green">≥0.8 Fair</span>
            <span className="badge badge-amber">0.6–0.8 Moderate</span>
            <span className="badge badge-rose">&lt;0.6 Imbalanced</span>
          </div>
        </div>
      )}
    </div>
  );
}
