import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../style/AjoutServeur.css';

function AddServer() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    nom: '',
    ip_address: '',
    ssh_port: 22,
    username: '',
    private_key: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      // TODO: remplacer par un vrai appel API une fois la route d'Ackèklna disponible
      // ex: await createServer(form);
      console.log('Serveur à créer (en attente de l\'API DevOps) :', form);
      navigate('/dashboard');
    } catch (err) {
      setError('Erreur lors de l\'ajout du serveur.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="as-page">
      <div className="as-card">
        <h1 className="as-title">Ajouter une serveur</h1>

        {error && <p className="as-error">{error}</p>}

        <form onSubmit={handleSubmit} className="as-form">
          <div className="as-field">
            <label>Nom</label>
            <input
              type="text"
              name="nom"
              placeholder="Entrer le nom du serveur"
              value={form.nom}
              onChange={handleChange}
              required
            />
          </div>

          <div className="as-field">
            <label>Serveur distant (IP)</label>
            <input
              type="text"
              name="ip_address"
              placeholder="Adresse IP du serveur"
              value={form.ip_address}
              onChange={handleChange}
              required
            />
          </div>

          <div className="as-field">
            <label>SSH (port)</label>
            <input
              type="number"
              name="ssh_port"
              placeholder="Numéro de port SSH (par défaut 22)"
              value={form.ssh_port}
              onChange={handleChange}
            />
          </div>

          <div className="as-field">
            <label>Utilisateur</label>
            <input
              type="text"
              name="username"
              placeholder="Nom d'utilisateur SSH"
              value={form.username}
              onChange={handleChange}
              required
            />
          </div>

          <div className="as-field">
            <label>Clé privée SSH</label>
            <textarea
              name="private_key"
              placeholder="-----BEGIN OPENSSH PRIVATE KEY-----"
              value={form.private_key}
              onChange={handleChange}
              rows={4}
            />
          </div>

          <div className="as-actions">
            <button type="button" className="as-cancel" onClick={() => navigate(-1)}>
              Cancel
            </button>
            <button type="submit" className="as-submit" disabled={loading}>
              {loading ? 'Ajout...' : 'Ajouter'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddServer;