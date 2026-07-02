import React, { useState, useEffect } from 'react';
import { scheduleAPI } from '../services/api';

export default function Scheduler() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [appointments, setAppointments] = useState([]);
  const [slots, setSlots] = useState([]);
  const [specialty, setSpecialty] = useState('General');
  const [loadingApts, setLoadingApts] = useState(false);

  const URGENCY_COLORS = ['', 'u1', 'u2', 'u3', 'u4', 'u5'];

  const SAMPLE_TEXTS = [
    "Mujhe kal subah doctor se milna hai, bahut dard ho raha hai",
    "I need an urgent appointment for severe chest pain",
    "Can I get a physiotherapy appointment for back pain next week?",
    "Mujhe heart specialist se milna hai, seene mein dard hai",
    "Book a general checkup for tomorrow morning"
  ];

  const loadAppointments = async () => {
    setLoadingApts(true);
    try {
      const res = await scheduleAPI.myAppointments();
      setAppointments(res.data.appointments || []);
    } catch (e) { console.error(e); }
    finally { setLoadingApts(false); }
  };

  const loadSlots = async () => {
    try {
      const res = await scheduleAPI.slots(specialty);
      setSlots(res.data.slots || []);
    } catch (e) { console.error(e); }
  };

  useEffect(() => { loadAppointments(); }, []);
  useEffect(() => { loadSlots(); }, [specialty]);

  const handleBook = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await scheduleAPI.request(text);
      setResult(res.data);
      await loadAppointments();
    } catch (err) {
      setError(err.response?.data?.detail || 'Booking failed. Please try again.');
    } finally { setLoading(false); }
  };

  const handleCancel = async (id) => {
    if (!window.confirm('Cancel this appointment?')) return;
    try {
      await scheduleAPI.cancel(id);
      await loadAppointments();
    } catch (e) { alert('Cancel failed.'); }
  };

  const formatSlot = (iso) => {
    if (!iso) return '';
    return new Date(iso).toLocaleString('en-IN', {
      weekday: 'short', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  };

  return (
    <div className="main-content">
      <h1 className="page-title">📅 Scheduling Engine</h1>
      <p className="page-subtitle">Multilingual appointment booking with urgency detection and fairness-aware slot assignment</p>

      <div className="grid-2">
        {/* ── Book Appointment ─────────────────────────────────────────── */}
        <div className="card">
          <div className="card-header">
            <div className="card-icon icon-teal">🗓️</div>
            <div>
              <div className="card-title">Book Appointment</div>
              <div className="card-subtitle">Type in English or Hindi/Hinglish</div>
            </div>
          </div>

          <form onSubmit={handleBook}>
            <div className="form-group">
              <label className="form-label">Your Request</label>
              <textarea
                id="schedule-input"
                className="form-textarea"
                placeholder="E.g.: Mujhe kal subah doctor se milna hai, bahut dard ho raha hai..."
                value={text}
                onChange={e => setText(e.target.value)}
                style={{ minHeight: '90px' }}
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <div className="form-label" style={{ marginBottom: '0.4rem' }}>Try a sample:</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                {SAMPLE_TEXTS.map((s, i) => (
                  <button key={i} type="button" className="badge badge-blue"
                    style={{ cursor: 'pointer', fontSize: '0.7rem', padding: '0.3rem 0.6rem' }}
                    onClick={() => setText(s)}>
                    {s.length > 30 ? s.slice(0, 30) + '…' : s}
                  </button>
                ))}
              </div>
            </div>
            <button id="btn-book" className="btn-primary" disabled={loading || !text.trim()}>
              {loading && <span className="loader" />}
              {loading ? 'Finding Best Slot...' : '🔍 Book Appointment'}
            </button>
          </form>

          {error && <div className="error-msg" style={{ marginTop: '1rem' }}>{error}</div>}

          {result && (
            <div className="result-panel">
              <div className="result-label">✅ Appointment Confirmed</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <span className="badge badge-green">🗓 {formatSlot(result.slot)}</span>
                <span className="badge badge-blue">👨‍⚕️ {result.doctor}</span>
                <span className="badge badge-amber">🏥 {result.specialty}</span>
                <span className="badge badge-blue">🌐 {result.language_detected}</span>
              </div>
              <div className="urgency-bar">
                <div className={`urgency-dot ${URGENCY_COLORS[result.urgency_score]}`} />
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Urgency: {result.urgency_score}/5 &nbsp;·&nbsp; Fairness Index: {result.fairness_score?.toFixed(2)}
                </span>
              </div>
              <div className="explanation-box">
                💡 {result.explanation}
              </div>
            </div>
          )}
        </div>

        {/* ── Available Slots ───────────────────────────────────────────── */}
        <div className="card">
          <div className="card-header">
            <div className="card-icon icon-blue">🕐</div>
            <div>
              <div className="card-title">Available Slots</div>
              <div className="card-subtitle">Browse slots by specialty</div>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Specialty</label>
            <select className="form-select" value={specialty} onChange={e => setSpecialty(e.target.value)}>
              {['General', 'Cardiology', 'Orthopedics', 'Neurology'].map(s => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </div>
          <div style={{ maxHeight: '320px', overflow: 'auto' }}>
            {slots.length === 0 ? (
              <div className="empty-state"><div className="empty-icon">📭</div>No slots found</div>
            ) : slots.slice(0, 12).map((slot, i) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '0.55rem 0.75rem', borderBottom: '1px solid var(--border)',
                fontSize: '0.8rem'
              }}>
                <span style={{ color: 'var(--text-secondary)' }}>👨‍⚕️ {slot.doctor}</span>
                <span className="badge badge-green">{formatSlot(slot.slot)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── My Appointments ─────────────────────────────────────────────── */}
      <div className="section" style={{ marginTop: '2rem' }}>
        <div className="section-title">📋 My Appointments
          <button className="btn-secondary" style={{ padding: '0.3rem 0.75rem', fontSize: '0.8rem', marginLeft: 'auto' }}
            onClick={loadAppointments}>Refresh</button>
        </div>
        {loadingApts ? <div className="empty-state"><span className="loader" /> Loading...</div>
          : appointments.length === 0 ? (
            <div className="empty-state"><div className="empty-icon">📭</div>No appointments yet. Book one above!</div>
          ) : (
            <div className="apt-list">
              {appointments.map(apt => (
                <div key={apt._id} className="apt-card">
                  <div className="apt-info">
                    <div className="apt-doctor">👨‍⚕️ {apt.doctor_name}
                      <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>({apt.specialty})</span>
                    </div>
                    <div className="apt-meta">
                      🗓 {formatSlot(apt.slot_time)} &nbsp;·&nbsp;
                      Urgency {apt.urgency}/5 &nbsp;·&nbsp;
                      Fairness {apt.fairness_score?.toFixed(2)}
                    </div>
                  </div>
                  <div className="apt-actions">
                    <span className={`badge ${apt.status === 'confirmed' ? 'badge-green' : 'badge-rose'}`}>
                      {apt.status}
                    </span>
                    {apt.status === 'confirmed' && (
                      <button className="btn-danger" onClick={() => handleCancel(apt._id)}>Cancel</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
      </div>
    </div>
  );
}
