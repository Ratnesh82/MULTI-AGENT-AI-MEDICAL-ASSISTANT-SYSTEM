import React, { useState } from 'react';
import { authAPI } from '../services/api';

export default function AuthScreen({ onLogin }) {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [form, setForm] = useState({ name: '', email: '', password: '', age: '', phone: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const res = await authAPI.login(form.email, form.password);
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('userName', res.data.name);
      onLogin(res.data.name);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check credentials.');
    } finally { setLoading(false); }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true); setError(''); setSuccess('');
    try {
      await authAPI.register({ ...form, age: parseInt(form.age) || 0 });
      setSuccess('Registration successful! Please log in.');
      setMode('login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.');
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-screen">
      <div className="auth-box">
        <div className="auth-logo">
          <div className="logo-mark">🏥</div>
          <h2>FCMAS-W</h2>
          <p>Fairness-Constrained Healthcare AI</p>
        </div>

        {error && <div className="error-msg">{error}</div>}
        {success && <div className="success-msg">{success}</div>}

        {mode === 'login' ? (
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input id="login-email" className="form-input" type="email" placeholder="patient@example.com"
                value={form.email} onChange={e => update('email', e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input id="login-password" className="form-input" type="password" placeholder="••••••••"
                value={form.password} onChange={e => update('password', e.target.value)} required />
            </div>
            <button id="btn-login" className="btn-primary" style={{ width: '100%' }} disabled={loading}>
              {loading && <span className="loader" />}
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister}>
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input id="reg-name" className="form-input" placeholder="Rahul Kumar"
                value={form.name} onChange={e => update('name', e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input id="reg-email" className="form-input" type="email" placeholder="rahul@example.com"
                value={form.email} onChange={e => update('email', e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input id="reg-password" className="form-input" type="password" placeholder="••••••••"
                value={form.password} onChange={e => update('password', e.target.value)} required />
            </div>
            <div className="grid-2" style={{ marginBottom: '1.25rem' }}>
              <div>
                <label className="form-label">Age</label>
                <input id="reg-age" className="form-input" type="number" placeholder="30"
                  value={form.age} onChange={e => update('age', e.target.value)} />
              </div>
              <div>
                <label className="form-label">Phone</label>
                <input id="reg-phone" className="form-input" placeholder="+91 98765 43210"
                  value={form.phone} onChange={e => update('phone', e.target.value)} />
              </div>
            </div>
            <button id="btn-register" className="btn-primary" style={{ width: '100%' }} disabled={loading}>
              {loading && <span className="loader" />}
              {loading ? 'Registering...' : 'Create Account'}
            </button>
          </form>
        )}

        <div className="auth-toggle">
          {mode === 'login' ? (
            <>Don't have an account?<button onClick={() => { setMode('register'); setError(''); }}>Register</button></>
          ) : (
            <>Already have an account?<button onClick={() => { setMode('login'); setError(''); }}>Login</button></>
          )}
        </div>
      </div>
    </div>
  );
}
