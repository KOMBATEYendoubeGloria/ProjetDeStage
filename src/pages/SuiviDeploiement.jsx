import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import '../style/SuiviDeploiement.css';

// Étapes anticipées d'après le moteur d'orchestration d'Ackèklna (WorkflowStep)
const STEPS = [
  { key: 'git', label: 'Récupération Git' },
  { key: 'copy', label: 'Copie du projet' },
  { key: 'install', label: 'npm install' },
  { key: 'env', label: 'Configuration env' },
  { key: 'pm2', label: 'Démarrage PM2' },
  { key: 'nginx', label: 'Configuration Nginx' },
  { key: 'done', label: 'Déploiement terminé' },
];

function DeploymentTracker() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [currentStepIndex, setCurrentStepIndex] = useState(-1);

  useEffect(() => {
    // TODO: remplacer par un vrai suivi (polling ou WebSocket) une fois
    // que devops/orchestrator sera exposé en API par Ackèklna.
    // Pour l'instant, on simule visuellement la progression.
    let i = 0;
    const interval = setInterval(() => {
      setCurrentStepIndex(i);
      i++;
      if (i >= STEPS.length) clearInterval(interval);
    }, 1200);
    return () => clearInterval(interval);
  }, []);

  const getStatus = (index) => {
    if (index < currentStepIndex) return 'done';
    if (index === currentStepIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="tr-page">
      <div className="tr-card">
        <h1 className="tr-title">Suivi du Déploiement</h1>
        <p className="tr-subtitle">Déploiement #{id}</p>

        <div className="tr-steps">
          {STEPS.map((step, index) => (
            <div key={step.key} className={`tr-step tr-step-${getStatus(index)}`}>
              <div className="tr-step-box">{step.label}</div>
              {index < STEPS.length - 1 && <div className="tr-arrow">→</div>}
            </div>
          ))}
        </div>

        <button className="tr-back" onClick={() => navigate('/deploiements')}>
          ← Retour aux déploiements
        </button>
      </div>
    </div>
  );
}

export default DeploymentTracker;