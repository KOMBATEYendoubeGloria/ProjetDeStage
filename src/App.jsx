import React, { useState } from 'react';
import api from './api/axios';
import './App.css';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

function App() {
  const [activeTab, setActiveTab] = useState('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [signupData, setSignupData] = useState({ username: '', email: '', password: '' });
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await api.post('auth/login/', loginData);
      await login(res.data.access, res.data.refresh);
      localStorage.setItem('username', loginData.username);
      navigate('/dashboard');
    } catch (err) {
      setError('Nom d’utilisateur ou mot de passe incorrect.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post('auth/register/', signupData);
      setActiveTab('login');
    } catch (err) {
      const msg = err.response?.data
        ? Object.values(err.response.data).flat().join(' ')
        : 'Erreur lors de l’inscription.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleSocialLogin = async (provider) => {
    try {
      const res = await api.get(`auth/${provider}/url/`);
      window.location.href = res.data.url;
    } catch {
      setError(`Impossible de contacter ${provider}.`);
    }
  };

  return (
    <div className="login-page">
      <div className="card-container">

        {/* PANNEAU GAUCHE */}
        <div className="tabs-panel">
          <div className="geo-shape shape-1"></div>
          <div className="geo-shape shape-2"></div>
          <div className="geo-shape shape-3"></div>

          <div className="tabs-content">
            <button
              className={`tab-btn ${activeTab === 'login' ? 'active' : ''}`}
              onClick={() => setActiveTab('login')}
            >
              LOGIN
            </button>
            <button
              className={`tab-btn ${activeTab === 'signup' ? 'active' : ''}`}
              onClick={() => setActiveTab('signup')}
            >
              S'inscrire
            </button>
          </div>
        </div>

        {/* PANNEAU DROITE */}
        <div className="form-panel">
          <div className="form-header">
            <div className="profile-avatar">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path fillRule="evenodd" d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z" clipRule="evenodd" />
              </svg>
            </div>
            <h1 className="form-title">{activeTab === 'login' ? 'LOGIN' : 'INSCRIPTION'}</h1>
          </div>

          {error && <p className="error-msg">{error}</p>}

          {/* FORMULAIRE LOGIN */}
          {activeTab === 'login' && (
            <form className="login-form" onSubmit={handleLogin}>
              <div className="input-group">
                <input
                  type="text"
                  placeholder=" "
                  required
                  value={loginData.username}
                  onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
                />
                <label>Nom d'utilisateur</label>
              </div>

              <div className="input-group">
                <input
                  type="password"
                  placeholder=" "
                  required
                  value={loginData.password}
                  onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                />
                <label>Mot de passe</label>
              </div>

              <div className="form-actions">
                <button type="submit" className="submit-btn" disabled={loading}>
                  {loading ? 'Connexion...' : 'Connectez-vous'}
                </button>
              </div>
            </form>
          )}

          {/* FORMULAIRE SIGNUP */}
          {activeTab === 'signup' && (
            <form className="login-form" onSubmit={handleSignup}>
              <div className="input-group">
                <input
                  type="text"
                  placeholder=" "
                  required
                  value={signupData.username}
                  onChange={(e) => setSignupData({ ...signupData, username: e.target.value })}
                />
                <label>Nom d'utilisateur</label>
              </div>

              <div className="input-group">
                <input
                  type="email"
                  placeholder=" "
                  required
                  value={signupData.email}
                  onChange={(e) => setSignupData({ ...signupData, email: e.target.value })}
                />
                <label>Email</label>
              </div>

              <div className="input-group">
                <input
                  type="password"
                  placeholder=" "
                  required
                  value={signupData.password}
                  onChange={(e) => setSignupData({ ...signupData, password: e.target.value })}
                />
                <label>Mot de passe</label>
              </div>

              <div className="form-actions">
                <button type="submit" className="submit-btn" disabled={loading}>
                  {loading ? 'Inscription...' : "S'inscrire"}
                </button>
              </div>
            </form>
          )}

          {/* SOCIAL LOGIN */}
          <div className="social-footer">
            <span className="social-label">
              {activeTab === 'login' ? 'Ou se connecter avec' : "Ou s'inscrire avec"}
            </span>
            <div className="social-buttons">
              <button className="social-btn" onClick={() => handleSocialLogin('google')}>
                <img src="https://authjs.dev/img/providers/google.svg" alt="Google" width="16" />
                Google
              </button>
              <button className="social-btn" onClick={() => handleSocialLogin('github')}>
                <img src="https://authjs.dev/img/providers/github.svg" alt="Github" width="16" />
                Github
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;