import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getProject, createProject, updateProject } from '../api/projects';
import '../style/FormulaireCreation.css';

const TECHNOLOGIES = [
  { value: 'NODEJS', label: 'Node.js' },
  { value: 'DJANGO', label: 'Django' },
  { value: 'REACT', label: 'React' },
];

function ProjectForm() {
  const navigate = useNavigate();
  const { id } = useParams(); // présent uniquement en mode édition
  const isEditMode = Boolean(id);

  const [form, setForm] = useState({
    nom: '',
    url_depot_git: '',
    technologie: 'NODEJS',
    branche: 'main',
    variables_env: {},
    variables_env_text: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isEditMode) {
      getProject(id)
        .then((res) => setForm(res.data))
        .catch(() => setError('Impossible de charger le projet.'));
    }
  }, [id, isEditMode]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const variables_env = {};
    (form.variables_env_text || '')
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .forEach((line) => {
        const [key, ...rest] = line.split('=');
        if (key) variables_env[key.trim()] = rest.join('=').trim();
      });

    const payload = { ...form, variables_env };
    delete payload.variables_env_text;

    try {
      if (isEditMode) {
        await updateProject(id, payload);
      } else {
        await createProject(payload);
      }
      navigate('/dashboard');
    } catch (err) {
      const msg = err.response?.data
        ? Object.values(err.response.data).flat().join(' ')
        : 'Erreur lors de l’enregistrement.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pf-page">
      <div className="pf-card">
        <h1 className="pf-title">
          {isEditMode ? 'Modifier le projet' : 'Création du projet'}
        </h1>

        {error && <p className="pf-error">{error}</p>}

        <form onSubmit={handleSubmit} className="pf-form">
          <div className="pf-field">
            <label>Nom du projet</label>
            <input
              type="text"
              name="nom"
              value={form.nom}
              onChange={handleChange}
              required
            />
          </div>

          <div className="pf-field">
            <label>URL du dépôt Git</label>
            <input
              type="text"
              name="url_depot_git"
              placeholder="https://github.com/utilisateur/projet.git"
              value={form.url_depot_git}
              onChange={handleChange}
              required
            />
          </div>

          <div className="pf-field">
            <label>Technologie</label>
            <select name="technologie" value={form.technologie} onChange={handleChange}>
              {TECHNOLOGIES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <div className="pf-field">
            <label>Branche</label>
            <input
              type="text"
              name="branche"
              value={form.branche}
              onChange={handleChange}
            />
          </div>

          <div className="pf-field">
            <label>Variables d'environnement (une par ligne : CLE=valeur)</label>
            <textarea
              name="variables_env_text"
              placeholder={'CLE=valeur\nAUTRE_CLE=valeur'}
              value={form.variables_env_text || ''}
              onChange={(e) => setForm({ ...form, variables_env_text: e.target.value })}
              rows={4}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '10px', marginTop: '12px' }}>
            <button type="submit" className="pf-submit" disabled={loading} style={{ width: '100%', maxWidth: '220px', alignSelf: 'center' }}>
              {loading ? 'Enregistrement...' : isEditMode ? 'Enregistrer' : 'Créer'}
            </button>
            <button type="button" onClick={() => navigate('/dashboard')} style={{ background: '#6b7280', color: '#fff', border: 'none', borderRadius: '8px', padding: '8px 14px', cursor: 'pointer', fontSize: '13px' }}>
              ← Retour
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ProjectForm;