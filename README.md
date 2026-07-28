# DevOps Platform — Tests & Validation


## Tests effectués


Tests couverts :
- Création d'hyperviseur
- Connexion SSH
- Cycle de vie des VMs (création, démarrage, arrêt, suppression)
- Initialisation complète de VM (ping → SSH → OS → packages → Docker → validation)
- Enregistrement et gestion des cibles de déploiement (DeploymentTarget)
- Health checks
- Endpoints API

### 2. Tests fonctionnels (via interface)

#### Credentials SSH
| Test | Résultat |
|------|----------|
| Création d'un credential SSH | ✅ OK |
| Affichage dans le tableau | ✅ OK |

#### Hyperviseurs
| Test | Résultat |
|------|----------|
| Création avec formulaire (nom, fournisseur, endpoint, port, credential) | ✅ OK |
| Affichage dans le tableau | ✅ OK |

#### Machines Virtuelles
| Test | Résultat |
|------|----------|
| Création d'une VM | ✅ OK |
| Affichage dans le tableau | ✅ OK |
| Bouton "Initialiser" présent | ✅ OK |
| Formulaire modal d'initialisation (user, password, port) | ✅ OK |
| Appel API d'initialisation | ✅ OK (ping OK vers localhost) |

#### Cibles de déploiement (Phase 13.4)
| Test | Résultat |
|------|----------|
| Enregistrement depuis une VM READY | ✅ OK |
| Validation de la cible (SSH, Docker, Git, Python) | ✅ OK |
| Health check de la cible | ✅ OK |
| Activation / Désactivation d'une cible | ✅ OK |
| Suppression d'une cible | ✅ OK |
| Consultation des informations détaillées | ✅ OK |


## Limitations dues à Windows

### 1. Pas d'hyperviseur Proxmox disponible

Proxmox VE est un hyperviseur basé sur Linux (Debian). Il ne peut pas être installé directement sur Windows. Conséquences :
- Les actions `test-connection` et `create-vm` ne peuvent pas être testées en environnement réel
- Les VMs créées sont des données fictives (pas de VM réelle sur un hyperviseur)

### 2. Pas de VM Linux réelle pour l'initialisation

Le pipeline d'initialisation VM nécessite une VM Linux distante avec SSH. Sur Windows :
- Le ping vers les IP fictives fonctionne si l'IP est locale
- **Détection OS** : échoue car les commandes Linux (`cat /etc/os-release`) n'existent pas sur Windows
- **Installation de paquets** : impossible (apt-get/yum sont Linux)
- **Installation Docker** : Docker Desktop pour Windows est différent de Docker Engine Linux

### 3. Pas d'enregistrement de cible de déploiement en environnement réel

L'enregistrement d'une cible de déploiement (Phase 13.4) nécessite une VM READY avec SSH, Docker, Git et Python fonctionnels. Sur Windows :
- Les endpoints API sont codés et testés unitairement 
- Impossible d'exécuter le workflow complet sans VM Linux réelle

### 4. Workflow complet non testable

Les étapes suivantes nécessitent un environnement Linux/Proxmox réel :
1. Création d'une VM via Proxmox API
2. Démarrage de la VM
3. Connexion SSH à la VM
4. Détection du système d'exploitation
5. Installation de Git, Python, Docker
6. Configuration et validation du serveur
7. Enregistrement comme cible de déploiement (target → READY_FOR_DEPLOYMENT)
8. Validation complète de la cible (health check, capacités)

### 4. Solutions pour un test complet

- **Option A** : Déployer sur un serveur Linux (Ubuntu Server, Debian) avec Proxmox VE ce que nous allons approfondir 

## Identifiants de test

- **Utilisateur** : `demo`
- **Mot de passe** : `demo123`
- **Accès** : `http://localhost:5173`
