import React, { useEffect, useState } from 'react';
import { getHealth } from '../api/devops';
import '../style/healthbanner.css';

function HealthBanner() {
  const [status, setStatus] = useState(null); // null = chargement, true = ok, false = down

  useEffect(() => {
    getHealth()
      .then((data) => setStatus(data.api === 'healthy' && data.database === 'healthy'))
      .catch(() => setStatus(false));
  }, []);

  if (status === null) return null; // rien pendant le chargement, pour ne pas clignoter
  if (status === true) return null; // rien si tout va bien, pour ne pas polluer l'UI

  return (
    <div className="health-banner">
      ⚠️ Le moteur DevOps est actuellement indisponible. Certaines fonctionnalités peuvent ne pas fonctionner.
    </div>
  );
}

export default HealthBanner;
