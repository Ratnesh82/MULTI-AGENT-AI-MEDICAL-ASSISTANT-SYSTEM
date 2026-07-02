import React, { useState, useEffect } from 'react';
import AuthScreen from './components/AuthScreen';
import Scheduler from './components/Scheduler';
import Wellness from './components/Wellness';
import AdminDashboard from './components/AdminDashboard';
import NLPAnalyzer from './components/NLPAnalyzer';
import Profile from './components/Profile';
import { profileAPI } from './services/api';
import './index.css';

export default function App() {
  const [user, setUser] = useState(null);
  const [page, setPage] = useState('home');
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const name = localStorage.getItem('userName');
    if (token && name) {
      setUser(name);
      loadNotificationCount();
    }
  }, []);

  const loadNotificationCount = async () => {
    try {
      const res = await profileAPI.notifications();
      setUnread(res.data.unread || 0);
    } catch (e) { /* silent */ }
  };

  const handleLogin = (name) => {
    setUser(name);
    setPage('schedule');
    setTimeout(loadNotificationCount, 500);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userName');
    setUser(null);
    setPage('home');
    setUnread(0);
  };

  if (!user) return <AuthScreen onLogin={handleLogin} />;

  const NAV = [
    { id: 'home',     label: '🏠 Home' },
    { id: 'schedule', label: '📅 Scheduling' },
    { id: 'wellness', label: '💚 Wellness' },
    { id: 'nlp',      label: '🧬 NLP Analyzer' },
    { id: 'admin',    label: '🛡️ Admin' },
    { id: 'profile',  label: '👤 Profile' },
  ];

  return (
    <div className="app-wrapper">
      {/* ── Navbar ─────────────────────────────────────────────────── */}
      <nav className="navbar">
        <a className="navbar-brand" href="#" onClick={() => setPage('home')}>
          <span className="logo-icon">🏥</span>
          FCMAS-W
        </a>
        <div className="navbar-links">
          {NAV.map(n => (
            <button key={n.id} id={`nav-${n.id}`}
              className={`nav-btn ${page === n.id ? 'active' : ''}`}
              onClick={() => setPage(n.id)}>
              {n.label}
            </button>
          ))}
        </div>
        <div className="nav-user">
          {/* Notification Bell */}
          <button className="notif-bell" id="btn-notifications"
            onClick={() => setPage('profile')}
            title="View notifications">
            🔔
            {unread > 0 && <span className="notif-badge">{unread}</span>}
          </button>
          <span>👤 {user}</span>
          <button id="btn-logout" className="btn-logout" onClick={handleLogout}>Logout</button>
        </div>
      </nav>

      {/* ── Pages ──────────────────────────────────────────────────── */}
      {page === 'home'     && <HomePage onNavigate={setPage} userName={user} />}
      {page === 'schedule' && <Scheduler />}
      {page === 'wellness' && <Wellness />}
      {page === 'nlp'      && <NLPAnalyzer />}
      {page === 'admin'    && <AdminDashboard />}
      {page === 'profile'  && <Profile />}
    </div>
  );
}

/* ── Home / Dashboard Page ─────────────────────────────────────────────────── */
function HomePage({ onNavigate, userName }) {
  return (
    <div>
      <div className="hero">
        <div className="hero-badge">⚕️ AI-Powered Healthcare System v3.0</div>
        <h1>Welcome back, {userName.split(' ')[0]}! 👋</h1>
        <p>
          FCMAS-W gives you fairness-aware appointment scheduling with multilingual
          support, personalized wellness recommendations, and AI health scoring — all in one place.
        </p>
        <div className="hero-actions">
          <button id="hero-btn-schedule" className="btn-primary" onClick={() => onNavigate('schedule')}>
            📅 Book Appointment
          </button>
          <button id="hero-btn-wellness" className="btn-secondary" onClick={() => onNavigate('wellness')}>
            💚 Explore Wellness
          </button>
        </div>
      </div>

      <div className="main-content" style={{ paddingTop: 0 }}>
        <div className="stats-row">
          {[
            { value: '5',    label: 'Specialist Doctors' },
            { value: '8',    label: 'Diet Conditions' },
            { value: '11',   label: 'Yoga Conditions' },
            { value: 'Hi/En', label: 'Languages' },
            { value: 'AI',   label: 'Health Score' },
          ].map((s, i) => (
            <div key={i} className="stat-card">
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>

        <div className="grid-2">
          {[
            {
              id: 'schedule', icon: '📅', iconClass: 'icon-teal',
              title: 'Scheduling Engine', sub: 'Urgency-aware · Fairness-indexed · Multilingual',
              desc: 'Type in English or Hindi/Hinglish. AI detects language, classifies intent, scores urgency 1–5, and assigns the fairest slot with a full explanation.',
              tags: [['badge-green','🌐 Multilingual'], ['badge-blue','⚡ Urgency Scoring'], ['badge-amber','⚖️ Jain Fairness Index']],
            },
            {
              id: 'wellness', icon: '💚', iconClass: 'icon-purple',
              title: 'Wellness Engine', sub: 'Diet · Yoga · Meditation — 8 conditions',
              desc: 'Personalized 7-day Indian diet plans (PDF download), condition-safe yoga, and adaptive meditation for diabetes, hypertension, thyroid, PCOS, obesity, arthritis & more.',
              tags: [['badge-green','🥗 PDF Diet Plans'], ['badge-blue','🧘 Safe Yoga'], ['badge-amber','🧠 Adaptive Meditation']],
            },
            {
              id: 'profile', icon: '🤖', iconClass: 'icon-blue',
              title: 'AI Health Score', sub: 'Risk scoring · Personalization · PDF Report',
              desc: 'Get your personalized AI health score (0–100) based on conditions, appointment urgency history, and wellness engagement. Download your full health report as PDF.',
              tags: [['badge-green','📊 Risk Gauge'], ['badge-blue','💡 Recommendations'], ['badge-amber','📋 Full PDF Report']],
            },
            {
              id: 'admin', icon: '🛡️', iconClass: 'icon-amber',
              title: 'Admin Dashboard', sub: 'Stats · Fairness Analytics · Doctor Management',
              desc: 'Monitor all appointments, track 7-day fairness index, view urgency distribution, and manage doctors — all in a real-time admin panel.',
              tags: [['badge-green','📊 Live Stats'], ['badge-blue','⚖️ Fairness Chart'], ['badge-amber','👨‍⚕️ Doctor Mgmt']],
            },
          ].map(m => (
            <div key={m.id} className="card" style={{ cursor: 'pointer' }} onClick={() => onNavigate(m.id)}>
              <div className="card-header">
                <div className={`card-icon ${m.iconClass}`}>{m.icon}</div>
                <div>
                  <div className="card-title">{m.title}</div>
                  <div className="card-subtitle">{m.sub}</div>
                </div>
              </div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: '1.7' }}>{m.desc}</p>
              <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {m.tags.map(([cls, label], i) => <span key={i} className={`badge ${cls}`}>{label}</span>)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
