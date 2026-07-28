import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../style/Landing.css';

function VoltraLanding() {
  const navigate = useNavigate();

  return (
    <div className="voltra-page">
      <header className="voltra-header">
        <div className="voltra-logo">
          <div className="voltra-logo-box">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
              <path d="M4 4h16v4H4V4zm0 6h16v4H4v-4zm0 6h16v4H4v-4z" />
            </svg>
          </div>
          <span>DeployApp</span>
        </div>
        <div className="voltra-header-right">
          <span className="voltra-tagline">Plateforme d'infrastructure pour équipes techniques</span>
          <button className="voltra-btn-outline" onClick={() => navigate('/login')}>
            Se connecter
          </button>
        </div>
      </header>

      <main className="voltra-main">
        <span className="voltra-badge">Infrastructure d'entreprise</span>

        <h1 className="voltra-title">
          L'infrastructure de déploiement pensée pour la production.
        </h1>

        <p className="voltra-subtitle">
          DeployApp donne à vos équipes techniques une plateforme fiable,
          sécurisée et auditable pour déployer, sans dépendre d'une
          équipe DevOps dédiée.
        </p>

        <div className="voltra-cta-group">
          <button className="voltra-btn-primary" onClick={() => navigate('/login')}>
            Déployer maintenant
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
              <path d="M5 12h14M13 6l6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>

        <div className="voltra-stats">
          <div className="voltra-stat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <p className="voltra-stat-value">99,99 %</p>
            <p className="voltra-stat-label">Disponibilité garantie</p>
          </div>
          <div className="voltra-stat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
              <path d="M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <p className="voltra-stat-value">SOC 2</p>
            <p className="voltra-stat-label">Type II certifié</p>
          </div>
          <div className="voltra-stat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
              <rect x="2" y="3" width="20" height="6" rx="1" />
              <rect x="2" y="15" width="20" height="6" rx="1" />
            </svg>
            <p className="voltra-stat-value">12 régions</p>
            <p className="voltra-stat-label">Infrastructure mondiale</p>
          </div>
        </div>

        <p className="voltra-trusted-label">Utilisé par des équipes techniques exigeantes</p>
        <div className="voltra-trusted-logos">
          <span>Norvégia</span>
          <span>Aramis</span>
          <span>Cellarix</span>
          <span>Ondaline</span>
          <span>Perrault Group</span>
        </div>
      </main>

      <footer className="voltra-footer">
        © 2026 DeployApp. Tous droits réservés.
      </footer>
    </div>
  );
}

export default VoltraLanding;